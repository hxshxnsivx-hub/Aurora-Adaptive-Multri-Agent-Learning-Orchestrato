"""
ElevenLabs API integration for text-to-speech generation.
"""

from typing import Dict, List, Optional
import logging
import base64

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class ElevenLabsClient:
    """Client for ElevenLabs Text-to-Speech API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize ElevenLabs client."""
        self.api_key = api_key or settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_voice_id = settings.ELEVENLABS_VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
    
    async def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_monolingual_v1",
        voice_settings: Optional[Dict] = None
    ) -> Optional[bytes]:
        """
        Convert text to speech.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (default: configured voice)
            model_id: Model ID to use
            voice_settings: Voice settings (stability, similarity_boost)
        
        Returns:
            Audio data as bytes or None
        """
        if not self.api_key:
            logger.warning("ElevenLabs API not configured, returning mock audio")
            return self._get_mock_audio()
        
        voice_id = voice_id or self.default_voice_id
        
        # Default voice settings
        if voice_settings is None:
            voice_settings = {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/text-to-speech/{voice_id}",
                    json={
                        "text": text,
                        "model_id": model_id,
                        "voice_settings": voice_settings
                    },
                    headers={
                        "xi-api-key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    return response.content
                else:
                    logger.error(f"ElevenLabs API error: {response.status_code}")
                    return self._get_mock_audio()
                    
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None
    
    async def get_voices(self) -> List[Dict]:
        """
        Get available voices.
        
        Returns:
            List of voice dictionaries
        """
        if not self.api_key:
            return self._get_mock_voices()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers={"xi-api-key": self.api_key},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("voices", [])
                else:
                    logger.error(f"ElevenLabs API error: {response.status_code}")
                    return self._get_mock_voices()
                    
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    async def get_voice_settings(self, voice_id: str) -> Optional[Dict]:
        """
        Get settings for a specific voice.
        
        Args:
            voice_id: Voice ID
        
        Returns:
            Voice settings dictionary or None
        """
        if not self.api_key:
            return {"stability": 0.5, "similarity_boost": 0.75}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/voices/{voice_id}/settings",
                    headers={"xi-api-key": self.api_key},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting voice settings: {e}")
            return None
    
    async def stream_text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_monolingual_v1"
    ):
        """
        Stream text-to-speech audio.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use
            model_id: Model ID to use
        
        Yields:
            Audio chunks as bytes
        """
        if not self.api_key:
            yield self._get_mock_audio()
            return
        
        voice_id = voice_id or self.default_voice_id
        
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/text-to-speech/{voice_id}/stream",
                    json={
                        "text": text,
                        "model_id": model_id,
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75
                        }
                    },
                    headers={
                        "xi-api-key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    timeout=60.0
                ) as response:
                    if response.status_code == 200:
                        async for chunk in response.aiter_bytes():
                            yield chunk
                    else:
                        logger.error(f"ElevenLabs stream error: {response.status_code}")
                        yield self._get_mock_audio()
                        
        except Exception as e:
            logger.error(f"Error streaming speech: {e}")
            yield self._get_mock_audio()
    
    def _get_mock_audio(self) -> bytes:
        """Return mock audio data (empty WAV file)."""
        # Minimal WAV file header (44 bytes) + 1 second of silence
        wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
        silence = b'\x00' * 44100  # 1 second of silence at 44.1kHz
        return wav_header + silence
    
    def _get_mock_voices(self) -> List[Dict]:
        """Return mock voice list."""
        return [
            {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "name": "Rachel",
                "category": "premade",
                "description": "Calm and professional"
            },
            {
                "voice_id": "AZnzlk1XvdvUeBnXmlld",
                "name": "Domi",
                "category": "premade",
                "description": "Strong and confident"
            }
        ]


# Singleton instance
elevenlabs_client = ElevenLabsClient()
