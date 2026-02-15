"""
Notion API integration for task and database synchronization.
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime

from notion_client import AsyncClient
from notion_client.errors import APIResponseError

from app.core.config import settings

logger = logging.getLogger(__name__)


class NotionClient:
    """Client for Notion API."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize Notion client.
        
        Args:
            token: Notion integration token or OAuth access token
        """
        self.token = token
        self.client = None
        if self.token:
            try:
                self.client = AsyncClient(auth=self.token)
            except Exception as e:
                logger.error(f"Failed to initialize Notion client: {e}")
    
    @staticmethod
    def get_oauth_url(redirect_uri: str, state: str) -> str:
        """
        Get Notion OAuth authorization URL.
        
        Args:
            redirect_uri: OAuth redirect URI
            state: State parameter for CSRF protection
        
        Returns:
            Authorization URL
        """
        client_id = settings.NOTION_CLIENT_ID
        auth_url = (
            f"https://api.notion.com/v1/oauth/authorize"
            f"?client_id={client_id}"
            f"&response_type=code"
            f"&owner=user"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
        )
        return auth_url
    
    @staticmethod
    async def exchange_code_for_token(code: str, redirect_uri: str) -> Optional[Dict]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code
            redirect_uri: OAuth redirect URI
        
        Returns:
            Token response dictionary or None
        """
        import httpx
        import base64
        
        client_id = settings.NOTION_CLIENT_ID
        client_secret = settings.NOTION_CLIENT_SECRET
        
        # Create basic auth header
        auth_string = f"{client_id}:{client_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        try:
            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(
                    "https://api.notion.com/v1/oauth/token",
                    headers={
                        "Authorization": f"Basic {auth_b64}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect_uri
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Notion OAuth error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return None
    
    async def search(
        self,
        query: Optional[str] = None,
        filter_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for pages and databases.
        
        Args:
            query: Search query
            filter_type: Filter by type ('page' or 'database')
        
        Returns:
            List of search results
        """
        if not self.client:
            logger.warning("Notion API not configured, returning mock data")
            return self._get_mock_search_results()
        
        try:
            search_params = {}
            if query:
                search_params['query'] = query
            if filter_type:
                search_params['filter'] = {'property': 'object', 'value': filter_type}
            
            response = await self.client.search(**search_params)
            return response.get('results', [])
            
        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return self._get_mock_search_results()
        except Exception as e:
            logger.error(f"Error searching Notion: {e}")
            return []
    
    async def get_database(self, database_id: str) -> Optional[Dict]:
        """
        Get database information.
        
        Args:
            database_id: Database ID
        
        Returns:
            Database dictionary or None
        """
        if not self.client:
            return self._get_mock_database(database_id)
        
        try:
            database = await self.client.databases.retrieve(database_id=database_id)
            return database
            
        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting database: {e}")
            return None
    
    async def query_database(
        self,
        database_id: str,
        filter_params: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Query database for pages.
        
        Args:
            database_id: Database ID
            filter_params: Filter parameters
            sorts: Sort parameters
        
        Returns:
            List of page dictionaries
        """
        if not self.client:
            return self._get_mock_pages()
        
        try:
            query_params = {}
            if filter_params:
                query_params['filter'] = filter_params
            if sorts:
                query_params['sorts'] = sorts
            
            response = await self.client.databases.query(
                database_id=database_id,
                **query_params
            )
            return response.get('results', [])
            
        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return self._get_mock_pages()
        except Exception as e:
            logger.error(f"Error querying database: {e}")
            return []
    
    async def create_page(
        self,
        parent_id: str,
        properties: Dict,
        parent_type: str = "database_id"
    ) -> Optional[Dict]:
        """
        Create a new page in a database or as a child of another page.
        
        Args:
            parent_id: Parent database or page ID
            properties: Page properties
            parent_type: Type of parent ('database_id' or 'page_id')
        
        Returns:
            Created page dictionary or None
        """
        if not self.client:
            return self._get_mock_page(properties)
        
        try:
            page_data = {
                'parent': {parent_type: parent_id},
                'properties': properties
            }
            
            page = await self.client.pages.create(**page_data)
            return page
            
        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating page: {e}")
            return None
    
    async def update_page(
        self,
        page_id: str,
        properties: Dict
    ) -> Optional[Dict]:
        """
        Update page properties.
        
        Args:
            page_id: Page ID
            properties: Updated properties
        
        Returns:
            Updated page dictionary or None
        """
        if not self.client:
            return None
        
        try:
            page = await self.client.pages.update(
                page_id=page_id,
                properties=properties
            )
            return page
            
        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error updating page: {e}")
            return None
    
    async def get_page(self, page_id: str) -> Optional[Dict]:
        """
        Get page information.
        
        Args:
            page_id: Page ID
        
        Returns:
            Page dictionary or None
        """
        if not self.client:
            return None
        
        try:
            page = await self.client.pages.retrieve(page_id=page_id)
            return page
            
        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting page: {e}")
            return None
    
    async def archive_page(self, page_id: str) -> bool:
        """
        Archive (delete) a page.
        
        Args:
            page_id: Page ID
        
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            await self.client.pages.update(
                page_id=page_id,
                archived=True
            )
            return True
            
        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error archiving page: {e}")
            return False
    
    async def create_task_page(
        self,
        database_id: str,
        title: str,
        status: str = "Not Started",
        due_date: Optional[datetime] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Create a task page in a Notion database.
        
        Args:
            database_id: Database ID
            title: Task title
            status: Task status
            due_date: Due date
            description: Task description
            tags: Task tags
        
        Returns:
            Created page dictionary or None
        """
        properties = {
            'Name': {
                'title': [
                    {
                        'text': {
                            'content': title
                        }
                    }
                ]
            },
            'Status': {
                'select': {
                    'name': status
                }
            }
        }
        
        if due_date:
            properties['Due Date'] = {
                'date': {
                    'start': due_date.isoformat()
                }
            }
        
        if description:
            properties['Description'] = {
                'rich_text': [
                    {
                        'text': {
                            'content': description
                        }
                    }
                ]
            }
        
        if tags:
            properties['Tags'] = {
                'multi_select': [{'name': tag} for tag in tags]
            }
        
        return await self.create_page(database_id, properties)
    
    async def update_task_status(
        self,
        page_id: str,
        status: str
    ) -> Optional[Dict]:
        """
        Update task status.
        
        Args:
            page_id: Page ID
            status: New status
        
        Returns:
            Updated page dictionary or None
        """
        properties = {
            'Status': {
                'select': {
                    'name': status
                }
            }
        }
        
        return await self.update_page(page_id, properties)
    
    def _get_mock_search_results(self) -> List[Dict]:
        """Return mock search results."""
        return [
            {
                'object': 'database',
                'id': 'mock_database_1',
                'title': [{'plain_text': 'Learning Tasks'}],
                'created_time': datetime.utcnow().isoformat(),
                'last_edited_time': datetime.utcnow().isoformat()
            }
        ]
    
    def _get_mock_database(self, database_id: str) -> Dict:
        """Return mock database."""
        return {
            'object': 'database',
            'id': database_id,
            'title': [{'plain_text': 'Learning Tasks'}],
            'properties': {
                'Name': {'type': 'title'},
                'Status': {'type': 'select'},
                'Due Date': {'type': 'date'}
            },
            'created_time': datetime.utcnow().isoformat(),
            'last_edited_time': datetime.utcnow().isoformat()
        }
    
    def _get_mock_pages(self) -> List[Dict]:
        """Return mock pages."""
        return [
            {
                'object': 'page',
                'id': f'mock_page_{i}',
                'properties': {
                    'Name': {
                        'title': [{'plain_text': f'Task {i}'}]
                    },
                    'Status': {
                        'select': {'name': 'In Progress'}
                    }
                },
                'created_time': datetime.utcnow().isoformat(),
                'last_edited_time': datetime.utcnow().isoformat()
            }
            for i in range(1, 4)
        ]
    
    def _get_mock_page(self, properties: Dict) -> Dict:
        """Return mock created page."""
        return {
            'object': 'page',
            'id': 'mock_page_new',
            'properties': properties,
            'created_time': datetime.utcnow().isoformat(),
            'last_edited_time': datetime.utcnow().isoformat()
        }
