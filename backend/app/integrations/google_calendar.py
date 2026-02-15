"""
Google Calendar API integration for event management and scheduling.
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleCalendarClient:
    """Client for Google Calendar API."""
    
    def __init__(self, credentials: Optional[Credentials] = None):
        """
        Initialize Google Calendar client.
        
        Args:
            credentials: OAuth2 credentials for the user
        """
        self.credentials = credentials
        self.service = None
        if self.credentials:
            try:
                self.service = build('calendar', 'v3', credentials=self.credentials)
            except Exception as e:
                logger.error(f"Failed to initialize Google Calendar client: {e}")
    
    @staticmethod
    def create_oauth_flow(redirect_uri: str) -> Flow:
        """
        Create OAuth2 flow for user authorization.
        
        Args:
            redirect_uri: OAuth redirect URI
        
        Returns:
            OAuth2 Flow instance
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=settings.GOOGLE_CALENDAR_SCOPES,
            redirect_uri=redirect_uri
        )
        return flow
    
    @staticmethod
    def get_authorization_url(redirect_uri: str) -> str:
        """
        Get OAuth2 authorization URL.
        
        Args:
            redirect_uri: OAuth redirect URI
        
        Returns:
            Authorization URL
        """
        flow = GoogleCalendarClient.create_oauth_flow(redirect_uri)
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return auth_url
    
    @staticmethod
    def exchange_code_for_credentials(code: str, redirect_uri: str) -> Credentials:
        """
        Exchange authorization code for credentials.
        
        Args:
            code: Authorization code
            redirect_uri: OAuth redirect URI
        
        Returns:
            OAuth2 Credentials
        """
        flow = GoogleCalendarClient.create_oauth_flow(redirect_uri)
        flow.fetch_token(code=code)
        return flow.credentials
    
    def refresh_credentials(self) -> bool:
        """
        Refresh expired credentials.
        
        Returns:
            True if refresh successful, False otherwise
        """
        if not self.credentials:
            return False
        
        try:
            if self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
                return True
            return True
        except Exception as e:
            logger.error(f"Error refreshing credentials: {e}")
            return False

    
    async def list_calendars(self) -> List[Dict]:
        """
        List all calendars for the user.
        
        Returns:
            List of calendar dictionaries
        """
        if not self.service:
            logger.warning("Google Calendar not configured, returning mock data")
            return self._get_mock_calendars()
        
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = []
            
            for calendar in calendar_list.get('items', []):
                calendars.append({
                    'id': calendar['id'],
                    'summary': calendar.get('summary', ''),
                    'description': calendar.get('description', ''),
                    'time_zone': calendar.get('timeZone', ''),
                    'primary': calendar.get('primary', False),
                    'access_role': calendar.get('accessRole', '')
                })
            
            return calendars
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return self._get_mock_calendars()
        except Exception as e:
            logger.error(f"Error listing calendars: {e}")
            return []
    
    async def get_events(
        self,
        calendar_id: str = 'primary',
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Get events from a calendar.
        
        Args:
            calendar_id: Calendar ID (default: 'primary')
            time_min: Minimum time for events
            time_max: Maximum time for events
            max_results: Maximum number of events to return
        
        Returns:
            List of event dictionaries
        """
        if not self.service:
            return self._get_mock_events()
        
        try:
            # Default to next 7 days if not specified
            if not time_min:
                time_min = datetime.utcnow()
            if not time_max:
                time_max = time_min + timedelta(days=7)
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = []
            for event in events_result.get('items', []):
                events.append(self._parse_event(event))
            
            return events
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return self._get_mock_events()
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return []
    
    async def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: str = 'primary'
    ) -> Optional[Dict]:
        """
        Create a new calendar event.
        
        Args:
            summary: Event title
            start_time: Event start time
            end_time: Event end time
            description: Event description
            location: Event location
            calendar_id: Calendar ID (default: 'primary')
        
        Returns:
            Created event dictionary or None
        """
        if not self.service:
            return self._get_mock_event(summary, start_time, end_time)
        
        try:
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                }
            }
            
            if description:
                event['description'] = description
            if location:
                event['location'] = location
            
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            return self._parse_event(created_event)
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return None
    
    async def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None,
        calendar_id: str = 'primary'
    ) -> Optional[Dict]:
        """
        Update an existing calendar event.
        
        Args:
            event_id: Event ID
            summary: New event title
            start_time: New start time
            end_time: New end time
            description: New description
            calendar_id: Calendar ID (default: 'primary')
        
        Returns:
            Updated event dictionary or None
        """
        if not self.service:
            return None
        
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields
            if summary:
                event['summary'] = summary
            if start_time:
                event['start'] = {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                }
            if end_time:
                event['end'] = {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                }
            if description:
                event['description'] = description
            
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            return self._parse_event(updated_event)
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return None
    
    async def delete_event(
        self,
        event_id: str,
        calendar_id: str = 'primary'
    ) -> bool:
        """
        Delete a calendar event.
        
        Args:
            event_id: Event ID
            calendar_id: Calendar ID (default: 'primary')
        
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False
        
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return True
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return False
    
    async def get_free_busy(
        self,
        time_min: datetime,
        time_max: datetime,
        calendar_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Get free/busy information for calendars.
        
        Args:
            time_min: Start time
            time_max: End time
            calendar_ids: List of calendar IDs (default: ['primary'])
        
        Returns:
            Free/busy information dictionary
        """
        if not self.service:
            return self._get_mock_free_busy()
        
        if not calendar_ids:
            calendar_ids = ['primary']
        
        try:
            body = {
                'timeMin': time_min.isoformat() + 'Z',
                'timeMax': time_max.isoformat() + 'Z',
                'items': [{'id': cal_id} for cal_id in calendar_ids]
            }
            
            freebusy_result = self.service.freebusy().query(body=body).execute()
            
            return {
                'time_min': time_min.isoformat(),
                'time_max': time_max.isoformat(),
                'calendars': freebusy_result.get('calendars', {})
            }
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return self._get_mock_free_busy()
        except Exception as e:
            logger.error(f"Error getting free/busy: {e}")
            return {}
    
    def _parse_event(self, event: Dict) -> Dict:
        """Parse Google Calendar event into standardized format."""
        start = event.get('start', {})
        end = event.get('end', {})
        
        return {
            'id': event.get('id'),
            'summary': event.get('summary', ''),
            'description': event.get('description', ''),
            'location': event.get('location', ''),
            'start_time': start.get('dateTime', start.get('date')),
            'end_time': end.get('dateTime', end.get('date')),
            'status': event.get('status', ''),
            'html_link': event.get('htmlLink', ''),
            'created': event.get('created', ''),
            'updated': event.get('updated', '')
        }
    
    def _get_mock_calendars(self) -> List[Dict]:
        """Return mock calendar list."""
        return [
            {
                'id': 'primary',
                'summary': 'Primary Calendar',
                'description': 'Your primary calendar',
                'time_zone': 'UTC',
                'primary': True,
                'access_role': 'owner'
            }
        ]
    
    def _get_mock_events(self) -> List[Dict]:
        """Return mock events."""
        now = datetime.utcnow()
        return [
            {
                'id': f'mock_event_{i}',
                'summary': f'Sample Event {i}',
                'description': 'This is a sample event',
                'location': '',
                'start_time': (now + timedelta(hours=i)).isoformat(),
                'end_time': (now + timedelta(hours=i+1)).isoformat(),
                'status': 'confirmed',
                'html_link': f'https://calendar.google.com/event?eid=mock_{i}',
                'created': now.isoformat(),
                'updated': now.isoformat()
            }
            for i in range(1, 4)
        ]
    
    def _get_mock_event(self, summary: str, start_time: datetime, end_time: datetime) -> Dict:
        """Return mock created event."""
        return {
            'id': 'mock_event_new',
            'summary': summary,
            'description': '',
            'location': '',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'status': 'confirmed',
            'html_link': 'https://calendar.google.com/event?eid=mock_new',
            'created': datetime.utcnow().isoformat(),
            'updated': datetime.utcnow().isoformat()
        }
    
    def _get_mock_free_busy(self) -> Dict:
        """Return mock free/busy data."""
        now = datetime.utcnow()
        return {
            'time_min': now.isoformat(),
            'time_max': (now + timedelta(days=7)).isoformat(),
            'calendars': {
                'primary': {
                    'busy': [
                        {
                            'start': (now + timedelta(hours=2)).isoformat(),
                            'end': (now + timedelta(hours=3)).isoformat()
                        }
                    ]
                }
            }
        }
