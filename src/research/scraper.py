import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
from src.utils.config import config
from src.utils.logger import logger

class ResearchScraper:
    """Web scraper for gathering topic research data."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
        self.sources = []
    
    def research_topic(self, topic: str) -> Dict[str, Any]:
        """Research a topic and gather information from multiple sources."""
        logger.info(f"Starting research for topic: {topic}")
        
        research_data = {
            'topic': topic,
            'sources': [],
            'key_points': [],
            'latest_developments': [],
            'summary': ''
        }
        
        try:
            # Search for recent articles and news
            search_results = self._search_topic(topic)
            
            # Scrape content from top results
            for url in search_results[:config.max_sources]:
                try:
                    content = self._scrape_url(url)
                    if content:
                        research_data['sources'].append({
                            'url': url,
                            'title': content.get('title', ''),
                            'content': content.get('content', ''),
                            'timestamp': content.get('timestamp', '')
                        })
                        
                        # Extract key points
                        key_points = self._extract_key_points(content.get('content', ''))
                        research_data['key_points'].extend(key_points)
                        
                        time.sleep(config.scraping_delay)  # Be respectful
                        
                except Exception as e:
                    logger.warning(f"Failed to scrape {url}: {e}")
                    continue
            
            # Remove duplicates and limit key points
            research_data['key_points'] = list(set(research_data['key_points']))[:20]
            
            # Generate summary
            if research_data['sources']:
                research_data['summary'] = self._generate_summary(research_data)
            
            logger.info(f"Research completed. Found {len(research_data['sources'])} sources")
            return research_data
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            return research_data
    
    def _search_topic(self, topic: str) -> List[str]:
        """Search for topic-related URLs (simplified implementation)."""
        # For MVP, we'll use a simple approach with some reliable sources
        # In a full implementation, you'd integrate with search APIs
        
        search_urls = [
            f"https://news.google.com/search?q={topic.replace(' ', '+')}",
            f"https://www.reddit.com/search/?q={topic.replace(' ', '+')}",
            f"https://medium.com/search?q={topic.replace(' ', '+')}"
        ]
        
        urls = []
        for search_url in search_urls:
            try:
                response = self.session.get(search_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract links (simplified)
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link['href']
                        if self._is_valid_url(href):
                            urls.append(href)
                            
            except Exception as e:
                logger.warning(f"Failed to search {search_url}: {e}")
                continue
        
        return urls[:config.max_sources]
    
    def _scrape_url(self, url: str) -> Dict[str, str]:
        """Scrape content from a URL."""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = ''
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Extract main content
            content = ''
            
            # Try to find main content areas
            content_selectors = [
                'article',
                '[role="main"]',
                '.content',
                '.post-content',
                '.entry-content',
                'main'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text()
                    break
            
            # If no main content found, get body text
            if not content:
                body = soup.find('body')
                if body:
                    content = body.get_text()
            
            # Clean content
            content = self._clean_text(content)
            
            return {
                'title': title,
                'content': content,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            return {}
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters
        text = re.sub(r'[^\w\s\.\,\!\?\-\:]', '', text)
        
        # Limit length
        if len(text) > 5000:
            text = text[:5000] + "..."
        
        return text.strip()
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content."""
        # Simple key point extraction
        sentences = re.split(r'[.!?]+', content)
        key_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:
                # Look for sentences with key indicators
                indicators = ['important', 'key', 'significant', 'major', 'latest', 'new', 'trend']
                if any(indicator in sentence.lower() for indicator in indicators):
                    key_points.append(sentence)
        
        return key_points[:10]  # Limit to 10 key points
    
    def _generate_summary(self, research_data: Dict[str, Any]) -> str:
        """Generate a summary of the research data."""
        summary_parts = []
        
        if research_data['key_points']:
            summary_parts.append("Key findings:")
            for i, point in enumerate(research_data['key_points'][:5], 1):
                summary_parts.append(f"{i}. {point}")
        
        if research_data['sources']:
            summary_parts.append(f"\nResearch based on {len(research_data['sources'])} sources.")
        
        return "\n".join(summary_parts)
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and interesting."""
        if not url.startswith('http'):
            return False
        
        # Skip common non-content URLs
        skip_domains = ['google.com', 'facebook.com', 'twitter.com', 'youtube.com']
        parsed = urlparse(url)
        
        return not any(domain in parsed.netloc for domain in skip_domains) 