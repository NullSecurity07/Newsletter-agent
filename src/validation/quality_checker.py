import re
import time
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse
from src.ollama.client import OllamaClient
from src.utils.logger import logger

class ContentQualityChecker:
    """Comprehensive content quality assessment and validation."""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
        self.quality_metrics = {}
    
    def assess_content_quality(self, content: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive content quality assessment."""
        logger.info("Starting content quality assessment")
        
        quality_report = {
            'overall_score': 0,
            'readability_score': 0,
            'factual_accuracy': 0,
            'coherence_score': 0,
            'engagement_score': 0,
            'source_alignment': 0,
            'issues': [],
            'suggestions': []
        }
        
        try:
            # Assess readability
            readability_score = self._assess_readability(content)
            quality_report['readability_score'] = readability_score
            
            # Assess factual accuracy
            factual_score = self._assess_factual_accuracy(content, research_data)
            quality_report['factual_accuracy'] = factual_score
            
            # Assess coherence and flow
            coherence_score = self._assess_coherence(content)
            quality_report['coherence_score'] = coherence_score
            
            # Assess engagement
            engagement_score = self._assess_engagement(content)
            quality_report['engagement_score'] = engagement_score
            
            # Assess source alignment
            source_score = self._assess_source_alignment(content, research_data)
            quality_report['source_alignment'] = source_score
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(quality_report)
            quality_report['overall_score'] = overall_score
            
            # Generate suggestions
            quality_report['suggestions'] = self._generate_suggestions(quality_report)
            
            logger.info(f"Content quality assessment completed. Overall score: {overall_score:.1f}/100")
            return quality_report
            
        except Exception as e:
            logger.error(f"Content quality assessment failed: {e}")
            quality_report['issues'].append(f"Assessment error: {e}")
            return quality_report
    
    def _assess_readability(self, content: str) -> float:
        """Assess content readability using various metrics."""
        try:
            # Basic readability metrics
            sentences = re.split(r'[.!?]+', content)
            words = re.findall(r'\b\w+\b', content.lower())
            
            if not sentences or not words:
                return 0.0
            
            # Average sentence length
            avg_sentence_length = len(words) / len(sentences)
            
            # Word complexity (percentage of long words)
            long_words = [word for word in words if len(word) > 6]
            complexity_ratio = len(long_words) / len(words) if words else 0
            
            # Paragraph structure
            paragraphs = content.split('\n\n')
            paragraph_score = min(len(paragraphs) / 5, 1.0)  # Prefer 5+ paragraphs
            
            # Calculate readability score
            sentence_score = max(0, 100 - (avg_sentence_length - 15) * 2)  # Prefer 15 words/sentence
            complexity_score = max(0, 100 - complexity_ratio * 200)  # Prefer simpler words
            structure_score = paragraph_score * 100
            
            readability_score = (sentence_score + complexity_score + structure_score) / 3
            return max(0, min(100, readability_score))
            
        except Exception as e:
            logger.warning(f"Readability assessment failed: {e}")
            return 50.0
    
    def _assess_factual_accuracy(self, content: str, research_data: Dict[str, Any]) -> float:
        """Assess factual accuracy against research data."""
        try:
            # Extract key facts from research
            research_facts = self._extract_research_facts(research_data)
            
            if not research_facts:
                return 50.0  # Neutral score if no research data
            
            # Use AI to assess factual alignment
            system_prompt = """You are a fact-checking expert. Assess how well the content aligns with the provided research facts. 
            Score from 0-100 where 100 means perfect factual alignment."""
            
            prompt = f"""
            Content to assess:
            {content[:1000]}...
            
            Research facts to verify against:
            {chr(10).join(f"- {fact}" for fact in research_facts[:10])}
            
            Rate the factual accuracy from 0-100 and provide a brief explanation.
            """
            
            response = self.ollama.generate_with_retry(prompt, system_prompt)
            
            # Extract score from response
            score_match = re.search(r'(\d+)', response)
            if score_match:
                return min(100, max(0, int(score_match.group(1))))
            
            return 50.0
            
        except Exception as e:
            logger.warning(f"Factual accuracy assessment failed: {e}")
            return 50.0
    
    def _assess_coherence(self, content: str) -> float:
        """Assess content coherence and logical flow."""
        try:
            system_prompt = """You are a content editor. Assess the coherence and logical flow of the content. 
            Score from 0-100 where 100 means excellent coherence and flow."""
            
            prompt = f"""
            Content to assess:
            {content[:1000]}...
            
            Rate the coherence and logical flow from 0-100. Consider:
            - Logical progression of ideas
            - Smooth transitions between sections
            - Clear topic sentences
            - Consistent tone and style
            """
            
            response = self.ollama.generate_with_retry(prompt, system_prompt)
            
            # Extract score from response
            score_match = re.search(r'(\d+)', response)
            if score_match:
                return min(100, max(0, int(score_match.group(1))))
            
            return 50.0
            
        except Exception as e:
            logger.warning(f"Coherence assessment failed: {e}")
            return 50.0
    
    def _assess_engagement(self, content: str) -> float:
        """Assess content engagement and reader interest."""
        try:
            # Engagement indicators
            engagement_indicators = [
                r'\?',  # Questions
                r'!',   # Exclamations
                r'\b(you|your|we|our)\b',  # Personal pronouns
                r'\b(imagine|consider|think|suppose)\b',  # Interactive words
                r'\b(amazing|incredible|fascinating|exciting)\b',  # Emotional words
            ]
            
            engagement_score = 0
            for indicator in engagement_indicators:
                matches = len(re.findall(indicator, content, re.IGNORECASE))
                engagement_score += min(matches * 10, 20)  # Cap at 20 points per indicator
            
            # Normalize to 0-100 scale
            engagement_score = min(100, engagement_score)
            
            return engagement_score
            
        except Exception as e:
            logger.warning(f"Engagement assessment failed: {e}")
            return 50.0
    
    def _assess_source_alignment(self, content: str, research_data: Dict[str, Any]) -> float:
        """Assess how well content aligns with source information."""
        try:
            if not research_data.get('sources'):
                return 50.0
            
            # Extract key terms from research
            research_terms = self._extract_research_terms(research_data)
            
            # Count research terms in content
            term_matches = 0
            for term in research_terms:
                if term.lower() in content.lower():
                    term_matches += 1
            
            # Calculate alignment score
            if research_terms:
                alignment_score = (term_matches / len(research_terms)) * 100
                return min(100, alignment_score)
            
            return 50.0
            
        except Exception as e:
            logger.warning(f"Source alignment assessment failed: {e}")
            return 50.0
    
    def _extract_research_facts(self, research_data: Dict[str, Any]) -> List[str]:
        """Extract key facts from research data."""
        facts = []
        
        # Add key points
        facts.extend(research_data.get('key_points', []))
        
        # Add source titles and descriptions
        for source in research_data.get('sources', []):
            if source.get('title'):
                facts.append(source['title'])
            if source.get('description'):
                facts.append(source['description'])
        
        return facts[:20]  # Limit to 20 facts
    
    def _extract_research_terms(self, research_data: Dict[str, Any]) -> List[str]:
        """Extract key terms from research data."""
        terms = set()
        
        # Extract from topic
        topic = research_data.get('topic', '')
        terms.update(topic.lower().split())
        
        # Extract from key points
        for point in research_data.get('key_points', []):
            words = re.findall(r'\b\w{4,}\b', point.lower())
            terms.update(words[:5])  # Top 5 words per point
        
        return list(terms)[:30]  # Limit to 30 terms
    
    def _calculate_overall_score(self, quality_report: Dict[str, Any]) -> float:
        """Calculate overall quality score."""
        weights = {
            'readability_score': 0.25,
            'factual_accuracy': 0.30,
            'coherence_score': 0.20,
            'engagement_score': 0.15,
            'source_alignment': 0.10
        }
        
        overall_score = 0
        for metric, weight in weights.items():
            overall_score += quality_report.get(metric, 0) * weight
        
        return round(overall_score, 1)
    
    def _generate_suggestions(self, quality_report: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on quality scores."""
        suggestions = []
        
        if quality_report['readability_score'] < 70:
            suggestions.append("Consider shorter sentences and simpler language for better readability")
        
        if quality_report['factual_accuracy'] < 70:
            suggestions.append("Verify facts against research sources and add citations")
        
        if quality_report['coherence_score'] < 70:
            suggestions.append("Improve logical flow with better transitions and topic sentences")
        
        if quality_report['engagement_score'] < 70:
            suggestions.append("Add more interactive elements like questions and personal pronouns")
        
        if quality_report['source_alignment'] < 70:
            suggestions.append("Better align content with research findings and key terms")
        
        if quality_report['overall_score'] < 60:
            suggestions.append("Consider significant revision to improve overall quality")
        
        return suggestions
    
    def validate_content(self, content: str, research_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate content and return pass/fail with detailed report."""
        quality_report = self.assess_content_quality(content, research_data)
        
        # Content passes if overall score is above 60
        passes = quality_report['overall_score'] >= 60
        
        return passes, quality_report 