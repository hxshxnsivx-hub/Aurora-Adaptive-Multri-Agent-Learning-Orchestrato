"""
YouTube Data API integration for video resource discovery.
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings

logger = logging.getLogger(__name__)


class YouTubeClient:
    """Client for YouTube Data API v3."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize YouTube client."""
        self.api_key = api_key or settings.YOUTUBE_API_KEY
        self.service = None
        if self.api_key:
            try:
                self.service = build('youtube', 'v3', developerKey=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize YouTube client: {e}")
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 10,
        order: str = "relevance",
        video_duration: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for videos on YouTube.
        
        Args:
            query: Search query
            max_results: Maximum number of results (1-50)
            order: Sort order (relevance, date, rating, viewCount)
            video_duration: Filter by duration (short, medium, long)
        
        Returns:
            List of video metadata dictionaries
        """
        if not self.service:
            logger.warning("YouTube API not configured, returning mock data")
            return self._get_mock_videos(query, max_results)
        
        try:
            # Build search request
            search_params = {
                'q': query,
                'part': 'snippet',
                'type': 'video',
                'maxResults': min(max_results, 50),
                'order': order,
                'relevanceLanguage': 'en',
                'safeSearch': 'moderate'
            }
            
            if video_duration:
                search_params['videoDuration'] = video_duration
            
            # Execute search
            search_response = self.service.search().list(**search_params).execute()
            
            # Get video IDs
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            if not video_ids:
                return []
            
            # Get detailed video information
            videos_response = self.service.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            ).execute()
            
            # Parse and format results
            videos = []
            for item in videos_response.get('items', []):
                video = self._parse_video_item(item)
                videos.append(video)
            
            return videos
            
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            return self._get_mock_videos(query, max_results)
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return []
    
    async def get_video_details(self, video_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific video.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Video metadata dictionary or None
        """
        if not self.service:
            return self._get_mock_video_details(video_id)
        
        try:
            response = self.service.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()
            
            items = response.get('items', [])
            if items:
                return self._parse_video_item(items[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting video details: {e}")
            return None
    
    async def get_channel_videos(
        self,
        channel_id: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Get videos from a specific channel.
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of results
        
        Returns:
            List of video metadata dictionaries
        """
        if not self.service:
            return []
        
        try:
            # Get uploads playlist ID
            channel_response = self.service.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response.get('items'):
                return []
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            playlist_response = self.service.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            ).execute()
            
            video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response.get('items', [])]
            
            if not video_ids:
                return []
            
            # Get detailed video information
            videos_response = self.service.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            ).execute()
            
            return [self._parse_video_item(item) for item in videos_response.get('items', [])]
            
        except Exception as e:
            logger.error(f"Error getting channel videos: {e}")
            return []
    
    def _parse_video_item(self, item: Dict) -> Dict:
        """Parse YouTube API video item into standardized format."""
        snippet = item.get('snippet', {})
        statistics = item.get('statistics', {})
        content_details = item.get('contentDetails', {})
        
        return {
            'id': item.get('id'),
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'channel_title': snippet.get('channelTitle', ''),
            'channel_id': snippet.get('channelId', ''),
            'published_at': snippet.get('publishedAt', ''),
            'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
            'duration': self._parse_duration(content_details.get('duration', '')),
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
            'url': f"https://www.youtube.com/watch?v={item.get('id')}",
            'resource_type': 'video',
            'source_platform': 'youtube'
        }
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to minutes."""
        import re
        
        if not duration_str:
            return 0
        
        # Parse PT#H#M#S format
        hours = re.search(r'(\d+)H', duration_str)
        minutes = re.search(r'(\d+)M', duration_str)
        seconds = re.search(r'(\d+)S', duration_str)
        
        total_minutes = 0
        if hours:
            total_minutes += int(hours.group(1)) * 60
        if minutes:
            total_minutes += int(minutes.group(1))
        if seconds:
            total_minutes += 1  # Round up
        
        return total_minutes
    
    def _get_mock_videos(self, query: str, max_results: int) -> List[Dict]:
        """Return mock video data when API is not configured."""
        return [
            {
                'id': f'mock_video_{i}',
                'title': f'Learn {query} - Tutorial {i}',
                'description': f'Comprehensive tutorial on {query}',
                'channel_title': 'Tech Education Channel',
                'channel_id': 'mock_channel',
                'published_at': datetime.utcnow().isoformat(),
                'thumbnail_url': 'https://via.placeholder.com/480x360',
                'duration': 30 + (i * 5),
                'view_count': 10000 + (i * 1000),
                'like_count': 500 + (i * 50),
                'comment_count': 100 + (i * 10),
                'url': f'https://www.youtube.com/watch?v=mock_{i}',
                'resource_type': 'video',
                'source_platform': 'youtube'
            }
            for i in range(1, min(max_results + 1, 6))
        ]
    
    def _get_mock_video_details(self, video_id: str) -> Dict:
        """Return mock video details."""
        return {
            'id': video_id,
            'title': 'Sample Tutorial Video',
            'description': 'This is a sample video description',
            'channel_title': 'Tech Education',
            'channel_id': 'mock_channel',
            'published_at': datetime.utcnow().isoformat(),
            'thumbnail_url': 'https://via.placeholder.com/480x360',
            'duration': 45,
            'view_count': 50000,
            'like_count': 2500,
            'comment_count': 500,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'resource_type': 'video',
            'source_platform': 'youtube'
        }


# Singleton instance
youtube_client = YouTubeClient()
