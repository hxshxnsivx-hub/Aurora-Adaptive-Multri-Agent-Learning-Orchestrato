"""
Schedule Optimizer Agent for time management and task scheduling.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from app.agents.base import BaseAgent, AgentMessage, AgentState

logger = logging.getLogger(__name__)


class ScheduleOptimizerAgent(BaseAgent):
    """Agent responsible for optimizing learning schedules based on user availability."""
    
    def __init__(self):
        super().__init__(
            agent_id="schedule_optimizer_agent",
            name="Schedule Optimizer Agent"
        )
    
    async def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Process schedule optimization requests."""
        try:
            action = message.content.get("action")
            
            if action == "optimize_schedule":
                return await self._optimize_schedule(message, state)
            elif action == "reschedule_tasks":
                return await self._reschedule_tasks(message, state)
            elif action == "check_availability":
                return await self._check_availability(message, state)
            elif action == "suggest_study_times":
                return await self._suggest_study_times(message, state)
            else:
                return self._create_error_response(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error in ScheduleOptimizerAgent: {e}")
            return self._create_error_response(str(e))
    
    async def _optimize_schedule(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Optimize learning schedule based on availability and goals."""
        learning_path = message.content.get("learning_path", {})
        availability = message.content.get("availability", {})
        preferences = message.content.get("preferences", {})
        
        # Calculate optimal schedule
        optimized_schedule = self._calculate_optimal_schedule(
            learning_path,
            availability,
            preferences
        )
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "optimized_schedule": optimized_schedule,
                "total_hours": sum(task["duration"] for task in optimized_schedule),
                "completion_date": self._estimate_completion_date(optimized_schedule)
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _reschedule_tasks(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Reschedule tasks when user falls behind or availability changes."""
        current_schedule = message.content.get("current_schedule", [])
        new_availability = message.content.get("new_availability", {})
        reason = message.content.get("reason", "user_request")
        
        # Reschedule tasks
        rescheduled = self._reschedule_with_constraints(
            current_schedule,
            new_availability,
            reason
        )
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "rescheduled_tasks": rescheduled,
                "changes_made": len(rescheduled),
                "new_completion_date": self._estimate_completion_date(rescheduled)
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _check_availability(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Check user availability for a specific time slot."""
        requested_time = message.content.get("requested_time")
        duration = message.content.get("duration", 60)  # minutes
        availability = message.content.get("availability", {})
        
        is_available = self._is_time_slot_available(
            requested_time,
            duration,
            availability
        )
        
        alternative_slots = []
        if not is_available:
            alternative_slots = self._find_alternative_slots(
                requested_time,
                duration,
                availability
            )
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "is_available": is_available,
                "alternative_slots": alternative_slots
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _suggest_study_times(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Suggest optimal study times based on user patterns and preferences."""
        user_patterns = message.content.get("user_patterns", {})
        preferences = message.content.get("preferences", {})
        
        suggestions = self._generate_study_time_suggestions(
            user_patterns,
            preferences
        )
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={"suggested_times": suggestions},
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    def _calculate_optimal_schedule(
        self,
        learning_path: Dict,
        availability: Dict,
        preferences: Dict
    ) -> List[Dict]:
        """Calculate optimal schedule for learning path."""
        schedule = []
        milestones = learning_path.get("milestones", [])
        
        current_date = datetime.utcnow()
        
        for milestone in milestones:
            tasks = milestone.get("tasks", [])
            for task in tasks:
                # Find next available slot
                scheduled_time = self._find_next_available_slot(
                    current_date,
                    task.get("estimated_minutes", 60),
                    availability,
                    preferences
                )
                
                schedule.append({
                    "task_id": task.get("id"),
                    "task_title": task.get("title"),
                    "scheduled_time": scheduled_time.isoformat(),
                    "duration": task.get("estimated_minutes", 60),
                    "milestone_id": milestone.get("id")
                })
                
                current_date = scheduled_time + timedelta(minutes=task.get("estimated_minutes", 60))
        
        return schedule
    
    def _reschedule_with_constraints(
        self,
        current_schedule: List[Dict],
        new_availability: Dict,
        reason: str
    ) -> List[Dict]:
        """Reschedule tasks with new constraints."""
        rescheduled = []
        current_date = datetime.utcnow()
        
        for task in current_schedule:
            scheduled_time = datetime.fromisoformat(task["scheduled_time"])
            
            # If task is in the past or conflicts with new availability, reschedule
            if scheduled_time < current_date or not self._is_time_slot_available(
                scheduled_time,
                task["duration"],
                new_availability
            ):
                new_time = self._find_next_available_slot(
                    current_date,
                    task["duration"],
                    new_availability,
                    {}
                )
                task["scheduled_time"] = new_time.isoformat()
                task["rescheduled"] = True
                task["reschedule_reason"] = reason
            
            rescheduled.append(task)
        
        return rescheduled
    
    def _is_time_slot_available(
        self,
        requested_time: datetime,
        duration: int,
        availability: Dict
    ) -> bool:
        """Check if a time slot is available."""
        day_of_week = requested_time.strftime("%A").lower()
        hour = requested_time.hour
        
        day_availability = availability.get(day_of_week, [])
        
        for slot in day_availability:
            if slot["start"] <= hour < slot["end"]:
                return True
        
        return False
    
    def _find_next_available_slot(
        self,
        start_date: datetime,
        duration: int,
        availability: Dict,
        preferences: Dict
    ) -> datetime:
        """Find the next available time slot."""
        current = start_date
        max_days_ahead = 30
        
        for _ in range(max_days_ahead):
            day_of_week = current.strftime("%A").lower()
            day_availability = availability.get(day_of_week, [])
            
            for slot in day_availability:
                slot_time = current.replace(hour=slot["start"], minute=0, second=0)
                if slot_time > start_date:
                    return slot_time
            
            current += timedelta(days=1)
        
        # Fallback: return next day at 9 AM
        return start_date + timedelta(days=1, hours=9)
    
    def _find_alternative_slots(
        self,
        requested_time: datetime,
        duration: int,
        availability: Dict
    ) -> List[Dict]:
        """Find alternative time slots."""
        alternatives = []
        current = requested_time
        
        for _ in range(7):  # Check next 7 days
            day_of_week = current.strftime("%A").lower()
            day_availability = availability.get(day_of_week, [])
            
            for slot in day_availability:
                slot_time = current.replace(hour=slot["start"], minute=0)
                if slot_time > requested_time:
                    alternatives.append({
                        "time": slot_time.isoformat(),
                        "day": day_of_week,
                        "duration": duration
                    })
                    
                    if len(alternatives) >= 3:
                        return alternatives
            
            current += timedelta(days=1)
        
        return alternatives
    
    def _generate_study_time_suggestions(
        self,
        user_patterns: Dict,
        preferences: Dict
    ) -> List[Dict]:
        """Generate study time suggestions based on patterns."""
        suggestions = []
        
        # Analyze user's most productive times
        productive_hours = user_patterns.get("productive_hours", [9, 14, 20])
        preferred_duration = preferences.get("session_duration", 60)
        
        for hour in productive_hours:
            suggestions.append({
                "time": f"{hour:02d}:00",
                "duration": preferred_duration,
                "reason": "Based on your productivity patterns",
                "confidence": 0.85
            })
        
        return suggestions
    
    def _estimate_completion_date(self, schedule: List[Dict]) -> str:
        """Estimate completion date for schedule."""
        if not schedule:
            return datetime.utcnow().isoformat()
        
        last_task = max(schedule, key=lambda x: x["scheduled_time"])
        completion = datetime.fromisoformat(last_task["scheduled_time"])
        completion += timedelta(minutes=last_task["duration"])
        
        return completion.isoformat()
