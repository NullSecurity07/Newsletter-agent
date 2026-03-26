from typing import Dict, Any, List
from src.ollama.client import OllamaClient
from src.utils.logger import logger

class HookEffectivenessScorer:
    """Scores psychological hooks for clarity, emotional impact, and relevance using a hybrid approach."""
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
        # Simple emotional word list for rule-based scoring
        self.emotional_words = [
            'amazing', 'incredible', 'shocking', 'exciting', 'fear', 'hope', 'urgent', 'secret', 'exclusive',
            'breakthrough', 'revolutionary', 'unbelievable', 'fascinating', 'critical', 'essential', 'limited',
            'scarce', 'rare', 'unique', 'brand new', 'never seen', 'imagine', 'picture this', 'story', 'case study'
        ]

    def score_hook(self, hook: str, topic: str, research_data: dict) -> dict:
        """Return a dict with clarity, emotional impact, relevance, and overall score (0-100)."""
        # Rule-based scoring
        clarity = self._score_clarity(hook)
        emotional_impact = self._score_emotional_impact(hook)
        relevance = self._score_relevance(hook, topic, research_data)
        # LLM-based adjustment
        llm_score = self._llm_score(hook, topic, research_data)
        # Weighted average (rule-based 70%, LLM 30%)
        overall = round((clarity + emotional_impact + relevance) / 3 * 0.7 + llm_score * 0.3, 1)
        return {
            'clarity': clarity,
            'emotional_impact': emotional_impact,
            'relevance': relevance,
            'llm_score': llm_score,
            'overall_score': overall
        }

    def _score_clarity(self, hook: str) -> float:
        # Simple: penalize long sentences, complex words
        words = hook.split()
        avg_word_len = sum(len(w) for w in words) / len(words) if words else 0
        score = 100 - max(0, (avg_word_len - 5) * 10) - max(0, (len(words) - 25) * 2)
        return max(0, min(100, score))

    def _score_emotional_impact(self, hook: str) -> float:
        # Count emotional words and exclamations
        count = sum(1 for w in self.emotional_words if w in hook.lower())
        exclam = hook.count('!')
        score = min(100, 60 + count * 10 + exclam * 5)
        return max(0, score)

    def _score_relevance(self, hook: str, topic: str, research_data: dict) -> float:
        # Check for topic keywords in hook
        topic_words = set(topic.lower().split())
        key_points = ' '.join(research_data.get('key_points', [])).lower().split()
        key_words = set(key_points)
        hook_words = set(hook.lower().split())
        overlap = len(hook_words & (topic_words | key_words))
        score = min(100, 60 + overlap * 5)
        return max(0, score)

    def _llm_score(self, hook: str, topic: str, research_data: dict) -> float:
        # Use LLM to rate overall effectiveness (0-100)
        system_prompt = """You are a copywriting expert. Rate the following hook for overall effectiveness (clarity, emotional impact, relevance) on a scale from 0-100. Only return the number."""
        prompt = f"""
        Hook: {hook}
        Topic: {topic}
        Key Points: {', '.join(research_data.get('key_points', [])[:3])}
        """
        response = self.ollama.generate_with_retry(prompt, system_prompt)
        try:
            score = int(''.join(filter(str.isdigit, response.strip())))
            return min(100, max(0, score))
        except Exception:
            return 60.0

# Integrate into HookGenerator
default_scorer = None

