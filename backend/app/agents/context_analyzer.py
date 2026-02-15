"""
Context Analyzer Agent - analyzes user context and maintains state.
"""

from typing import Dict, Any, List, Optional
from app.agents.base import BaseAgent, AgentMessage
import logging

logger = logging.getLogger(__name__)


class ContextAnalyzer(BaseAgent):
    """Agent responsible for analyzing user context and maintaining comprehensive state."""
    
    def __init__(self):
        super().__init__("context_analyzer", "Context Analyzer")
        self.user_contexts: Dict[str, Dict] = {}
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process context-related messages."""
        self.add_message_to_history(message)
        
        if message.message_type == "analyze_context":
            result = await self._analyze_user_context(message.content)
            return await self.send_message(
                message.sender,
                "context_analysis_result",
                result
            )
        elif message.message_type == "update_context":
            await self._update_user_context(message.content)
            return await self.send_message(
                message.sender,
                "context_updated",
                {"status": "success"}
            )
        
        return None
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute context analysis tasks."""
        task_type = task.get("type")
        
        self.update_state("processing", task_type)
        
        try:
            if task_type == "analyze_user_context":
                return await self._analyze_user_context(task)
            elif task_type == "get_user_context":
                return await self._get_user_context(task)
            elif task_type == "update_progress_context":
                return await self._update_progress_context(task)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
        finally:
            self.update_state("idle")
    
    async def _analyze_user_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze comprehensive user context including skills, preferences, and progress."""
        user_profile = data.get("user_profile", {})
        goals = data.get("goals", [])
        user_id = user_profile.get("user_id") or data.get("user_id")
        
        if not user_id:
            raise ValueError("User ID is required for context analysis")
        
        # Analyze skill levels and gaps
        skill_analysis = await self._analyze_skill_gaps(user_profile, goals)
        
        # Analyze learning preferences and patterns
        preference_analysis = await self._analyze_learning_preferences(user_profile)
        
        # Analyze availability and time constraints
        availability_analysis = await self._analyze_availability(user_profile)
        
        # Analyze goal complexity and feasibility
        goal_analysis = await self._analyze_goals(goals, user_profile)
        
        # Create comprehensive context
        context = {
            "user_id": user_id,
            "skill_analysis": skill_analysis,
            "preference_analysis": preference_analysis,
            "availability_analysis": availability_analysis,
            "goal_analysis": goal_analysis,
            "recommended_approach": await self._recommend_learning_approach(
                skill_analysis, preference_analysis, goal_analysis
            ),
            "context_confidence": self._calculate_context_confidence(user_profile),
            "analysis_timestamp": self.state.last_updated
        }
        
        # Store context for future reference
        self.user_contexts[user_id] = context
        
        return context
    
    async def _analyze_skill_gaps(self, user_profile: Dict, goals: List[Dict]) -> Dict[str, Any]:
        """Analyze skill gaps between current level and goal requirements."""
        current_skills = user_profile.get("skill_levels", {})
        
        # Extract required skills from goals
        required_skills = {}
        for goal in goals:
            # TODO: Use NLP to extract required skills from goal descriptions
            # For now, use simple keyword matching
            goal_skills = goal.get("required_skills", {})
            for skill, level in goal_skills.items():
                required_skills[skill] = max(required_skills.get(skill, 0), level)
        
        # Calculate skill gaps
        skill_gaps = {}
        for skill, required_level in required_skills.items():
            current_level = current_skills.get(skill, 0.0)
            gap = max(0, required_level - current_level)
            skill_gaps[skill] = {
                "current_level": current_level,
                "required_level": required_level,
                "gap": gap,
                "priority": "high" if gap > 0.5 else "medium" if gap > 0.2 else "low"
            }
        
        return {
            "current_skills": current_skills,
            "required_skills": required_skills,
            "skill_gaps": skill_gaps,
            "total_gap_score": sum(gap["gap"] for gap in skill_gaps.values()),
            "critical_gaps": [skill for skill, gap in skill_gaps.items() if gap["gap"] > 0.5]
        }
    
    async def _analyze_learning_preferences(self, user_profile: Dict) -> Dict[str, Any]:
        """Analyze user learning preferences and patterns."""
        preferences = user_profile.get("learning_preferences", {})
        
        return {
            "preferred_content_types": preferences.get("preferred_content_types", ["video", "article"]),
            "learning_pace": preferences.get("learning_pace", "moderate"),
            "difficulty_preference": preferences.get("difficulty_preference", "adaptive"),
            "session_duration_preference": preferences.get("session_duration_preference", 60),
            "interaction_style": preferences.get("interaction_style", "guided"),
            "feedback_frequency": preferences.get("feedback_frequency", "regular")
        }
    
    async def _analyze_availability(self, user_profile: Dict) -> Dict[str, Any]:
        """Analyze user availability and time constraints."""
        schedule = user_profile.get("availability_schedule", {})
        timezone = user_profile.get("timezone", "UTC")
        
        # Calculate total available hours per week
        total_hours = 0
        for day, slots in schedule.items():
            for slot in slots:
                total_hours += slot.get("end", 0) - slot.get("start", 0)
        
        # Identify peak availability periods
        peak_periods = self._identify_peak_periods(schedule)
        
        return {
            "total_weekly_hours": total_hours,
            "timezone": timezone,
            "schedule": schedule,
            "peak_periods": peak_periods,
            "consistency_score": self._calculate_schedule_consistency(schedule),
            "flexibility_score": self._calculate_schedule_flexibility(schedule)
        }
    
    async def _analyze_goals(self, goals: List[Dict], user_profile: Dict) -> Dict[str, Any]:
        """Analyze learning goals for complexity and feasibility."""
        goal_analysis = []
        
        for goal in goals:
            analysis = {
                "goal": goal,
                "complexity": self._assess_goal_complexity(goal),
                "feasibility": self._assess_goal_feasibility(goal, user_profile),
                "estimated_duration": self._estimate_goal_duration(goal),
                "prerequisites": self._identify_prerequisites(goal),
                "priority": goal.get("priority", "medium")
            }
            goal_analysis.append(analysis)
        
        return {
            "goals": goal_analysis,
            "total_estimated_duration": sum(g["estimated_duration"] for g in goal_analysis),
            "complexity_distribution": self._calculate_complexity_distribution(goal_analysis),
            "recommended_order": self._recommend_goal_order(goal_analysis)
        }
    
    async def _recommend_learning_approach(
        self, 
        skill_analysis: Dict, 
        preference_analysis: Dict, 
        goal_analysis: Dict
    ) -> Dict[str, Any]:
        """Recommend optimal learning approach based on analysis."""
        # Determine recommended path structure
        if skill_analysis["total_gap_score"] > 2.0:
            approach = "foundational"  # Focus on building strong foundations
        elif len(goal_analysis["goals"]) > 3:
            approach = "parallel"  # Work on multiple goals simultaneously
        else:
            approach = "sequential"  # Focus on one goal at a time
        
        # Recommend pacing
        available_hours = preference_analysis.get("session_duration_preference", 60) * 5  # Assume 5 sessions per week
        total_duration = goal_analysis["total_estimated_duration"]
        
        if available_hours >= total_duration / 8:  # Can complete in 8 weeks
            pacing = "intensive"
        elif available_hours >= total_duration / 16:  # Can complete in 16 weeks
            pacing = "moderate"
        else:
            pacing = "relaxed"
        
        return {
            "approach": approach,
            "pacing": pacing,
            "recommended_session_duration": preference_analysis["session_duration_preference"],
            "recommended_frequency": self._recommend_session_frequency(available_hours),
            "focus_areas": skill_analysis["critical_gaps"][:3],  # Top 3 critical gaps
            "learning_style_adaptations": self._recommend_style_adaptations(preference_analysis)
        }
    
    def _calculate_context_confidence(self, user_profile: Dict) -> float:
        """Calculate confidence score for context analysis."""
        confidence_factors = []
        
        # Skill data completeness
        skills = user_profile.get("skill_levels", {})
        confidence_factors.append(min(1.0, len(skills) / 10))  # Assume 10 skills is comprehensive
        
        # Preference data completeness
        preferences = user_profile.get("learning_preferences", {})
        confidence_factors.append(min(1.0, len(preferences) / 6))  # 6 key preferences
        
        # Schedule data completeness
        schedule = user_profile.get("availability_schedule", {})
        confidence_factors.append(min(1.0, len(schedule) / 7))  # 7 days of week
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _identify_peak_periods(self, schedule: Dict) -> List[Dict]:
        """Identify peak availability periods."""
        # TODO: Implement peak period identification
        return []
    
    def _calculate_schedule_consistency(self, schedule: Dict) -> float:
        """Calculate schedule consistency score."""
        # TODO: Implement consistency calculation
        return 0.8
    
    def _calculate_schedule_flexibility(self, schedule: Dict) -> float:
        """Calculate schedule flexibility score."""
        # TODO: Implement flexibility calculation
        return 0.7
    
    def get_capabilities(self) -> List[str]:
        """Return context analyzer capabilities."""
        return [
            "user_context_analysis",
            "skill_gap_analysis",
            "preference_analysis",
            "availability_analysis",
            "goal_feasibility_assessment",
            "learning_approach_recommendation"
        ]