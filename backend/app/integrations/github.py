"""
GitHub API integration for repository and documentation search.
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime

import httpx
from github import Github, GithubException

from app.core.config import settings

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for GitHub API v3."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client."""
        self.token = token or settings.GITHUB_TOKEN
        self.client = None
        if self.token:
            try:
                self.client = Github(self.token)
            except Exception as e:
                logger.error(f"Failed to initialize GitHub client: {e}")
    
    async def search_repositories(
        self,
        query: str,
        language: Optional[str] = None,
        sort: str = "stars",
        max_results: int = 10
    ) -> List[Dict]:
        """
        Search for repositories on GitHub.
        
        Args:
            query: Search query
            language: Filter by programming language
            sort: Sort by (stars, forks, updated)
            max_results: Maximum number of results
        
        Returns:
            List of repository metadata dictionaries
        """
        if not self.client:
            logger.warning("GitHub API not configured, returning mock data")
            return self._get_mock_repositories(query, max_results)
        
        try:
            # Build search query
            search_query = query
            if language:
                search_query += f" language:{language}"
            
            # Search repositories
            repositories = self.client.search_repositories(
                query=search_query,
                sort=sort,
                order="desc"
            )
            
            # Parse results
            results = []
            for i, repo in enumerate(repositories):
                if i >= max_results:
                    break
                
                repo_data = self._parse_repository(repo)
                results.append(repo_data)
            
            return results
            
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            return self._get_mock_repositories(query, max_results)
        except Exception as e:
            logger.error(f"Error searching GitHub: {e}")
            return []
    
    async def get_repository(self, owner: str, repo_name: str) -> Optional[Dict]:
        """
        Get detailed information about a specific repository.
        
        Args:
            owner: Repository owner
            repo_name: Repository name
        
        Returns:
            Repository metadata dictionary or None
        """
        if not self.client:
            return self._get_mock_repository_details(owner, repo_name)
        
        try:
            repo = self.client.get_repo(f"{owner}/{repo_name}")
            return self._parse_repository(repo)
            
        except Exception as e:
            logger.error(f"Error getting repository: {e}")
            return None
    
    async def get_readme(self, owner: str, repo_name: str) -> Optional[str]:
        """
        Get README content from a repository.
        
        Args:
            owner: Repository owner
            repo_name: Repository name
        
        Returns:
            README content as string or None
        """
        if not self.client:
            return "# Sample README\n\nThis is a sample README file."
        
        try:
            repo = self.client.get_repo(f"{owner}/{repo_name}")
            readme = repo.get_readme()
            return readme.decoded_content.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error getting README: {e}")
            return None
    
    async def search_code(
        self,
        query: str,
        language: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Search for code on GitHub.
        
        Args:
            query: Search query
            language: Filter by programming language
            max_results: Maximum number of results
        
        Returns:
            List of code search results
        """
        if not self.client:
            return []
        
        try:
            search_query = query
            if language:
                search_query += f" language:{language}"
            
            code_results = self.client.search_code(query=search_query)
            
            results = []
            for i, code in enumerate(code_results):
                if i >= max_results:
                    break
                
                results.append({
                    'name': code.name,
                    'path': code.path,
                    'repository': code.repository.full_name,
                    'url': code.html_url,
                    'sha': code.sha
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching code: {e}")
            return []
    
    async def get_trending_repositories(
        self,
        language: Optional[str] = None,
        since: str = "daily"
    ) -> List[Dict]:
        """
        Get trending repositories (using GitHub search as approximation).
        
        Args:
            language: Filter by programming language
            since: Time period (daily, weekly, monthly)
        
        Returns:
            List of trending repository metadata
        """
        if not self.client:
            return []
        
        try:
            # Calculate date range
            from datetime import timedelta
            
            days_map = {"daily": 1, "weekly": 7, "monthly": 30}
            days = days_map.get(since, 7)
            
            date_threshold = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            # Build query
            query = f"created:>{date_threshold}"
            if language:
                query += f" language:{language}"
            
            # Search repositories
            repositories = self.client.search_repositories(
                query=query,
                sort="stars",
                order="desc"
            )
            
            results = []
            for i, repo in enumerate(repositories):
                if i >= 10:
                    break
                results.append(self._parse_repository(repo))
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting trending repositories: {e}")
            return []
    
    def _parse_repository(self, repo) -> Dict:
        """Parse GitHub repository object into standardized format."""
        return {
            'id': repo.id,
            'name': repo.name,
            'full_name': repo.full_name,
            'owner': repo.owner.login,
            'description': repo.description or '',
            'url': repo.html_url,
            'clone_url': repo.clone_url,
            'homepage': repo.homepage,
            'language': repo.language,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'watchers': repo.watchers_count,
            'open_issues': repo.open_issues_count,
            'created_at': repo.created_at.isoformat() if repo.created_at else None,
            'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
            'topics': repo.get_topics() if hasattr(repo, 'get_topics') else [],
            'license': repo.license.name if repo.license else None,
            'resource_type': 'repository',
            'source_platform': 'github'
        }
    
    def _get_mock_repositories(self, query: str, max_results: int) -> List[Dict]:
        """Return mock repository data when API is not configured."""
        return [
            {
                'id': i,
                'name': f'{query.lower().replace(" ", "-")}-{i}',
                'full_name': f'example/{query.lower().replace(" ", "-")}-{i}',
                'owner': 'example',
                'description': f'A comprehensive {query} library with examples',
                'url': f'https://github.com/example/{query.lower().replace(" ", "-")}-{i}',
                'clone_url': f'https://github.com/example/{query.lower().replace(" ", "-")}-{i}.git',
                'homepage': None,
                'language': 'Python',
                'stars': 1000 + (i * 100),
                'forks': 100 + (i * 10),
                'watchers': 50 + (i * 5),
                'open_issues': 10 + i,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'topics': [query.lower(), 'tutorial', 'examples'],
                'license': 'MIT',
                'resource_type': 'repository',
                'source_platform': 'github'
            }
            for i in range(1, min(max_results + 1, 6))
        ]
    
    def _get_mock_repository_details(self, owner: str, repo_name: str) -> Dict:
        """Return mock repository details."""
        return {
            'id': 12345,
            'name': repo_name,
            'full_name': f'{owner}/{repo_name}',
            'owner': owner,
            'description': 'Sample repository description',
            'url': f'https://github.com/{owner}/{repo_name}',
            'clone_url': f'https://github.com/{owner}/{repo_name}.git',
            'homepage': None,
            'language': 'Python',
            'stars': 1500,
            'forks': 200,
            'watchers': 75,
            'open_issues': 15,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'topics': ['sample', 'tutorial'],
            'license': 'MIT',
            'resource_type': 'repository',
            'source_platform': 'github'
        }


# Singleton instance
github_client = GitHubClient()
