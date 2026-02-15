"""
Resource Curator Agent for content ranking and quality assessment.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.agents.base import BaseAgent, AgentMessage, AgentState

logger = logging.getLogger(__name__)


class ResourceCuratorAgent(BaseAgent):
    """Agent responsible for curating and ranking educational resources."""
    
    def __init__(self):
        super().__init__(
            agent_id="resource_curator_agent",
            name="Resource Curator Agent"
        )
    
    async def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Process resource curation requests."""
        try:
            action = message.content.get("action")
            
            if action == "curate_resources":
                return await self._curate_resources(message, state)
            elif action == "rank_resources":
                return await self._rank_resources(message, state)
            elif action == "filter_resources":
                return await self._filter_resources(message, state)
            elif action == "assess_quality":
                return await self._assess_quality(message, state)
            else:
                return self._create_error_response(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error in ResourceCuratorAgent: {e}")
            return self._create_error_response(str(e))
    
    async def _curate_resources(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Curate resources for a specific milestone or topic."""
        milestone = message.content.get("milestone", {})
        user_preferences = message.content.get("user_preferences", {})
        
        # Get resources from research agent results
        raw_resources = message.content.get("raw_resources", [])
        
        # Curate and enhance resources
        curated = []
        for resource in raw_resources:
            enhanced = await self._enhance_resource(resource, milestone, user_preferences)
            if enhanced["quality_score"] >= 0.6:  # Minimum quality threshold
                curated.append(enhanced)
        
        # Rank by relevance and quality
        ranked = sorted(curated, key=lambda x: (x["relevance_score"] + x["quality_score"]) / 2, reverse=True)
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "curated_resources": ranked[:10],  # Top 10
                "total_curated": len(ranked),
                "average_quality": sum(r["quality_score"] for r in ranked) / len(ranked) if ranked else 0
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _rank_resources(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Rank resources by relevance and quality."""
        resources = message.content.get("resources", [])
        criteria = message.content.get("criteria", {})
        
        ranked = []
        for resource in resources:
            score = self._calculate_ranking_score(resource, criteria)
            resource["ranking_score"] = score
            ranked.append(resource)
        
        ranked.sort(key=lambda x: x["ranking_score"], reverse=True)
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={"ranked_resources": ranked},
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _filter_resources(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Filter resources based on criteria."""
        resources = message.content.get("resources", [])
        filters = message.content.get("filters", {})
        
        filtered = []
        for resource in resources:
            if self._matches_filters(resource, filters):
                filtered.append(resource)
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "filtered_resources": filtered,
                "original_count": len(resources),
                "filtered_count": len(filtered)
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _assess_quality(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Assess quality of a resource."""
        resource = message.content.get("resource", {})
        
        assessment = {
            "resource_id": resource.get("id"),
            "quality_score": self._calculate_quality_score(resource),
            "relevance_score": self._calculate_relevance_score(resource, message.content.get("topic", "")),
            "difficulty_match": self._assess_difficulty_match(resource, message.content.get("target_level", "intermediate")),
            "content_freshness": self._assess_freshness(resource),
            "engagement_metrics": self._assess_engagement(resource),
            "recommendation": self._generate_recommendation(resource)
        }
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content=assessment,
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _enhance_resource(self, resource: Dict, milestone: Dict, preferences: Dict) -> Dict:
        """Enhance resource with additional metadata and scores."""
        enhanced = resource.copy()
        
        enhanced["quality_score"] = self._calculate_quality_score(resource)
        enhanced["relevance_score"] = self._calculate_relevance_score(resource, milestone.get("title", ""))
        enhanced["difficulty_level"] = self._determine_difficulty(resource)
        enhanced["estimated_duration"] = self._estimate_duration(resource)
        enhanced["content_type_match"] = self._check_content_type_preference(resource, preferences)
        
        return enhanced
    
    def _calculate_quality_score(self, resource: Dict) -> float:
        """Calculate quality score for a resource."""
        score = 0.5  # Base score
        
        # Factor in engagement metrics
        if resource.get("views", 0) > 10000:
            score += 0.1
        if resource.get("rating", 0) > 4.5:
            score += 0.15
        if resource.get("stars", 0) > 1000:
            score += 0.1
        
        # Factor in recency
        published = resource.get("published_date")
        if published:
            try:
                pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
                days_old = (datetime.utcnow() - pub_date).days
                if days_old < 365:
                    score += 0.1
            except:
                pass
        
        # Factor in completeness
        if resource.get("description"):
            score += 0.05
        
        return min(score, 1.0)
    
    def _calculate_relevance_score(self, resource: Dict, topic: str) -> float:
        """Calculate relevance score for a resource."""
        score = 0.5
        
        title = resource.get("title", "").lower()
        description = resource.get("description", "").lower()
        topic_lower = topic.lower()
        
        # Check title relevance
        if topic_lower in title:
            score += 0.3
        
        # Check description relevance
        if topic_lower in description:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_ranking_score(self, resource: Dict, criteria: Dict) -> float:
        """Calculate overall ranking score."""
        quality_weight = criteria.get("quality_weight", 0.5)
        relevance_weight = criteria.get("relevance_weight", 0.3)
        recency_weight = criteria.get("recency_weight", 0.2)
        
        quality = resource.get("quality_score", 0.5)
        relevance = resource.get("relevance_score", 0.5)
        recency = self._calculate_recency_score(resource)
        
        return (quality * quality_weight + 
                relevance * relevance_weight + 
                recency * recency_weight)
    
    def _matches_filters(self, resource: Dict, filters: Dict) -> bool:
        """Check if resource matches filters."""
        # Check resource type
        if "resource_type" in filters:
            if resource.get("resource_type") not in filters["resource_type"]:
                return False
        
        # Check difficulty level
        if "difficulty_level" in filters:
            if resource.get("difficulty_level") not in filters["difficulty_level"]:
                return False
        
        # Check minimum quality
        if "min_quality" in filters:
            if resource.get("quality_score", 0) < filters["min_quality"]:
                return False
        
        return True
    
    def _determine_difficulty(self, resource: Dict) -> str:
        """Determine difficulty level of a resource."""
        title = resource.get("title", "").lower()
        description = resource.get("description", "").lower()
        
        if any(word in title or word in description for word in ["beginner", "intro", "basics", "fundamentals"]):
            return "beginner"
        elif any(word in title or word in description for word in ["advanced", "expert", "master"]):
            return "advanced"
        else:
            return "intermediate"
    
    def _estimate_duration(self, resource: Dict) -> int:
        """Estimate duration in minutes."""
        if "duration" in resource:
            return resource["duration"]
        
        resource_type = resource.get("resource_type", "article")
        
        duration_map = {
            "video": 30,
            "article": 15,
            "course": 120,
            "book": 300,
            "tutorial": 45
        }
        
        return duration_map.get(resource_type, 30)
    
    def _check_content_type_preference(self, resource: Dict, preferences: Dict) -> float:
        """Check if resource matches user's content type preferences."""
        preferred_types = preferences.get("preferred_content_types", [])
        resource_type = resource.get("resource_type", "")
        
        if resource_type in preferred_types:
            return 1.0
        return 0.5
    
    def _assess_difficulty_match(self, resource: Dict, target_level: str) -> float:
        """Assess how well resource difficulty matches target level."""
        resource_level = self._determine_difficulty(resource)
        
        level_map = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        resource_num = level_map.get(resource_level, 2)
        target_num = level_map.get(target_level, 2)
        
        diff = abs(resource_num - target_num)
        
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.7
        else:
            return 0.4
    
    def _assess_freshness(self, resource: Dict) -> float:
        """Assess content freshness."""
        published = resource.get("published_date")
        if not published:
            return 0.5
        
        try:
            pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
            days_old = (datetime.utcnow() - pub_date).days
            
            if days_old < 180:
                return 1.0
            elif days_old < 365:
                return 0.8
            elif days_old < 730:
                return 0.6
            else:
                return 0.4
        except:
            return 0.5
    
    def _assess_engagement(self, resource: Dict) -> Dict:
        """Assess engagement metrics."""
        return {
            "views": resource.get("views", 0),
            "rating": resource.get("rating", 0),
            "stars": resource.get("stars", 0),
            "engagement_score": self._calculate_engagement_score(resource)
        }
    
    def _calculate_engagement_score(self, resource: Dict) -> float:
        """Calculate engagement score."""
        score = 0.0
        
        views = resource.get("views", 0)
        if views > 100000:
            score += 0.4
        elif views > 10000:
            score += 0.3
        elif views > 1000:
            score += 0.2
        
        rating = resource.get("rating", 0)
        if rating > 4.5:
            score += 0.3
        elif rating > 4.0:
            score += 0.2
        elif rating > 3.5:
            score += 0.1
        
        stars = resource.get("stars", 0)
        if stars > 5000:
            score += 0.3
        elif stars > 1000:
            score += 0.2
        elif stars > 100:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_recency_score(self, resource: Dict) -> float:
        """Calculate recency score."""
        return self._assess_freshness(resource)
    
    def _generate_recommendation(self, resource: Dict) -> str:
        """Generate recommendation for a resource."""
        quality = resource.get("quality_score", 0.5)
        
        if quality >= 0.8:
            return "Highly recommended"
        elif quality >= 0.6:
            return "Recommended"
        else:
            return "Consider alternatives"
