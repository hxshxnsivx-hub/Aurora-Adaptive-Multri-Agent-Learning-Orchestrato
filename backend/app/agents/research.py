"""
Research Agent for content discovery across multiple platforms.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.agents.base import BaseAgent, AgentMessage, AgentState
from app.integrations import youtube_client, github_client, tavily_client

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Agent responsible for discovering and researching learning content."""
    
    def __init__(self):
        super().__init__(
            agent_id="research_agent",
            name="Research Agent"
        )
    
    async def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Process research requests."""
        try:
            action = message.content.get("action")
            
            if action == "search_content":
                return await self._search_content(message, state)
            elif action == "deep_research":
                return await self._deep_research(message, state)
            elif action == "validate_sources":
                return await self._validate_sources(message, state)
            else:
                return self._create_error_response(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error in ResearchAgent: {e}")
            return self._create_error_response(str(e))
    
    async def _search_content(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Search for learning content across platforms."""
        query = message.content.get("query", "")
        platforms = message.content.get("platforms", ["youtube", "github", "web"])
        
        results = {
            "youtube": await self._search_youtube(query) if "youtube" in platforms else [],
            "github": await self._search_github(query) if "github" in platforms else [],
            "web": await self._search_web(query) if "web" in platforms else []
        }
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={"results": results, "total_found": sum(len(v) for v in results.values())},
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _deep_research(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Conduct deep research on a topic."""
        topic = message.content.get("topic", "")
        depth = message.content.get("depth", "intermediate")
        
        research_data = {
            "topic": topic,
            "key_concepts": self._extract_key_concepts(topic),
            "recommended_resources": await self._find_comprehensive_resources(topic, depth),
            "learning_path_suggestions": self._suggest_learning_sequence(topic),
            "prerequisites": self._identify_prerequisites(topic)
        }
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content=research_data,
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _validate_sources(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Validate quality and reliability of sources."""
        sources = message.content.get("sources", [])
        
        validated = []
        for source in sources:
            validation = {
                "source": source,
                "is_valid": True,
                "quality_score": self._calculate_quality_score(source),
                "reliability": self._assess_reliability(source),
                "issues": []
            }
            validated.append(validation)
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={"validated_sources": validated},
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _search_youtube(self, query: str) -> List[Dict]:
        """Search YouTube for educational content."""
        try:
            videos = await youtube_client.search_videos(
                query=query,
                max_results=10,
                order="relevance",
                video_duration="medium"
            )
            return videos
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return []
    
    async def _search_github(self, query: str) -> List[Dict]:
        """Search GitHub for repositories and documentation."""
        try:
            repos = await github_client.search_repositories(
                query=query,
                sort="stars",
                max_results=10
            )
            return repos
        except Exception as e:
            logger.error(f"Error searching GitHub: {e}")
            return []
    
    async def _search_web(self, query: str) -> List[Dict]:
        """Search web for articles and documentation."""
        try:
            results = await tavily_client.search(
                query=query,
                search_depth="basic",
                max_results=10
            )
            return results
        except Exception as e:
            logger.error(f"Error searching web: {e}")
            return []
    
    def _extract_key_concepts(self, topic: str) -> List[str]:
        """Extract key concepts from a topic."""
        # Simplified concept extraction
        return [f"{topic} basics", f"{topic} advanced", f"{topic} best practices"]
    
    async def _find_comprehensive_resources(self, topic: str, depth: str) -> List[Dict]:
        """Find comprehensive resources for a topic."""
        return [
            {"type": "video", "title": f"{topic} Tutorial", "difficulty": depth},
            {"type": "article", "title": f"{topic} Guide", "difficulty": depth},
            {"type": "course", "title": f"Master {topic}", "difficulty": depth}
        ]
    
    def _suggest_learning_sequence(self, topic: str) -> List[str]:
        """Suggest optimal learning sequence."""
        return [
            f"1. Introduction to {topic}",
            f"2. {topic} Fundamentals",
            f"3. Practical {topic} Applications",
            f"4. Advanced {topic} Techniques"
        ]
    
    def _identify_prerequisites(self, topic: str) -> List[str]:
        """Identify prerequisites for a topic."""
        return [f"Basic programming", f"Problem solving"]
    
    def _calculate_quality_score(self, source: Dict) -> float:
        """Calculate quality score for a source."""
        score = 0.7  # Base score
        
        if source.get("views", 0) > 10000:
            score += 0.1
        if source.get("rating", 0) > 4.5:
            score += 0.1
        if source.get("stars", 0) > 1000:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_reliability(self, source: Dict) -> str:
        """Assess reliability of a source."""
        quality = self._calculate_quality_score(source)
        
        if quality >= 0.8:
            return "high"
        elif quality >= 0.6:
            return "medium"
        else:
            return "low"
