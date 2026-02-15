"""
External API integrations for the Adaptive Learning Platform.
"""

from app.integrations.youtube import youtube_client, YouTubeClient
from app.integrations.github import github_client, GitHubClient
from app.integrations.tavily import tavily_client, TavilyClient
from app.integrations.elevenlabs import elevenlabs_client, ElevenLabsClient
from app.integrations.openai_client import openai_client, OpenAIClient
from app.integrations.google_calendar import GoogleCalendarClient
from app.integrations.notion import NotionClient

__all__ = [
    'youtube_client',
    'YouTubeClient',
    'github_client',
    'GitHubClient',
    'tavily_client',
    'TavilyClient',
    'elevenlabs_client',
    'ElevenLabsClient',
    'openai_client',
    'OpenAIClient',
    'GoogleCalendarClient',
    'NotionClient',
]
