"""
Goal Interpreter Agent for analyzing and interpreting user learning goals.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from app.agents.base import BaseAgent, AgentMessage, AgentState

logger = logging.getLogger(__name__)


class GoalInterpreterAgent(BaseAgent):
    """Agent responsible for interpreting user goals and requirements."""
    
    def __init__(self):
        super().__init__(
            agent_id="goal_interpreter_agent",
            name="Goal Interpreter Agent"
        )
    
    async def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Process goal interpretation requests."""
        try:
            action = message.content.get("action")
            
            if action == "interpret_goals":
                return await self._interpret_goals(message, state)
            elif action == "prioritize_goals":
                return await self._prioritize_goals(message, state)
            elif action == "validate_goals":
                return await self._validate_goals(message, state)
            else:
                return self._create_error_response(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error in GoalInterpreterAgent: {e}")
            return self._create_error_response(str(e))
    
    async def _interpret_goals(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Interpret user goals into actionable learning objectives."""
        raw_goals = message.content.get("goals", [])
        user_context = message.content.get("user_context", {})
        
        interpreted_goals = []
        for goal in raw_goals:
            interpreted = {
                "id": f"goal_{len(interpreted_goals) + 1}",
                "title": goal.get("title", ""),
                "description": goal.get("description", ""),
                "target_level": self._determine_target_level(goal, user_context),
                "estimated_duration": self._estimate_duration(goal),
                "prerequisites": self._identify_prerequisites(goal, user_context),
                "milestones": self._break_into_milestones(goal),
                "priority": goal.get("priority", "medium")
            }
            interpreted_goals.append(interpreted)
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "interpreted_goals": interpreted_goals,
                "total_estimated_hours": sum(g["estimated_duration"] for g in interpreted_goals)
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _prioritize_goals(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Prioritize goals based on urgency, dependencies, and user preferences."""
        goals = message.content.get("goals", [])
        
        # Sort by priority and deadline
        prioritized = sorted(
            goals,
            key=lambda g: (
                {"high": 0, "medium": 1, "low": 2}.get(g.get("priority", "medium"), 1),
                g.get("deadline", datetime.max.isoformat())
            )
        )
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={"prioritized_goals": prioritized},
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _validate_goals(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Validate goals for feasibility and completeness."""
        goals = message.content.get("goals", [])
        user_context = message.content.get("user_context", {})
        
        validation_results = []
        for goal in goals:
            is_valid, issues = self._check_goal_validity(goal, user_context)
            validation_results.append({
                "goal_id": goal.get("id"),
                "is_valid": is_valid,
                "issues": issues,
                "suggestions": self._generate_suggestions(goal, issues)
            })
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={"validation_results": validation_results},
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    def _determine_target_level(self, goal: Dict, user_context: Dict) -> str:
        """Determine target proficiency level for a goal."""
        current_level = user_context.get("skill_levels", {}).get(goal.get("topic"), 0.0)
        
        if current_level < 0.3:
            return "intermediate"
        elif current_level < 0.6:
            return "advanced"
        else:
            return "expert"
    
    def _estimate_duration(self, goal: Dict) -> int:
        """Estimate duration in hours for achieving a goal."""
        complexity = goal.get("complexity", "medium")
        
        duration_map = {
            "low": 20,
            "medium": 40,
            "high": 80
        }
        
        return duration_map.get(complexity, 40)
    
    def _identify_prerequisites(self, goal: Dict, user_context: Dict) -> List[str]:
        """Identify prerequisites for a goal."""
        # Simplified prerequisite identification
        topic = goal.get("topic", "")
        prerequisites = []
        
        # Add basic prerequisites based on topic
        if "advanced" in topic.lower():
            prerequisites.append(f"Basic {topic.replace('Advanced', '').strip()}")
        
        return prerequisites
    
    def _break_into_milestones(self, goal: Dict) -> List[Dict]:
        """Break goal into smaller milestones."""
        duration = self._estimate_duration(goal)
        num_milestones = max(3, duration // 15)  # One milestone per ~15 hours
        
        milestones = []
        for i in range(num_milestones):
            milestones.append({
                "order": i + 1,
                "title": f"Milestone {i + 1}",
                "estimated_hours": duration // num_milestones
            })
        
        return milestones
    
    def _check_goal_validity(self, goal: Dict, user_context: Dict) -> tuple:
        """Check if a goal is valid and achievable."""
        issues = []
        
        if not goal.get("title"):
            issues.append("Goal title is missing")
        
        if not goal.get("description"):
            issues.append("Goal description is missing")
        
        deadline = goal.get("deadline")
        if deadline:
            deadline_date = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
            if deadline_date < datetime.utcnow():
                issues.append("Deadline is in the past")
        
        return len(issues) == 0, issues
    
    def _generate_suggestions(self, goal: Dict, issues: List[str]) -> List[str]:
        """Generate suggestions for improving a goal."""
        suggestions = []
        
        if "title is missing" in str(issues):
            suggestions.append("Add a clear, specific title for your goal")
        
        if "description is missing" in str(issues):
            suggestions.append("Provide a detailed description of what you want to achieve")
        
        if "Deadline is in the past" in str(issues):
            suggestions.append("Set a realistic future deadline")
        
        return suggestions
