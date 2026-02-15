"""
Task Manager Agent for task orchestration and tracking.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from app.agents.base import BaseAgent, AgentMessage, AgentState

logger = logging.getLogger(__name__)


class TaskManagerAgent(BaseAgent):
    """Agent responsible for managing and orchestrating learning tasks."""
    
    def __init__(self):
        super().__init__(
            agent_id="task_manager_agent",
            name="Task Manager Agent"
        )
    
    async def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Process task management requests."""
        try:
            action = message.content.get("action")
            
            if action == "create_tasks":
                return await self._create_tasks(message, state)
            elif action == "update_task_status":
                return await self._update_task_status(message, state)
            elif action == "get_upcoming_tasks":
                return await self._get_upcoming_tasks(message, state)
            elif action == "prioritize_tasks":
                return await self._prioritize_tasks(message, state)
            elif action == "track_progress":
                return await self._track_progress(message, state)
            else:
                return self._create_error_response(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error in TaskManagerAgent: {e}")
            return self._create_error_response(str(e))
    
    async def _create_tasks(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Create tasks from milestones."""
        milestone = message.content.get("milestone", {})
        resources = message.content.get("resources", [])
        
        tasks = []
        for idx, resource in enumerate(resources):
            task = {
                "id": f"task_{milestone.get('id')}_{idx}",
                "milestone_id": milestone.get("id"),
                "title": f"Study: {resource.get('title', 'Resource')}",
                "description": resource.get("description", ""),
                "task_type": self._determine_task_type(resource),
                "estimated_minutes": resource.get("estimated_duration", 30),
                "resource_id": resource.get("id"),
                "status": "not_started",
                "priority": self._calculate_priority(resource, milestone),
                "created_at": datetime.utcnow().isoformat()
            }
            tasks.append(task)
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={"tasks": tasks, "total_created": len(tasks)},
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _update_task_status(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Update task status and track completion."""
        task_id = message.content.get("task_id")
        new_status = message.content.get("status")
        completion_data = message.content.get("completion_data", {})
        
        update_result = {
            "task_id": task_id,
            "old_status": "in_progress",  # Would fetch from DB
            "new_status": new_status,
            "updated_at": datetime.utcnow().isoformat(),
            "completion_percentage": self._calculate_completion_percentage(new_status),
            "next_task": self._suggest_next_task(task_id, state)
        }
        
        # If task completed, update progress metrics
        if new_status == "completed":
            update_result["progress_update"] = self._update_progress_metrics(
                task_id,
                completion_data
            )
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content=update_result,
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _get_upcoming_tasks(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Get upcoming tasks for a user."""
        user_id = message.content.get("user_id")
        days_ahead = message.content.get("days_ahead", 7)
        
        # Simulate fetching upcoming tasks
        upcoming = [
            {
                "id": f"task_{i}",
                "title": f"Study Task {i}",
                "scheduled_at": (datetime.utcnow() + timedelta(days=i)).isoformat(),
                "estimated_minutes": 30,
                "priority": "medium",
                "status": "not_started"
            }
            for i in range(1, min(days_ahead + 1, 8))
        ]
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "upcoming_tasks": upcoming,
                "total_tasks": len(upcoming),
                "total_hours": sum(t["estimated_minutes"] for t in upcoming) / 60
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _prioritize_tasks(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Prioritize tasks based on deadlines and dependencies."""
        tasks = message.content.get("tasks", [])
        
        prioritized = sorted(
            tasks,
            key=lambda t: (
                self._get_priority_value(t.get("priority", "medium")),
                t.get("scheduled_at", ""),
                -t.get("estimated_minutes", 0)
            )
        )
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={"prioritized_tasks": prioritized},
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _track_progress(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Track progress across all tasks."""
        user_id = message.content.get("user_id")
        learning_path_id = message.content.get("learning_path_id")
        
        progress = {
            "total_tasks": 50,  # Would fetch from DB
            "completed_tasks": 15,
            "in_progress_tasks": 5,
            "not_started_tasks": 30,
            "completion_percentage": 30.0,
            "total_study_time": 450,  # minutes
            "average_task_duration": 30,
            "streak_days": 7,
            "last_activity": datetime.utcnow().isoformat()
        }
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content=progress,
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    def _determine_task_type(self, resource: Dict) -> str:
        """Determine task type from resource."""
        resource_type = resource.get("resource_type", "article")
        
        type_map = {
            "video": "watch",
            "article": "read",
            "repository": "code",
            "course": "practice",
            "tutorial": "practice"
        }
        
        return type_map.get(resource_type, "read")
    
    def _calculate_priority(self, resource: Dict, milestone: Dict) -> str:
        """Calculate task priority."""
        # Check if milestone has deadline
        deadline = milestone.get("due_date")
        if deadline:
            try:
                due = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                days_until = (due - datetime.utcnow()).days
                
                if days_until < 3:
                    return "high"
                elif days_until < 7:
                    return "medium"
            except:
                pass
        
        # Check resource importance
        quality = resource.get("quality_score", 0.5)
        if quality > 0.8:
            return "high"
        
        return "medium"
    
    def _calculate_completion_percentage(self, status: str) -> float:
        """Calculate completion percentage based on status."""
        status_map = {
            "not_started": 0.0,
            "in_progress": 50.0,
            "completed": 100.0,
            "skipped": 0.0
        }
        return status_map.get(status, 0.0)
    
    def _suggest_next_task(self, current_task_id: str, state: AgentState) -> Optional[Dict]:
        """Suggest next task after completing current one."""
        # Simplified - would fetch from DB based on dependencies
        return {
            "id": f"next_task_after_{current_task_id}",
            "title": "Next recommended task",
            "estimated_minutes": 30
        }
    
    def _update_progress_metrics(self, task_id: str, completion_data: Dict) -> Dict:
        """Update progress metrics after task completion."""
        return {
            "tasks_completed_today": 3,
            "total_study_time_today": 90,
            "streak_maintained": True,
            "milestone_progress": 45.0
        }
    
    def _get_priority_value(self, priority: str) -> int:
        """Get numeric value for priority."""
        priority_map = {
            "high": 0,
            "medium": 1,
            "low": 2
        }
        return priority_map.get(priority, 1)
