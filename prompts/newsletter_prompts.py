"""
Enhanced prompt templates for newsletter generation using CodeGemma:7b.
Optimized for content quality, factual accuracy, and engagement.
"""

class NewsletterPrompts:
    """Enhanced prompt templates for newsletter generation."""
    
    @staticmethod
    def get_research_analysis_prompt(topic: str, research_data: dict) -> tuple[str, str]:
        """Generate prompt for analyzing research data and creating insights."""
        system_prompt = """You are an expert research analyst specializing in creating comprehensive, accurate, and engaging newsletter content. 
        Your task is to analyze research data and create insightful, well-structured content that is:
        - Factually accurate and verified against sources
        - Engaging and accessible to a general audience
        - Well-organized with clear logical flow
        - Rich in context and meaningful insights
        - Professional yet conversational in tone
        
        Always prioritize accuracy over creativity. When in doubt, stick to verified facts from reliable sources."""
        
        prompt = f"""
        Topic: {topic}
        
        Research Data Summary:
        - Key Points: {chr(10).join(f"• {point}" for point in research_data.get('key_points', [])[:5])}
        - Sources: {len(research_data.get('sources', []))} verified sources
        - Recent Developments: {research_data.get('recent_developments', 'No recent developments found')}
        
        Create a comprehensive newsletter article that:
        1. Opens with a compelling hook that captures reader interest
        2. Provides clear context and background information
        3. Presents the latest developments and key insights
        4. Explains the significance and implications
        5. Includes relevant examples or case studies
        6. Concludes with forward-looking insights or next steps
        
        Structure the content with:
        - Clear headings and subheadings
        - Short, readable paragraphs (2-3 sentences max)
        - Smooth transitions between sections
        - Engaging language that maintains reader interest
        - Factual accuracy throughout
        
        Target length: 800-1200 words
        Tone: Professional, informative, engaging
        """
        
        return prompt, system_prompt
    
    @staticmethod
    def get_outline_generation_prompt(topic: str, research_data: dict) -> tuple[str, str]:
        """Generate prompt for creating newsletter outline."""
        company = research_data.get('company', '[Company]')
        company_info = research_data.get('company_info', '')
        purpose = research_data.get('purpose', '[Purpose]')
        system_prompt = """You are an expert newsletter editor and content strategist. \
Create compelling, well-structured outlines that maximize reader engagement and information retention.\
Focus on logical flow, clear progression of ideas, and strategic placement of hooks and key information.\
Require depth, actionable insights, expert commentary, and all premium newsletter features.\
Personalize the outline for the company, its brand, and the stated purpose."""
        
        prompt = f"""
        Topic: {topic}
        Company: {company}
        Company Info: {company_info}
        Purpose/Goal: {purpose}
        
        Research Context:
        - Key Points: {chr(10).join(f"• {point}" for point in research_data.get('key_points', [])[:5])}
        - Source Count: {len(research_data.get('sources', []))}
        
        Create a detailed newsletter outline with these required sections, tailored to the company's brand, mission, and the stated purpose:
        1. Compelling headline that captures attention and aligns with the company's brand
        2. Opening hook that creates curiosity and connects to the company's mission or product
        3. Personal Editor's Note or Expert Insights (exclusive analysis, unique perspective, or company leadership message)
        4. Clear introduction that sets context, states the publishing schedule, and references the company and purpose
        5. 5-7 main sections with descriptive, expert-level headings, including:
           - At least one actionable resource (step-by-step guide, checklist, template, or case study) directly supporting the stated purpose
           - A research transparency sidebar/section ("How We Researched This")
        6. Conclusion with personal connection, story, or direct address from the company/editor
        7. Subscriber Perks (bonuses, early access, discounts, community, etc.)
        8. Proof of Impact (testimonials, success stories, or real-world results)
        9. Call-to-action or forward-looking statement, tailored to the purpose (e.g., sign up, buy, attend, etc.)
        
        Format the outline as:
        # [HEADLINE]
        
        ## Opening Hook
        [Brief description of hook approach]
        
        ## Editor's Note / Expert Insights
        [Exclusive analysis, company leadership message, or unique perspective]
        
        ## Introduction
        [Context, background, publishing schedule, company, and purpose]
        
        ## [Section 1 Title]
        - [Key point 1]
        - [Key point 2]
        - [Key point 3]
        - [Expert insight or deep dive]
        
        ## [Actionable Resource: Guide/Checklist/Template/Case Study]
        - [Step-by-step instructions or actionable content supporting the purpose]
        
        ## [Section 2 Title]
        - [Key point 1]
        - [Key point 2]
        - [Key point 3]
        - [Expert insight or deep dive]
        
        ## Research Transparency: How We Researched This
        [Summary of research process, sources, and originality]
        
        ## [Section 3 Title]
        - [Key point 1]
        - [Key point 2]
        - [Key point 3]
        - [Expert insight or deep dive]
        
        ## Conclusion
        [Personal story, connection, or direct address from the company/editor]
        
        ## Subscriber Perks
        [Bonuses, early access, discounts, community, etc.]
        
        ## Proof of Impact
        [Testimonials, success stories, or real-world results]
        
        ## Call-to-Action
        [Engaging, actionable closing statement tailored to the purpose]
        
        Ensure the outline flows logically, builds reader engagement, and provides depth, actionability, and all premium features throughout. Personalize every section for the company and the stated goal.
        """
        
        return prompt, system_prompt
    
    @staticmethod
    def get_content_generation_prompt(topic: str, outline: str, research_data: dict) -> tuple[str, str]:
        """Generate prompt for creating full newsletter content from outline."""
        company = research_data.get('company', '[Company]')
        company_info = research_data.get('company_info', '')
        purpose = research_data.get('purpose', '[Purpose]')
        system_prompt = """You are a professional newsletter writer with expertise in creating engaging, accurate, and well-structured content.\
Your writing should be:\
- Clear and accessible to a general audience\
- Factually accurate and well-researched\
- Engaging with varied sentence structure and vocabulary\
- Professional yet conversational in tone\
- Well-organized with smooth transitions\
- Rich in actionable insights, expert commentary, and deep dives\
- Includes all premium newsletter features (see below)\
- Personalized for the company's brand, mission, and the stated purpose\
\
Always prioritize clarity and accuracy. Use active voice, avoid jargon, and make complex topics accessible.\
\
Output only the final newsletter content. Do not include any explanations, meta-comments, or instructions. Do not repeat the prompt or system prompt. Only output what the reader should see in the newsletter.\
\
Write the newsletter as a seamless, engaging narrative. Use headings for each section, but ensure each section is expanded into 3–5 detailed paragraphs, including examples, analogies, and at least one cited fact or statistic per section. Each main section must include a 'deep dive' or 'expert insight' sub-section.\
\
You must use all provided research data (key points, summaries, sources, company info, and purpose) as the basis for the newsletter. Do not invent facts or stray from the research. Do not include meta-comments, suggestions, or generic greetings. The newsletter must be detailed, topic-specific, and cover all key points and research findings. The topic, company, and purpose must be mentioned throughout. The output must be at least 1200 words. Only output the final, reader-facing newsletter content, ready for publication.\
\
Include inline citations for every claim, and a professional references section at the end listing all sources used.\
\
**Required Premium Features:**\
- Exclusive, expert-driven content (Editor's Note/Expert Insights, company leadership message)\
- Actionable resource (guide, checklist, template, or case study) supporting the purpose\
- Research transparency section ("How We Researched This")\
- Publishing schedule mention\
- Personal connection and brand voice\
- Professional formatting and design\
- Subscriber perks section\
- Proof of impact/testimonials\
- All content tailored to the company and the stated goal\
\
If any required section is missing, add it.\
"""
        
        prompt = f"""
        Topic: {topic}
        Company: {company}
        Company Info: {company_info}
        Purpose/Goal: {purpose}
        
        Newsletter Outline:
        {outline}
        
        Research Data:
        - Key Points: {chr(10).join(f"• {point}" for point in research_data.get('key_points', [])[:10])}
        - Sources: {len(research_data.get('sources', []))} verified sources
        - Recent Developments: {research_data.get('recent_developments', 'No recent developments found')}
        
        Write the complete newsletter content following the outline structure. Ensure:
        
        1. **Opening Hook**: Start with a compelling hook that immediately captures reader interest and connects to the company's mission or product
        2. **Editor's Note / Expert Insights**: Share exclusive analysis, company leadership message, or unique perspective
        3. **Introduction**: Provide clear context, background, state the publishing schedule, and reference the company and purpose
        4. **Main Content**: For each section, write 3–5 detailed paragraphs, including examples, analogies, actionable advice, and at least one cited fact/statistic. Include a 'deep dive' or 'expert insight' in each main section. Personalize for the company and purpose.
        5. **Actionable Resource**: Include a step-by-step guide, checklist, template, or case study directly supporting the purpose
        6. **Research Transparency**: Add a sidebar/section explaining how the research was conducted and sources used
        7. **Transitions**: Use smooth transitions between sections and paragraphs
        8. **Engagement**: Include questions, stories, and interactive elements
        9. **Accuracy**: Stick to verified facts from research sources, with inline citations
        10. **Conclusion**: Provide meaningful insights, personal story, and forward-looking perspective from the company/editor
        11. **Subscriber Perks**: Offer bonuses, early access, discounts, or community invites
        12. **Proof of Impact**: Share testimonials, success stories, or real-world results
        13. **Call-to-Action**: End with a strong, actionable closing statement tailored to the purpose
        14. **References**: List all sources cited in a professional references section
        
        Writing Guidelines:
        - Use short, readable paragraphs (2-3 sentences max)
        - Vary sentence structure for rhythm and flow
        - Include specific examples and details when available
        - Use active voice and strong verbs
        - Avoid jargon and technical terms without explanation
        - Maintain consistent tone throughout
        - Target 1200-2000 words total
        
        Format the content with clear headings and proper spacing for readability. Personalize every section for the company and the stated goal.
        """
        
        return prompt, system_prompt
    
    @staticmethod
    def get_hook_generation_prompt(topic: str, content: str) -> tuple[str, str]:
        """Generate prompt for creating psychological hooks."""
        system_prompt = """You are an expert in psychological triggers and reader engagement. 
        Create compelling hooks that use proven psychological principles to capture and maintain reader attention.
        Focus on curiosity gaps, emotional triggers, and cognitive biases that drive engagement."""
        
        prompt = f"""
        Topic: {topic}
        
        Content Preview:
        {content[:500]}...
        
        Create 3 different types of psychological hooks for this newsletter:
        
        1. **Curiosity Gap Hook**: Create intrigue by revealing partial information
        2. **Emotional Trigger Hook**: Appeal to emotions (fear, excitement, hope, etc.)
        3. **Cognitive Bias Hook**: Use patterns like scarcity, authority, or social proof
        
        For each hook type, provide:
        - The hook text (1-2 sentences max)
        - The psychological principle being used
        - Why it will be effective for this topic
        
        Format as:
        
        ## Curiosity Gap Hook
        [Hook text]
        **Principle**: [Psychological principle]
        **Effectiveness**: [Why it works for this topic]
        
        ## Emotional Trigger Hook
        [Hook text]
        **Principle**: [Psychological principle]
        **Effectiveness**: [Why it works for this topic]
        
        ## Cognitive Bias Hook
        [Hook text]
        **Principle**: [Psychological principle]
        **Effectiveness**: [Why it works for this topic]
        
        Choose the most effective hook based on the content and topic.
        """
        
        return prompt, system_prompt
    
    @staticmethod
    def get_content_optimization_prompt(content: str, quality_report: dict) -> tuple[str, str]:
        """Generate prompt for optimizing content based on quality assessment."""
        system_prompt = """You are an expert content editor and optimization specialist.
        Improve content based on quality metrics while maintaining accuracy and engagement.
        Focus on addressing specific issues identified in the quality report."""
        
        prompt = f"""
        Original Content:
        {content}
        
        Quality Assessment:
        - Overall Score: {quality_report.get('overall_score', 0)}/100
        - Readability: {quality_report.get('readability_score', 0)}/100
        - Factual Accuracy: {quality_report.get('factual_accuracy', 0)}/100
        - Coherence: {quality_report.get('coherence_score', 0)}/100
        - Engagement: {quality_report.get('engagement_score', 0)}/100
        - Source Alignment: {quality_report.get('source_alignment', 0)}/100
        
        Improvement Suggestions:
        {chr(10).join(f"• {suggestion}" for suggestion in quality_report.get('suggestions', []))}
        
        Optimize the content to address the identified issues while:
        1. Maintaining factual accuracy and source alignment
        2. Improving readability and coherence
        3. Enhancing engagement and flow
        4. Preserving the original message and insights
        5. Keeping the same length and structure
        
        Provide the optimized version with clear explanations of key changes made.
        """
        
        return prompt, system_prompt
    
    @staticmethod
    def get_fact_verification_prompt(content: str, research_data: dict) -> tuple[str, str]:
        """Generate prompt for fact-checking content against research data."""
        system_prompt = """You are a professional fact-checker and verification specialist.
        Verify the accuracy of content against provided research data and identify any factual errors or unsupported claims.
        Be thorough but fair in your assessment."""
        
        prompt = f"""
        Content to Verify:
        {content}
        
        Research Data for Verification:
        - Key Points: {chr(10).join(f"• {point}" for point in research_data.get('key_points', []))}
        - Sources: {len(research_data.get('sources', []))} sources
        - Source Details: {chr(10).join(f"• {source.get('title', 'No title')} - {source.get('url', 'No URL')}" for source in research_data.get('sources', [])[:5])}
        
        Fact-check the content and provide:
        
        1. **Verified Facts**: List facts that are supported by research
        2. **Unsupported Claims**: Identify claims that lack research backing
        3. **Potential Errors**: Note any factual inaccuracies
        4. **Missing Context**: Identify areas that need more context
        5. **Overall Accuracy Score**: Rate from 0-100
        
        For each issue found, provide:
        - Specific location in content
        - Nature of the issue
        - Suggested correction or improvement
        
        Be precise and constructive in your feedback.
        """
        
        return prompt, system_prompt 