class HookGenerator:
    """Generates psychological hooks using codellama:7b."""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
        global default_scorer
        if default_scorer is None:
            default_scorer = HookEffectivenessScorer(ollama_client)
        self.scorer = default_scorer
    
    def _analyze_topic_context(self, topic: str, research_data: Dict[str, Any]) -> dict:
        """Analyze topic and research data to infer audience and tone."""
        # Simple heuristics for demo; can be expanded
        topic_lower = topic.lower()
        summary = research_data.get('summary', '').lower()
        key_points = ' '.join(research_data.get('key_points', [])).lower()
        text = f"{topic_lower} {summary} {key_points}"
        # Audience
        if any(w in text for w in ['student', 'education', 'university', 'school']):
            audience = 'students'
        elif any(w in text for w in ['doctor', 'medical', 'healthcare', 'patient', 'hospital']):
            audience = 'healthcare professionals'
        elif any(w in text for w in ['developer', 'engineer', 'software', 'programming', 'ai', 'machine learning']):
            audience = 'tech professionals'
        elif any(w in text for w in ['business', 'finance', 'market', 'startup', 'entrepreneur']):
            audience = 'business professionals'
        else:
            audience = 'general public'
        # Tone
        if any(w in text for w in ['urgent', 'critical', 'breaking', 'alert']):
            tone = 'urgent'
        elif any(w in text for w in ['fun', 'exciting', 'amazing', 'incredible']):
            tone = 'enthusiastic'
        elif any(w in text for w in ['controversial', 'debate', 'argument']):
            tone = 'neutral'
        elif any(w in text for w in ['research', 'study', 'report', 'analysis']):
            tone = 'formal'
        else:
            tone = 'informative'
        return {'audience': audience, 'tone': tone}

    def generate_hooks(self, topic: str, research_data: Dict[str, Any], preferred_styles: set = None, console=None) -> List[dict]:
        """Generate multiple psychological hooks for the topic, using context-based trigger selection and personalization. Returns list of dicts with hook and scores."""
        logger.info(f"Generating psychological hooks for topic: {topic}")
        try:
            hooks = []
            context = self._analyze_topic_context(topic, research_data)
            selected_hook_types = self._select_triggers_by_context(topic, research_data)
            # Map style names to generation functions
            style_func_map = {
                'curiosity': self._generate_curiosity_hook,
                'urgency': self._generate_urgency_hook,
                'emotional': self._generate_emotional_hook,
                'benefit': self._generate_benefit_hook,
                'question': self._generate_question_hook,
                'fomo': self._generate_fomo_hook,
                'authority': self._generate_authority_hook,
                'social_proof': self._generate_social_proof_hook,
                'scarcity': self._generate_scarcity_hook,
                'novelty': self._generate_novelty_hook,
                'storytelling': self._generate_storytelling_hook
            }
            # Support for multi-trigger generation and combination
            for style_name, hook_func in style_func_map.items():
                if hook_func in selected_hook_types:
                    if preferred_styles and style_name not in preferred_styles:
                        continue
                    hook = hook_func(topic, research_data, context, console=console)
                    if hook and not any(h['hook'] == hook for h in hooks):
                        score = self.scorer.score_hook(hook, topic, research_data)
                        hooks.append({'hook': hook, 'score': score, 'context': context, 'style': style_name})
            if not hooks:
                fallback = self._generate_fallback_hook(topic)
                score = self.scorer.score_hook(fallback, topic, research_data)
                hooks.append({'hook': fallback, 'score': score, 'context': context, 'style': 'fallback'})
            logger.info(f"Generated {len(hooks)} psychological hooks (multi-trigger support)")
            return hooks[:5]  # Return up to 5 hooks
        except Exception as e:
            logger.error(f"Hook generation failed: {e}")
            return [{'hook': f"Discover the latest insights on {topic}", 'score': {{}}, 'context': {{}}, 'style': 'fallback'}]
    
    def _select_triggers_by_context(self, topic: str, research_data: Dict[str, Any]):
        """Select the most relevant triggers based on topic keywords and research data."""
        # Define mapping of keywords to triggers
        trigger_map = [
            (['new', 'breakthrough', 'innovation', 'first', 'never seen', 'revolutionary'], self._generate_novelty_hook),
            (['urgent', 'now', 'today', 'critical', 'immediate', 'act fast'], self._generate_urgency_hook),
            (['limited', 'scarce', 'few left', 'exclusive', 'while supplies last'], self._generate_scarcity_hook),
            (['everyone', 'millions', 'trusted by', 'popular', 'as seen in'], self._generate_social_proof_hook),
            (['expert', 'authority', 'researchers', 'scientist', 'trusted source'], self._generate_authority_hook),
            (['story', 'imagine', 'case study', 'anecdote', 'scenario'], self._generate_storytelling_hook),
            (['fear', 'hope', 'excite', 'concern', 'emotion'], self._generate_emotional_hook),
            (['discover', 'learn', 'unlock', 'master', 'achieve'], self._generate_benefit_hook),
            (['question', 'why', 'how', 'what if', 'challenge'], self._generate_question_hook),
            (['secret', 'revealed', 'shocking', 'you won\'t believe'], self._generate_curiosity_hook),
            (['miss out', 'only a few', 'limited time', 'fomo'], self._generate_fomo_hook),
        ]
        # Gather all text to search
        text = f"{topic} {research_data.get('summary', '')} {' '.join(research_data.get('key_points', []))}".lower()
        selected = set()
        for keywords, func in trigger_map:
            if any(word in text for word in keywords):
                selected.add(func)
        # Always include curiosity and benefit as defaults if nothing else matches
        if not selected:
            selected.update([self._generate_curiosity_hook, self._generate_benefit_hook])
        return list(selected)
    
    # Modular prompt templates for each trigger type
    HOOK_PROMPT_TEMPLATES = {
        'curiosity': {
            'system': """You are an expert copywriter specializing in psychological hooks. Create a curiosity gap hook that:
        - Teases valuable information without revealing everything
        - Creates a strong desire to learn more
        - Uses phrases like 'you won't believe', 'shocking', 'revealed', 'secret'
        - Is 1-2 sentences maximum
        - Makes the reader want to continue reading
- Tailored for an audience of {audience} in a {tone} tone""",
            'instructions': "Create a curiosity gap hook that teases the most interesting or surprising finding about this topic. Make it compelling and mysterious without being clickbait. Audience: {audience}. Tone: {tone}."
        },
        'urgency': {
            'system': """You are an expert copywriter. Write an urgency-based hook that:
- Conveys time sensitivity or immediate action
- Uses urgent language (e.g., 'now', 'today', 'don't miss out')
- Is concise and compelling
- Tailored for an audience of {audience} in a {tone} tone""",
            'instructions': "Create an urgency-based hook that motivates immediate action on this topic. Audience: {audience}. Tone: {tone}."
        },
        'emotional': {
            'system': """You are an expert copywriter. Write an emotionally charged hook that:
- Evokes strong feelings (fear, hope, excitement, etc.)
- Uses emotional language
- Is concise and impactful
- Tailored for an audience of {audience} in a {tone} tone""",
            'instructions': "Create an emotional hook that resonates with the reader about this topic. Audience: {audience}. Tone: {tone}."
        },
        'benefit': {
            'system': """You are an expert copywriter. Write a benefit-driven hook that:
- Clearly states the main benefit or value
- Is concise and persuasive
- Tailored for an audience of {audience} in a {tone} tone""",
            'instructions': "Create a benefit-driven hook that highlights the main value of this topic. Audience: {audience}. Tone: {tone}."
        },
        'question': {
            'system': """You are an expert copywriter. Write a question-based hook that:
- Asks a thought-provoking or challenging question
- Relates directly to the topic
- Is concise and engaging
- Tailored for an audience of {audience} in a {tone} tone""",
            'instructions': "Create a question-based hook that makes the reader think about this topic. Audience: {audience}. Tone: {tone}."
        },
        'fomo': {
            'system': """You are an expert copywriter. Write a FOMO (fear of missing out) hook that:
- Emphasizes what the reader will miss if they don't act
- Uses scarcity or exclusivity language
- Is concise and compelling
- Tailored for an audience of {audience} in a {tone} tone""",
            'instructions': "Create a FOMO-based hook that makes the reader not want to miss out on this topic. Audience: {audience}. Tone: {tone}."
        },
        'authority': {
            'system': """You are an expert copywriter. Write an authority-based hook that:
- References experts, research, or trusted sources
- Builds credibility and trust
- Is concise and authoritative
- Tailored for an audience of {audience} in a {tone} tone""",
            'instructions': "Create an authority-based hook that builds trust in this topic. Audience: {audience}. Tone: {tone}."
        },
        'social_proof': {
            'system': """You are an expert copywriter. Write a social proof hook that:
- Shows that many people or respected groups are interested or involved
- Uses popularity or testimonials
- Is concise and persuasive
- Tailored for an audience of {audience} in a {tone} tone""",
            'instructions': "Create a social proof hook that shows this topic is popular or trusted. Audience: {audience}. Tone: {tone}."
        },
        'scarcity': {
            'system': """You are an expert copywriter. Write a scarcity-based hook that:
- Emphasizes limited availability or opportunity
- Uses scarcity language (e.g., 'only a few', 'limited time')
- Is concise and urgent
- Tailored for an audience of {audience} in a {tone} tone""",
            'instructions': "Create a scarcity-based hook that makes the reader act quickly on this topic. Audience: {audience}. Tone: {tone}."
        },
        'novelty': {
            'system': """You are an expert copywriter. Write a novelty-based hook that:
- Highlights something new, unique, or never seen before
- Uses language of innovation or surprise
- Is concise and intriguing
- Tailored for an audience of {audience} in a {tone} tone""",
            'instructions': "Create a novelty-based hook that highlights what's new or unique about this topic. Audience: {audience}. Tone: {tone}."
        },
        'storytelling': {
            'system': """You are an expert copywriter. Write a storytelling hook that:
- Begins a short, engaging story or scenario
- Relates directly to the topic
- Is concise and vivid
- Tailored for an audience of {audience} in a {tone} tone""",
            'instructions': "Create a storytelling hook that draws the reader in about this topic. Audience: {audience}. Tone: {tone}."
        },
    }

    def _generate_hook_from_template(self, trigger: str, topic: str, research_data: Dict[str, Any], context: dict = None, console=None) -> str:
        """Generate a hook using the modular template for the given trigger."""
        audience = context['audience'] if context else 'general public'
        tone = context['tone'] if context else 'informative'
        template = self.HOOK_PROMPT_TEMPLATES[trigger]
        system_prompt = template['system'].format(audience=audience, tone=tone)
        prompt = f"""
        Topic: {topic}
        Key Research Points:\n""" + '\n'.join(f"- {point}" for point in research_data.get('key_points', [])[:3]) + f"\n{template['instructions'].format(audience=audience, tone=tone)}"
        hook = self.ollama.generate_with_retry(prompt, system_prompt, console=console)
        return self._clean_hook(hook)
    
    # Refactor individual hook methods to use the modular template
    def _generate_curiosity_hook(self, topic, research_data, context=None, console=None):
        return self._generate_hook_from_template('curiosity', topic, research_data, context, console)
    def _generate_urgency_hook(self, topic, research_data, context=None, console=None):
        return self._generate_hook_from_template('urgency', topic, research_data, context, console)
    def _generate_emotional_hook(self, topic, research_data, context=None, console=None):
        return self._generate_hook_from_template('emotional', topic, research_data, context, console)
    def _generate_benefit_hook(self, topic, research_data, context=None, console=None):
        return self._generate_hook_from_template('benefit', topic, research_data, context, console)
    def _generate_question_hook(self, topic, research_data, context=None, console=None):
        return self._generate_hook_from_template('question', topic, research_data, context, console)
    def _generate_fomo_hook(self, topic, research_data, context=None, console=None):
        return self._generate_hook_from_template('fomo', topic, research_data, context, console)
    def _generate_authority_hook(self, topic, research_data, context=None, console=None):
        return self._generate_hook_from_template('authority', topic, research_data, context, console)
    def _generate_social_proof_hook(self, topic, research_data, context=None, console=None):
        return self._generate_hook_from_template('social_proof', topic, research_data, context, console)
    def _generate_scarcity_hook(self, topic, research_data, context=None, console=None):
        return self._generate_hook_from_template('scarcity', topic, research_data, context, console)
    def _generate_novelty_hook(self, topic, research_data, context=None, console=None):
        return self._generate_hook_from_template('novelty', topic, research_data, context, console)
    def _generate_storytelling_hook(self, topic, research_data, context=None, console=None):
        return self._generate_hook_from_template('storytelling', topic, research_data, context, console)
    
    def _generate_fallback_hook(self, topic: str) -> str:
        """Generate a simple fallback hook."""
        return f"Discover the latest insights and trends in {topic} that you need to know."
    
    def _clean_hook(self, hook: str) -> str:
        """Clean and format the hook."""
        if not hook:
            return ""
        
        # Remove quotes and extra whitespace
        hook = hook.strip().strip('"').strip("'")
        
        # Ensure it ends with proper punctuation
        if hook and not hook.endswith(('.', '!', '?')):
            hook += '.'
        
        return hook 