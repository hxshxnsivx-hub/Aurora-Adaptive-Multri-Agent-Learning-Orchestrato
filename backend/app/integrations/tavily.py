"""
Tavily Search API integration for high-quality article discovery.
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class TavilyClient:
    """Client for Tavily Search API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Tavily client."""
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.base_url = "https://api.tavily.com"
    
    async def search(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = 10,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Search for high-quality content using Tavily.
        
        Args:
            query: Search query
            search_depth: Search depth (basic or advanced)
            max_results: Maximum number of results
            include_domains: List of domains to include
            exclude_domains: List of domains to exclude
        
        Returns:
            List of search result dictionaries
        """
        if not self.api_key:
            logger.warning("Tavily API not configured, returning mock data")
            return self._get_mock_results(query, max_results)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "search_depth": search_depth,
                        "max_results": max_results,
                        "include_domains": include_domains or [],
                        "exclude_domains": exclude_domains or []
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_results(data.get("results", []))
                else:
                    logger.error(f"Tavily API error: {response.status_code}")
                    return self._get_mock_results(query, max_results)
                    
        except Exception as e:
            logger.error(f"Error searching Tavily: {e}")
            return self._get_mock_results(query, max_results)
    
    async def search_news(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Search for news articles.
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of news article dictionaries
        """
        # Tavily can filter by recency
        return await self.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
    
    async def extract_content(self, url: str) -> Optional[Dict]:
        """
        Extract clean content from a URL.
        
        Args:
            url: URL to extract content from
        
        Returns:
            Extracted content dictionary or None
        """
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/extract",
                    json={
                        "api_key": self.api_key,
                        "url": url
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Tavily extract error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return None
    
    def _parse_results(self, results: List[Dict]) -> List[Dict]:
        """Parse Tavily search results into standardized format."""
        parsed = []
        for result in results:
            parsed.append({
                'title': result.get('title', ''),
                'url': result.get('url', ''),
                'content': result.get('content', ''),
                'snippet': result.get('snippet', ''),
                'published_date': result.get('published_date'),
                'author': result.get('author'),
                'score': result.get('score', 0.0),
                'resource_type': 'article',
                'source_platform': 'web'
            })
        return parsed
    
    def _get_mock_results(self, query: str, max_results: int) -> List[Dict]:
        """Return mock search results when API is not configured."""
        return [
            {
                'title': f'Complete Guide to {query} - Part {i}',
                'url': f'https://example.com/{query.lower().replace(" ", "-")}-guide-{i}',
                'content': f'This is a comprehensive guide covering {query} in detail...',
                'snippet': f'Learn everything about {query} with practical examples and best practices.',
                'published_date': datetime.utcnow().isoformat(),
                'author': 'Tech Writer',
                'score': 0.9 - (i * 0.05),
                'resource_type': 'article',
                'source_platform': 'web'
            }
            for i in range(1, min(max_results + 1, 6))
        ]


# Singleton instance
tavily_client = TavilyClient()
