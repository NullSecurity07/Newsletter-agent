from typing import Dict, Any, List, Tuple
from src.ollama.client import OllamaClient
from src.utils.logger import logger
from src.validation.quality_checker import ContentQualityChecker
from prompts.newsletter_prompts import NewsletterPrompts
import re
import os
from datetime import datetime
from collections import Counter

class NewsletterGenerator:
    """Generates newsletter content using codellama:7b with quality validation."""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
        self.quality_checker = ContentQualityChecker(ollama_client)
        self.prompts = NewsletterPrompts()
    
    def generate(self, topic: str, research_data: Dict[str, Any], console=None) -> Tuple[str, Dict[str, Any]]:
        """Generate newsletter content from research data with quality validation. Passes console for detailed output."""
        logger.info(f"Generating newsletter for topic: {topic}")
        
        try:
            # Generate outline first
            outline = self._generate_outline(topic, research_data, console=console)
            logger.info("Newsletter outline generated successfully")
            # Display outline in CLI
            if console:
                console.print("\n[bold blue]Generated Outline:[/bold blue]\n" + outline)
            # Parse outline into sections
            sections = self.parse_outline(outline)
            # Enforce minimum section count
            min_sections = 5
            if len(sections) < min_sections:
                if console:
                    console.print(f"[yellow]Outline has only {len(sections)} sections. Regenerating for more depth...[/yellow]")
                outline = self._generate_outline(topic, research_data, console=console)
                sections = self.parse_outline(outline)
            # Prepare sources for citation
            sources = research_data.get('sources', [])
            source_refs = [s.get('url', '') for s in sources if s.get('url')]
            # Generate content for each section, passing sources
            section_contents = []
            used_sources = set()
            transition_phrases = [
                "Next, ",
                "Additionally, ",
                "Furthermore, ",
                "In addition, ",
                "On the other hand, ",
                "As a result, "
            ]
            for idx, section in enumerate(sections):
                section_title = section['title']
                section_points = section['points']
                # Pass sources and encourage citation
                prompt, system_prompt = self.prompts.get_content_generation_prompt(
                    topic,
                    f"## {section_title}\n" + '\n'.join(f"- {p}" for p in section_points),
                    research_data
                )
                # Add explicit instruction for citations
                prompt += f"\n\nCite supporting sources inline as [n] (where n is the source number from the list below). If a claim cannot be matched to a source, mark it as [unverified].\n\nSources:\n"
                for i, url in enumerate(source_refs, 1):
                    prompt += f"[{i}] {url}\n"
                # Enforce minimum paragraph and citation count per section
                max_retries = 2
                for attempt in range(max_retries):
                    content = self.ollama.generate_with_retry(prompt, system_prompt, console=console)
                    paragraphs = [p for p in content.split('\n') if len(p.strip()) > 40]
                    citation_count = content.count('[')
                    if len(paragraphs) >= 3 and citation_count >= 1 and ('deep dive' in content.lower() or 'expert insight' in content.lower()):
                        break
                    if console:
                        console.print(f"[yellow]Section '{section_title}' too short or missing required elements. Re-prompting for more detail...[/yellow]")
                # Track which sources are cited
                for i, url in enumerate(source_refs, 1):
                    if f'[{i}]' in content:
                        used_sources.add(url)
                # Prepend a transition phrase to each section after the first
                if idx > 0 and content:
                    transition = transition_phrases[(idx - 1) % len(transition_phrases)]
                    # Only add transition if not already present
                    if not content.strip().lower().startswith(tuple(tp.strip().lower() for tp in transition_phrases)):
                        content = transition + content[0].lower() + content[1:] if content else content
                section_contents.append(f"## {section_title}\n{content.strip()}\n")
            content = '\n'.join(section_contents)
            logger.info("Section-by-section newsletter content generated with source verification")
            
            # Assess content quality
            quality_report = self.quality_checker.assess_content_quality(content, research_data)
            logger.info(f"Content quality assessment completed. Score: {quality_report['overall_score']:.1f}/100")
            
            # Optimize content if needed
            if quality_report['overall_score'] < 70:
                logger.info("Content quality below threshold, optimizing...")
                content = self._optimize_content(content, quality_report, console=console)
                # Re-assess quality after optimization
                quality_report = self.quality_checker.assess_content_quality(content, research_data)
                logger.info(f"Content optimized. New score: {quality_report['overall_score']:.1f}/100")
            
            # Humanize the content
            humanized_content = self._humanize_content(content, console=console)
            
            # Plagiarism/duplication check
            def has_significant_duplication(text):
                sentences = [s.strip() for s in re.split(r'[.!?]\s+', text) if len(s.strip()) > 20]
                counts = Counter(sentences)
                duplicates = [s for s, c in counts.items() if c > 1]
                return len(duplicates) > 2  # Warn if more than 2 repeated sentences
            if console and has_significant_duplication(humanized_content):
                console.print("[yellow]Warning: Detected repeated sentences or paragraphs. Review for possible duplication or plagiarism.[/yellow]")
            
            # Content flow optimization check
            def has_flow_issues(text):
                headings = re.findall(r'^## (.+)$', text, re.MULTILINE)
                expected_order = ["Opening Hook", "Introduction", "Section 1", "Section 2", "Section 3", "Conclusion", "Call-to-action"]
                # Check for logical order
                order_issues = False
                last_idx = -1
                for h in headings:
                    idxs = [i for i, e in enumerate(expected_order) if e.lower() in h.lower()]
                    if idxs:
                        idx = idxs[0]
                        if idx < last_idx:
                            order_issues = True
                        last_idx = idx
                # Check for transitions (look for 'Next,' 'Additionally,' 'Furthermore,' etc.)
                transitions = re.findall(r'\b(Next|Additionally|Furthermore|Meanwhile|In addition|On the other hand|As a result)\b', text)
                transition_issues = len(transitions) < max(1, len(headings) - 1)
                return order_issues, transition_issues
            order_issues, transition_issues = has_flow_issues(humanized_content)
            if console:
                if order_issues:
                    console.print("[yellow]Warning: Section headings may be out of logical order. Review for flow.[/yellow]")
                if transition_issues:
                    console.print("[yellow]Warning: Few transitions detected between sections. Consider adding more for better flow.[/yellow]")
            
            cleaned = self._clean_llm_output(humanized_content)
            polished = self.polish_newsletter(cleaned, console=console)
            # Final validation: ensure output is not a meta-assessment or quality report
            meta_indicators = [
                'Readability:', 'Factual Accuracy:', 'Overall Score:', 'Coherence:', 'Engagement:', 'Source Alignment:',
                'The Overall Score', 'This score suggests', 'can be improved', 'should be double-checked', 'areas where the writing can be improved'
            ]
            if any(ind in polished for ind in meta_indicators) or len(polished.split()) < 300:
                if console:
                    console.print("[red]Warning: Final output appears to be a meta-assessment or too short. Reverting to last known good content and re-polishing...[/red]")
                cleaned = self._clean_llm_output(humanized_content)
                polished = self.polish_newsletter(cleaned, console=console)
                # If still meta, raise error
                if any(ind in polished for ind in meta_indicators) or len(polished.split()) < 300:
                    if console:
                        console.print("[red]Error: Unable to generate a valid newsletter. Please review prompts and pipeline.[/red]")
                    return "Error: Newsletter generation failed due to repeated meta-content.", quality_report
            # Enforce presence of all premium sections
            required_sections = {
                "Editor's Note": "## Editor's Note / Expert Insights\n[Exclusive analysis or unique perspective from the editor.]\n",
                "Actionable Resource": "## Actionable Resource: Guide/Checklist/Template/Case Study\n[Step-by-step instructions, actionable checklist, or case study relevant to the topic.]\n",
                "Research Transparency": "## Research Transparency: How We Researched This\n[Summary of research process, sources, and originality.]\n",
                "Publishing Schedule": "Welcome to your [weekly/biweekly/monthly] issue of our premium newsletter!\n",
                "Personal Connection": "## Conclusion\n[Personal story, connection, or direct address from the editor.]\n",
                "Subscriber Perks": "## Subscriber Perks\n[Bonuses, early access, discounts, community, etc.]\n",
                "Proof of Impact": "## Proof of Impact\n[Testimonials, success stories, or real-world results from readers.]\n"
            }
            missing_sections = []
            for section, template in required_sections.items():
                if section == "Publishing Schedule":
                    if not ("weekly" in polished.lower() or "biweekly" in polished.lower() or "monthly" in polished.lower()):
                        polished = template + polished
                        missing_sections.append(section)
                else:
                    if template.split('\n')[0] not in polished:
                        polished += "\n" + template
                        missing_sections.append(section)
            if missing_sections and console:
                console.print(f"[yellow]The following premium sections were missing and have been added as templates: {', '.join(missing_sections)}[/yellow]")
            
            # Display source coverage summary in CLI
            if console and source_refs:
                cited = [url for i, url in enumerate(source_refs, 1) if url in used_sources]
                uncited = [url for url in source_refs if url not in used_sources]
                console.print(f"[bold green]Cited Sources:[/bold green] {len(cited)}")
                for url in cited:
                    console.print(f"  [green]{url}[/green]")
                if uncited:
                    console.print(f"[bold yellow]Uncited Sources:[/bold yellow] {len(uncited)}")
                    for url in uncited:
                        console.print(f"  [yellow]{url}[/yellow]")
            
            # Basic content length check
            word_count = len(polished.split())
            if word_count < 600:
                console.print(f"[yellow]Warning: Newsletter is only {word_count} words. Consider expanding for more depth.[/yellow]")
            
            # Content length optimization (upper bound)
            if console:
                if word_count > 2000:
                    console.print(f"[yellow]Warning: Newsletter is {word_count} words. Consider splitting into multiple issues or trimming for readability.[/yellow]")
            
            # Readability & engagement scoring
            def flesch_reading_ease(text):
                sentences = re.split(r'[.!?]', text)
                words = re.findall(r'\w+', text)
                syllables = sum(len(re.findall(r'[aeiouy]+', w, re.I)) for w in words)
                n_sent = max(1, len([s for s in sentences if s.strip()]))
                n_words = max(1, len(words))
                n_syll = max(1, syllables)
                return 206.835 - 1.015 * (n_words / n_sent) - 84.6 * (n_syll / n_words)
            def engagement_score(text):
                questions = len(re.findall(r'\?', text))
                you_we = len(re.findall(r'\b(you|we)\b', text, re.I))
                return questions + you_we
            if console:
                fre = flesch_reading_ease(humanized_content)
                eng = engagement_score(humanized_content)
                console.print(f"[cyan]Readability (Flesch Reading Ease): {fre:.1f}[/cyan]")
                console.print(f"[cyan]Engagement Score (questions + 'you/we'): {eng}[/cyan]")
            
            return polished, quality_report
            
        except Exception as e:
            logger.error(f"Newsletter generation failed: {e}")
            return f"Error generating newsletter: {e}", {'overall_score': 0, 'issues': [str(e)]}
    
    def _generate_outline(self, topic: str, research_data: Dict[str, Any], console=None) -> str:
        """Generate newsletter outline using enhanced prompts."""
        prompt, system_prompt = self.prompts.get_outline_generation_prompt(topic, research_data)
        
        outline = self.ollama.generate_with_retry(prompt, system_prompt, console=console)
        return outline or "1. Introduction\n2. Main Content\n3. Conclusion"
    
    def _generate_content(self, topic: str, research_data: Dict[str, Any], outline: str, console=None) -> str:
        """Generate newsletter content based on outline using enhanced prompts."""
        prompt, system_prompt = self.prompts.get_content_generation_prompt(topic, outline, research_data)
        
        content = self.ollama.generate_with_retry(prompt, system_prompt, console=console)
        return content or f"Unable to generate content for {topic}"
    
    def _optimize_content(self, content: str, quality_report: Dict[str, Any], console=None) -> str:
        """Optimize content based on quality assessment."""
        prompt, system_prompt = self.prompts.get_content_optimization_prompt(content, quality_report)
        
        optimized_content = self.ollama.generate_with_retry(prompt, system_prompt, console=console)
        return optimized_content or content
    
    def _humanize_content(self, content: str, console=None) -> str:
        """Add human touches to make content more engaging and relatable."""
        system_prompt = (
            "You are an expert newsletter editor and storyteller. Make the content more human, engaging, and newsletter-friendly by:"
            "\n- Adding conversational transitions and rhetorical questions"
            "\n- Including personal touches, anecdotes, or analogies when appropriate"
            "\n- Addressing the reader directly (e.g., 'you', 'we', 'let's')"
            "\n- Using varied sentence structure and natural language"
            "\n- Making the content feel like a conversation, not a lecture"
            "\n- Maintaining professional quality, factual accuracy, and clarity"
            "\n- Keeping paragraphs short and easy to read"
            "\n- Ensuring the tone matches the intended audience (e.g., professionals, general public, students)"
        )
        prompt = f"""
        Original Content:
        {content}
        
        Please humanize this content to make it more engaging, relatable, and enjoyable for newsletter readers. 
        Add conversational transitions, rhetorical questions, and personal touches. Use stories or analogies if relevant. Address the reader directly. Keep the tone professional but friendly.
        """
        humanized = self.ollama.generate_with_retry(prompt, system_prompt, console=console)
        # Optionally display before/after in CLI
        if console:
            console.print("\n[bold magenta]Before Humanization:[/bold magenta]\n" + content[:800] + ("..." if len(content) > 800 else ""))
            console.print("\n[bold green]After Humanization:[/bold green]\n" + (humanized[:800] if humanized else "") + ("..." if humanized and len(humanized) > 800 else ""))
        return humanized or content
    
    def generate_with_validation(self, topic: str, research_data: Dict[str, Any], console=None) -> Tuple[str, bool, Dict[str, Any]]:
        """Generate newsletter with validation and return pass/fail status."""
        content, quality_report = self.generate(topic, research_data, console=console)
        
        # Validate content quality
        passes_validation, validation_report = self.quality_checker.validate_content(content, research_data)
        
        return content, passes_validation, validation_report 
    
    def _clean_llm_output(self, text: str) -> str:
        """Remove prompt echoes, meta-instructions, and trailing whitespace from LLM output. Also remove meta-assessment lines."""
        lines = text.splitlines()
        cleaned = []
        skip_block = False
        topic_words = set(self.topic.lower().split()) if hasattr(self, 'topic') else set()
        meta_indicators = [
            'Readability:', 'Factual Accuracy:', 'Overall Score:', 'Coherence:', 'Engagement:', 'Source Alignment:',
            'The Overall Score', 'This score suggests', 'can be improved', 'should be double-checked', 'areas where the writing can be improved'
        ]
        for line in lines:
            l = line.strip()
            if not l:
                cleaned.append("")
                continue
            # Remove lines that are instructions or meta
            if re.search(r'(please|add engaging elements|keep the same information|make it more conversational|humanize this content|as an expert editor|your task is to|system prompt:|original content:|as a business owner|as a professional|this hook|based on our research|in conclusion|call-to-action:|opening hook:|introduction:|section [0-9]+:|conclusion:|hey there!|newsletter outline:|main content:)', l, re.IGNORECASE):
                continue
            # Remove lines that are just 'Research Data:' or similar
            if re.match(r'^(Research Data|Key Points|Sources|Recent Developments)[:：]', l, re.IGNORECASE):
                continue
            # Remove lines that are just a heading or label
            if re.match(r'^(section|conclusion|call-to-action|opening hook|introduction|main content)[\s\d:.-]*$', l, re.IGNORECASE):
                continue
            # Remove repeated greetings
            if l.lower() in {"hey there!", "hello!", "hi there!"}:
                continue
            # Aggressively skip meta/suggestion blocks
            if re.match(r'^(the original content has|based on your quality assessment|here are the changes i made|humanized content:|overall, optimizing the content|any suggestions|anything you\'d like to add|do you have any suggestions|we want to make sure|we\'re doing our best|we\'re verifying facts|we\'re incorporating|we want to maintain)', l, re.IGNORECASE):
                skip_block = True
                continue
            if skip_block:
                # End block skipping on empty line
                if not l:
                    skip_block = False
                continue
            # Remove numbered suggestion lists (not narrative)
            if re.match(r'^[0-9]+\.( |$)', l) and not any(word in l.lower() for word in topic_words):
                continue
            # Remove meta-assessment lines
            if any(ind in l for ind in meta_indicators):
                continue
            cleaned.append(line)
        # Remove trailing empty lines
        while cleaned and not cleaned[-1].strip():
            cleaned.pop()
        return "\n".join(cleaned)
    
    def polish_newsletter(self, draft: str, console=None) -> str:
        """Send the cleaned newsletter draft through a final LLM polishing prompt for seamless, publication-ready output."""
        system_prompt = (
            "You are an expert newsletter editor.\n"
            "Your job is to polish the following newsletter draft so it is ready for publication.\n"
            "- Remove any meta-comments, instructions, or AI artifacts.\n"
            "- Ensure the flow is seamless and engaging.\n"
            "- Do not add any new sections or explanations.\n"
            "- Only output the final, polished newsletter content."
        )
        prompt = f"Here is the draft newsletter. Polish it for publication:\n\n{draft.strip()}"
        polished = self.ollama.generate_with_retry(prompt, system_prompt, console=console)
        return polished.strip() if polished else draft.strip()

    def parse_outline(self, outline: str) -> List[dict]:
        """Parse the outline into a list of sections with titles and key points."""
        sections = []
        current_section = None
        for line in outline.splitlines():
            line = line.strip()
            if line.startswith('## '):
                if current_section:
                    sections.append(current_section)
                current_section = {'title': line[3:], 'points': []}
            elif line.startswith('- '):
                if current_section:
                    current_section['points'].append(line[2:])
            elif line and not line.startswith('#'):
                if current_section:
                    current_section['points'].append(line)
        if current_section:
            sections.append(current_section)
        return sections 

    def save_newsletter(self, content: str, topic: str, format: str, output_dir: str) -> str:
        """Save newsletter to file."""
        # Clean topic for filename
        safe_topic = re.sub(r'[^\w\s-]', '', topic).strip()
        safe_topic = re.sub(r'[-\s]+', '-', safe_topic)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = 'md' if format == 'markdown' else format
        filename = f"{safe_topic}_{timestamp}.{ext}"
        filepath = os.path.join(output_dir, filename)
        # If markdown, ensure headings use #
        if format == 'markdown':
            content = re.sub(r'^## ', '# ', content, flags=re.MULTILINE)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath 

# Placeholder for parallel processing (future batch topic generation)
def generate_newsletters_in_parallel(topics, research_data_list, console=None):
    """Future: Generate multiple newsletters in parallel (batch mode)."""
    from concurrent.futures import ThreadPoolExecutor
    # TODO: Implement batch processing for multiple topics
    # Example usage:
    # with ThreadPoolExecutor() as executor:
    #     results = list(executor.map(lambda args: NewsletterGenerator(...).generate(*args), zip(topics, research_data_list)))
    pass 

# Placeholder for engagement prediction (future ML integration)
def predict_engagement(newsletter_text):
    """Future: Predict engagement score using ML model or API."""
    # TODO: Integrate ML model or API for engagement prediction
    # Example: return engagement_model.predict(newsletter_text)
    return None 

# Placeholder for advanced plagiarism detection (future API integration)
def check_plagiarism_external(newsletter_text):
    """Future: Check for plagiarism using a third-party API/service."""
    # TODO: Integrate external plagiarism detection API
    # Example: return plagiarism_api.check(newsletter_text)
    return None 