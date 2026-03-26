import requests
import time
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from newsapi import NewsApiClient
from gnews import GNews
import newspaper
import feedparser
from src.utils.config import config
from src.utils.logger import logger
from src.utils.db import save_research, fetch_research
from src.research.trend_analysis import TrendAnalyzer

# Whitelist and blacklist for source credibility
CREDIBLE_DOMAINS = {"nature.com", "nejm.org", "who.int", "cdc.gov", "reuters.com", "bbc.com"}
BLACKLISTED_DOMAINS = {"clickbait.com", "fake-news.net"}

request_timestamps = []
RATE_LIMIT = 10  # max requests per minute

def check_rate_limit(console=None):
    now = time.time()
    # Remove timestamps older than 60 seconds
    global request_timestamps
    request_timestamps = [t for t in request_timestamps if now - t < 60]
    if len(request_timestamps) >= RATE_LIMIT:
        if console:
            console.print("[yellow]Warning: Approaching rate limit for web requests. Slow down to avoid being blocked.[/yellow]")
        else:
            print("[Warning] Approaching rate limit for web requests.")
    request_timestamps.append(now)

def is_credible_source(url):
    """Return True if the source is credible, False if blacklisted, else None."""
    domain = urlparse(url).netloc.replace('www.', '')
    if domain in CREDIBLE_DOMAINS:
        return True
    if domain in BLACKLISTED_DOMAINS:
        return False
    return None

