"""
OpenAI API integration for LLM and embeddings.
"""

from typing import Dict, List, Optional
import logging

from openai import AsyncOpenAI
from openai import OpenAIError

from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client."""
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = None
        if self.api_key:
            try:
                self.client = AsyncOpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
    
    async def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Create a chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (gpt-4, gpt-3.5-turbo, etc.)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text or None
        """
        if not self.client:
            logger.warning("OpenAI API not configured, returning mock response")
            return self._get_mock_completion(messages)
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_mock_completion(messages)
        except Exception as e:
            logger.error(f"Error creating chat completion: {e}")
            return None
    
    async def create_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small"
    ) -> Optional[List[float]]:
        """
        Create an embedding for text.
        
        Args:
            text: Text to embed
            model: Embedding model to use
        
        Returns:
            Embedding vector or None
        """
        if not self.client:
            logger.warning("OpenAI API not configured, returning mock embedding")
            return self._get_mock_embedding()
        
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=text
            )
            
            return response.data[0].embedding
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_mock_embedding()
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            return None
    
    async def create_embeddings_batch(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small"
    ) -> Optional[List[List[float]]]:
        """
        Create embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            model: Embedding model to use
        
        Returns:
            List of embedding vectors or None
        """
        if not self.client:
            return [self._get_mock_embedding() for _ in texts]
        
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=texts
            )
            
            return [item.embedding for item in response.data]
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return [self._get_mock_embedding() for _ in texts]
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            return None
    
    async def analyze_text(
        self,
        text: str,
        task: str = "summarize"
    ) -> Optional[str]:
        """
        Analyze text using GPT.
        
        Args:
            text: Text to analyze
            task: Analysis task (summarize, extract_keywords, assess_difficulty, etc.)
        
        Returns:
            Analysis result or None
        """
        prompts = {
            "summarize": f"Summarize the following text concisely:\n\n{text}",
            "extract_keywords": f"Extract key topics and concepts from this text:\n\n{text}",
            "assess_difficulty": f"Assess the difficulty level (beginner/intermediate/advanced) of this content:\n\n{text}",
            "generate_questions": f"Generate 3 study questions based on this content:\n\n{text}"
        }
        
        prompt = prompts.get(task, f"{task}:\n\n{text}")
        
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant for educational content analysis."},
            {"role": "user", "content": prompt}
        ]
        
        return await self.create_chat_completion(messages, model="gpt-3.5-turbo")
    
    async def generate_learning_path(
        self,
        topic: str,
        current_level: str,
        target_level: str,
        goals: List[str]
    ) -> Optional[Dict]:
        """
        Generate a learning path using GPT.
        
        Args:
            topic: Learning topic
            current_level: Current skill level
            target_level: Target skill level
            goals: Learning goals
        
        Returns:
            Learning path structure or None
        """
        prompt = f"""Generate a structured learning path for the following:

Topic: {topic}
Current Level: {current_level}
Target Level: {target_level}
Goals: {', '.join(goals)}

Provide a JSON structure with milestones, each containing:
- title
- description
- estimated_hours
- key_concepts
- recommended_resources (types)
"""
        
        messages = [
            {"role": "system", "content": "You are an expert educational path designer."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.create_chat_completion(messages, model="gpt-4", temperature=0.7)
        
        if response:
            try:
                import json
                return json.loads(response)
            except:
                return {"raw_response": response}
        
        return None
    
    def _get_mock_completion(self, messages: List[Dict]) -> str:
        """Return mock completion response."""
        last_message = messages[-1]["content"] if messages else ""
        return f"This is a mock response to: {last_message[:100]}..."
    
    def _get_mock_embedding(self) -> List[float]:
        """Return mock embedding vector (1536 dimensions for text-embedding-3-small)."""
        import random
        return [random.random() for _ in range(1536)]


# Singleton instance
openai_client = OpenAIClient()
