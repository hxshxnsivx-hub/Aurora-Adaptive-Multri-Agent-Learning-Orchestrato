"""
User Profile Agent for skill tracking and proficiency management.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.agents.base import BaseAgent, AgentMessage, AgentState
from app.core.database import AsyncSession
from app.models.user import UserProfile
from sqlalchemy import select

logger = logging.getLogger(__name__)


class UserProfileAgent(BaseAgent):
    """Agent responsible for tracking user skills and proficiency levels."""
    
    def __init__(self):
        super().__init__(
            agent_id="user_profile_agent",
            name="User Profile Agent"
        )
    
    async def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Process user profile related requests."""
        try:
            action = message.content.get("action")
            
            if action == "get_profile":
                return await self._get_user_profile(message, state)
            elif action == "update_skills":
                return await self._update_skill_levels(message, state)
            elif action == "assess_proficiency":
                return await self._assess_proficiency(message, state)
            else:
                return self._create_error_response(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error in UserProfileAgent: {e}")
            return self._create_error_response(str(e))
    
    async def _get_user_profile(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Retrieve user profile with skill levels."""
        user_id = message.content.get("user_id")
        
        # Simulate profile retrieval
        profile_data = {
            "user_id": user_id,
            "skill_levels": state.context.get("skill_levels", {}),
            "learning_preferences": state.context.get("preferences", {}),
            "goals": state.context.get("goals", [])
        }
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={"profile": profile_data},
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _update_skill_levels(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Update user skill levels based on progress."""
        user_id = message.content.get("user_id")
        skill_updates = message.content.get("skill_updates", {})
        
        # Update skill levels in state
        current_skills = state.context.get("skill_levels", {})
        current_skills.update(skill_updates)
        state.context["skill_levels"] = current_skills
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "updated_skills": current_skills,
                "message": "Skill levels updated successfully"
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _assess_proficiency(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Assess user proficiency based on assessment results."""
        assessment_results = message.content.get("assessment_results", {})
        
        # Calculate proficiency levels (0.0 to 1.0)
        proficiency_levels = {}
        for topic, score in assessment_results.items():
            # Normalize score to 0-1 range
            proficiency_levels[topic] = min(max(score / 100.0, 0.0), 1.0)
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "proficiency_levels": proficiency_levels,
                "confidence": 0.85
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