class EnhancedResearchScraper:
    """Enhanced web scraper with news API integration and credibility assessment."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
        
        # Initialize news APIs
        self.newsapi = None
        self.gnews = None
        self._init_news_apis()
        
        # Credible domains (high authority news sources)
        self.credible_domains = {
            'reuters.com', 'ap.org', 'bbc.com', 'cnn.com', 'nytimes.com',
            'washingtonpost.com', 'wsj.com', 'ft.com', 'economist.com',
            'techcrunch.com', 'wired.com', 'arstechnica.com', 'theverge.com',
            'mit.edu', 'harvard.edu', 'stanford.edu', 'nature.com', 'science.org'
        }
        
        # Domain credibility scores
        self.domain_scores = {}
        
        # Initialize trend analyzer
        self.trend_analyzer = TrendAnalyzer()
    
    def _init_news_apis(self):
        """Initialize news API clients if API keys are available."""
        try:
            # Try to get NewsAPI key from environment
            newsapi_key = config.newsapi_key if hasattr(config, 'newsapi_key') else None
            if newsapi_key:
                self.newsapi = NewsApiClient(api_key=newsapi_key)
                logger.info("NewsAPI client initialized")
        except Exception as e:
            logger.warning(f"NewsAPI initialization failed: {e}")
        
        try:
            # GNews doesn't require API key for basic usage
            self.gnews = GNews(language='en', country='US', max_results=20)
            logger.info("GNews client initialized")
        except Exception as e:
            logger.warning(f"GNews initialization failed: {e}")
    
    def research_topic(self, topic: str) -> Dict[str, Any]:
        """Enhanced topic research with multiple sources, credibility assessment, and trend analysis."""
        logger.info(f"Starting enhanced research for topic: {topic}")
        
        # Check DB for recent research first
        db_result = fetch_research(topic)
        if db_result:
            logger.info(f"Loaded research for '{topic}' from database.")
            # Convert DB format to expected research_data format
            return {
                'topic': topic,
                'sources': db_result.get('sources', []),
                'key_points': db_result.get('key_points', []),
                'latest_developments': db_result.get('raw_data', {}).get('latest_developments', []),
                'summary': db_result.get('raw_data', {}).get('summary', ''),
                'credibility_score': db_result.get('raw_data', {}).get('credibility_score', 0),
                'source_diversity': db_result.get('raw_data', {}).get('source_diversity', 0),
                'trend_summary': db_result.get('raw_data', {}).get('trend_summary', '')
            }
        
        research_data = {
            'topic': topic,
            'sources': [],
            'key_points': [],
            'latest_developments': [],
            'summary': '',
            'credibility_score': 0,
            'source_diversity': 0,
            'trend_summary': ''
        }
        
        try:
            # Trend analysis integration
            trends = self.trend_analyzer.fetch_trends(topic)
            research_data['trend_summary'] = self.trend_analyzer.summarize_trends(trends)
            
            # Collect sources from multiple methods
            all_sources = []
            
            # 1. News API sources
            if self.newsapi:
                newsapi_sources = self._get_newsapi_sources(topic)
                all_sources.extend(newsapi_sources)
            
            # 2. GNews sources
            if self.gnews:
                gnews_sources = self._get_gnews_sources(topic)
                all_sources.extend(gnews_sources)
            
            # 3. RSS feeds from credible sources
            rss_sources = self._get_rss_sources(topic)
            all_sources.extend(rss_sources)
            
            # 4. Fallback to web scraping
            if len(all_sources) < 5:
                web_sources = self._get_web_sources(topic)
                all_sources.extend(web_sources)
            
            # Assess credibility and diversity
            scored_sources = self._assess_sources(all_sources)
            
            # Select best sources
            best_sources = self._select_best_sources(scored_sources)
            
            # Extract content from selected sources
            for source in best_sources:
                try:
                    content = self._extract_content(source['url'])
                    if content:
                        source.update(content)
                        research_data['sources'].append(source)
                        
                        # Extract key points
                        key_points = self._extract_key_points(content.get('content', ''))
                        research_data['key_points'].extend(key_points)
                        
                        time.sleep(config.scraping_delay)
                        
                except Exception as e:
                    logger.warning(f"Failed to extract content from {source['url']}: {e}")
                    continue
            
            # Calculate metrics
            research_data['credibility_score'] = self._calculate_credibility_score(research_data['sources'])
            research_data['source_diversity'] = self._calculate_diversity_score(research_data['sources'])
            
            # Remove duplicates and limit key points
            research_data['key_points'] = list(set(research_data['key_points']))[:25]
            
            # Generate enhanced summary
            if research_data['sources']:
                research_data['summary'] = self._generate_enhanced_summary(research_data)
            
            logger.info(f"Enhanced research completed. Found {len(research_data['sources'])} sources with credibility score: {research_data['credibility_score']:.2f}")
            
            # Save research to DB
            save_research(
                topic,
                research_data['key_points'],
                [s.get('content', '') for s in research_data['sources']],
                research_data['sources'],
                {
                    'latest_developments': research_data.get('latest_developments', []),
                    'summary': research_data.get('summary', ''),
                    'credibility_score': research_data.get('credibility_score', 0),
                    'source_diversity': research_data.get('source_diversity', 0),
                    'trend_summary': research_data.get('trend_summary', '')
                }
            )
            return research_data
            
        except Exception as e:
            logger.error(f"Enhanced research failed: {e}")
            return research_data
    
    def _get_newsapi_sources(self, topic: str) -> List[Dict[str, Any]]:
        """Get sources from NewsAPI."""
        sources = []
        try:
            # Search for recent articles
            articles = self.newsapi.get_everything(
                q=topic,
                language='en',
                sort_by='relevancy',
                from_param=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                page_size=20
            )
            
            for article in articles.get('articles', []):
                sources.append({
                    'url': article.get('url', ''),
                    'title': article.get('title', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'published_at': article.get('publishedAt', ''),
                    'description': article.get('description', ''),
                    'method': 'newsapi'
                })
                
        except Exception as e:
            logger.warning(f"NewsAPI search failed: {e}")
        
        return sources
    
    def _get_gnews_sources(self, topic: str) -> List[Dict[str, Any]]:
        """Get sources from GNews."""
        sources = []
        try:
            articles = self.gnews.get_news(topic)
            
            for article in articles:
                sources.append({
                    'url': article.get('link', ''),
                    'title': article.get('title', ''),
                    'source': article.get('publisher', {}).get('title', ''),
                    'published_at': article.get('published date', ''),
                    'description': article.get('description', ''),
                    'method': 'gnews'
                })
                
        except Exception as e:
            logger.warning(f"GNews search failed: {e}")
        
        return sources
    
    def _get_rss_sources(self, topic: str) -> List[Dict[str, Any]]:
        """Get sources from RSS feeds of credible sources."""
        sources = []
        
        # RSS feeds from credible sources
        rss_feeds = [
            'https://feeds.reuters.com/reuters/technologyNews',
            'https://rss.cnn.com/rss/edition_technology.rss',
            'https://feeds.feedburner.com/TechCrunch/',
            'https://www.wired.com/feed/rss'
        ]
        
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:5]:  # Limit to 5 entries per feed
                    # Check if entry is relevant to topic
                    if self._is_relevant_to_topic(entry, topic):
                        sources.append({
                            'url': entry.get('link', ''),
                            'title': entry.get('title', ''),
                            'source': feed.feed.get('title', ''),
                            'published_at': entry.get('published', ''),
                            'description': entry.get('summary', ''),
                            'method': 'rss'
                        })
                        
            except Exception as e:
                logger.warning(f"RSS feed {feed_url} failed: {e}")
        
        return sources
    
    def _get_web_sources(self, topic: str) -> List[Dict[str, Any]]:
        """Fallback web scraping for additional sources."""
        # This is the original web scraping method as fallback
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
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link['href']
                        if self._is_valid_url(href):
                            urls.append(href)
            except Exception as e:
                logger.warning(f"Failed to search {search_url}: {e}")
        
        return [{'url': url, 'method': 'web_scraping'} for url in urls[:config.max_sources]]
    
    def _assess_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assess credibility and quality of sources."""
        scored_sources = []
        
        for source in sources:
            score = 0
            url = source.get('url', '')
            
            if not url:
                continue
            
            # Domain credibility
            domain = urlparse(url).netloc.lower()
            if domain in self.credible_domains:
                score += 50
            elif domain in self.domain_scores:
                score += self.domain_scores[domain]
            
            # Method credibility
            method = source.get('method', '')
            if method == 'newsapi':
                score += 30
            elif method == 'gnews':
                score += 25
            elif method == 'rss':
                score += 20
            elif method == 'web_scraping':
                score += 10
            
            # Recency
            published_at = source.get('published_at', '')
            if published_at:
                try:
                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    days_old = (datetime.now() - pub_date).days
                    if days_old <= 1:
                        score += 20
                    elif days_old <= 7:
                        score += 15
                    elif days_old <= 30:
                        score += 10
                except:
                    pass
            
            # Content quality indicators
            title = source.get('title', '')
            description = source.get('description', '')
            
            if title and len(title) > 20:
                score += 10
            if description and len(description) > 50:
                score += 10
            
            source['credibility_score'] = score
            scored_sources.append(source)
        
        return scored_sources
    
    def _select_best_sources(self, scored_sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Select the best sources based on credibility and diversity."""
        # Sort by credibility score
        scored_sources.sort(key=lambda x: x.get('credibility_score', 0), reverse=True)
        
        # Select top sources with diversity
        selected = []
        domains_seen = set()
        
        for source in scored_sources:
            if len(selected) >= config.max_sources:
                break
            
            domain = urlparse(source.get('url', '')).netloc.lower()
            
            # Prefer diverse sources
            if domain not in domains_seen or len(selected) < 5:
                selected.append(source)
                domains_seen.add(domain)
        
        return selected
    
    def _extract_content(self, url: str) -> Optional[Dict[str, str]]:
        """Extract content from URL using newspaper3k."""
        try:
            article = newspaper.Article(url)
            article.download()
            article.parse()
            
            return {
                'title': article.title,
                'content': article.text,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.warning(f"Failed to extract content from {url}: {e}")
            return None
    
    def _is_relevant_to_topic(self, entry: Any, topic: str) -> bool:
        """Check if RSS entry is relevant to the topic."""
        title = entry.get('title', '').lower()
        summary = entry.get('summary', '').lower()
        topic_words = topic.lower().split()
        
        # Check if topic words appear in title or summary
        for word in topic_words:
            if len(word) > 3 and (word in title or word in summary):
                return True
        
        return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and interesting."""
        if not url.startswith('http'):
            return False
        
        skip_domains = ['google.com', 'facebook.com', 'twitter.com', 'youtube.com']
        parsed = urlparse(url)
        
        return not any(domain in parsed.netloc for domain in skip_domains)
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content."""
        sentences = re.split(r'[.!?]+', content)
        key_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:
                indicators = ['important', 'key', 'significant', 'major', 'latest', 'new', 'trend', 'study', 'research', 'found']
                if any(indicator in sentence.lower() for indicator in indicators):
                    key_points.append(sentence)
        
        return key_points[:15]
    
    def _calculate_credibility_score(self, sources: List[Dict[str, Any]]) -> float:
        """Calculate overall credibility score."""
        if not sources:
            return 0.0
        
        total_score = sum(source.get('credibility_score', 0) for source in sources)
        return total_score / len(sources)
    
    def _calculate_diversity_score(self, sources: List[Dict[str, Any]]) -> float:
        """Calculate source diversity score."""
        if not sources:
            return 0.0
        
        domains = set()
        for source in sources:
            domain = urlparse(source.get('url', '')).netloc.lower()
            domains.add(domain)
        
        return len(domains) / len(sources)
    
    def _generate_enhanced_summary(self, research_data: Dict[str, Any]) -> str:
        """Generate enhanced summary with credibility metrics."""
        summary_parts = []
        
        if research_data['key_points']:
            summary_parts.append("Key findings:")
            for i, point in enumerate(research_data['key_points'][:5], 1):
                summary_parts.append(f"{i}. {point}")
        
        if research_data['sources']:
            summary_parts.append(f"\nResearch based on {len(research_data['sources'])} sources.")
            summary_parts.append(f"Credibility score: {research_data['credibility_score']:.1f}/100")
            summary_parts.append(f"Source diversity: {research_data['source_diversity']:.1f}")
        
        return "\n".join(summary_parts) 