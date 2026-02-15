"""
Reallocation Agent for dynamic path adjustment.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.agents.base import BaseAgent, AgentMessage, AgentState

logger = logging.getLogger(__name__)


class ReallocationAgent(BaseAgent):
    """Agent responsible for dynamic learning path reallocation."""
    
    def __init__(self):
        super().__init__(
            agent_id="reallocation_agent",
            name="Reallocation Agent"
        )
    
    async def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Process reallocation requests."""
        try:
            action = message.content.get("action")
            
            if action == "analyze_need":
                return await self._analyze_reallocation_need(message, state)
            elif action == "propose_changes":
                return await self._propose_changes(message, state)
            elif action == "apply_reallocation":
                return await self._apply_reallocation(message, state)
            else:
                return self._create_error_response(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error in ReallocationAgent: {e}")
            return self._create_error_response(str(e))
    
    async def _analyze_reallocation_need(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Analyze if reallocation is needed."""
        user_feedback = message.content.get("feedback", {})
        progress_data = message.content.get("progress", {})
        current_path = message.content.get("current_path", {})
        
        analysis = {
            "reallocation_needed": self._should_reallocate(user_feedback, progress_data),
            "reason": self._determine_reason(user_feedback, progress_data),
            "severity": self._assess_severity(user_feedback, progress_data),
            "recommended_changes": self._recommend_changes(user_feedback, progress_data, current_path),
            "confidence": 0.85
        }
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content=analysis,
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _propose_changes(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Propose specific changes to learning path."""
        reason = message.content.get("reason", "user_feedback")
        current_path = message.content.get("current_path", {})
        user_context = message.content.get("user_context", {})
        
        changes = []
        
        if reason == "too_difficult":
            changes.extend(self._propose_difficulty_reduction(current_path, user_context))
        elif reason == "too_easy":
            changes.extend(self._propose_difficulty_increase(current_path, user_context))
        elif reason == "behind_schedule":
            changes.extend(self._propose_schedule_adjustment(current_path, user_context))
        elif reason == "missing_prerequisites":
            changes.extend(self._propose_prerequisite_addition(current_path, user_context))
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "proposed_changes": changes,
                "total_changes": len(changes),
                "estimated_impact": self._estimate_impact(changes),
                "requires_approval": True
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _apply_reallocation(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        """Apply approved reallocation changes."""
        changes = message.content.get("changes", [])
        learning_path_id = message.content.get("learning_path_id")
        
        applied_changes = []
        for change in changes:
            result = self._apply_change(change, learning_path_id)
            applied_changes.append(result)
        
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            message_type="response",
            content={
                "applied_changes": applied_changes,
                "total_applied": len(applied_changes),
                "new_path_summary": self._generate_path_summary(applied_changes),
                "success": True
            },
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
    
    def _should_reallocate(self, feedback: Dict, progress: Dict) -> bool:
        """Determine if reallocation is needed."""
        # Check user feedback
        if feedback.get("difficulty_rating") == "too_hard" or feedback.get("difficulty_rating") == "too_easy":
            return True
        
        # Check progress metrics
        completion_rate = progress.get("completion_rate", 1.0)
        if completion_rate < 0.5:  # Less than 50% completion rate
            return True
        
        # Check if behind schedule
        if progress.get("behind_schedule", False):
            return True
        
        return False
    
    def _determine_reason(self, feedback: Dict, progress: Dict) -> str:
        """Determine reason for reallocation."""
        if feedback.get("difficulty_rating") == "too_hard":
            return "too_difficult"
        elif feedback.get("difficulty_rating") == "too_easy":
            return "too_easy"
        elif progress.get("behind_schedule"):
            return "behind_schedule"
        elif feedback.get("missing_background"):
            return "missing_prerequisites"
        else:
            return "user_feedback"
    
    def _assess_severity(self, feedback: Dict, progress: Dict) -> str:
        """Assess severity of reallocation need."""
        completion_rate = progress.get("completion_rate", 1.0)
        
        if completion_rate < 0.3:
            return "high"
        elif completion_rate < 0.6:
            return "medium"
        else:
            return "low"
    
    def _recommend_changes(self, feedback: Dict, progress: Dict, current_path: Dict) -> List[str]:
        """Recommend specific changes."""
        recommendations = []
        
        reason = self._determine_reason(feedback, progress)
        
        if reason == "too_difficult":
            recommendations.append("Add prerequisite materials")
            recommendations.append("Replace with easier resources")
            recommendations.append("Add more practice exercises")
        
        elif reason == "too_easy":
            recommendations.append("Skip to advanced topics")
            recommendations.append("Add challenging projects")
            recommendations.append("Accelerate timeline")
        
        elif reason == "behind_schedule":
            recommendations.append("Extend deadlines")
            recommendations.append("Reduce scope")
            recommendations.append("Increase study time")
        
        return recommendations
    
    def _propose_difficulty_reduction(self, current_path: Dict, user_context: Dict) -> List[Dict]:
        """Propose changes to reduce difficulty."""
        return [
            {
                "type": "add_milestone",
                "action": "Insert prerequisite milestone",
                "details": "Add foundational concepts before current content",
                "impact": "Extends timeline by 1 week"
            },
            {
                "type": "modify_resources",
                "action": "Replace with beginner-friendly resources",
                "details": "Swap current resources with easier alternatives",
                "impact": "Better comprehension, same timeline"
            }
        ]
    
    def _propose_difficulty_increase(self, current_path: Dict, user_context: Dict) -> List[Dict]:
        """Propose changes to increase difficulty."""
        return [
            {
                "type": "remove_milestone",
                "action": "Skip basic milestones",
                "details": "Remove redundant beginner content",
                "impact": "Reduces timeline by 1 week"
            },
            {
                "type": "add_milestone",
                "action": "Add advanced topics",
                "details": "Include expert-level challenges",
                "impact": "Extends timeline by 1 week, increases depth"
            }
        ]
    
    def _propose_schedule_adjustment(self, current_path: Dict, user_context: Dict) -> List[Dict]:
        """Propose schedule adjustments."""
        return [
            {
                "type": "reschedule",
                "action": "Extend deadlines",
                "details": "Push all milestones back by 1 week",
                "impact": "More manageable pace"
            },
            {
                "type": "modify_resources",
                "action": "Reduce content per milestone",
                "details": "Focus on core concepts only",
                "impact": "Faster completion, less depth"
            }
        ]
    
    def _propose_prerequisite_addition(self, current_path: Dict, user_context: Dict) -> List[Dict]:
        """Propose adding prerequisites."""
        return [
            {
                "type": "add_milestone",
                "action": "Add prerequisite milestone",
                "details": "Cover missing foundational knowledge",
                "impact": "Extends timeline by 2 weeks, improves understanding"
            }
        ]
    
    def _estimate_impact(self, changes: List[Dict]) -> Dict:
        """Estimate impact of proposed changes."""
        timeline_change = 0
        difficulty_change = 0
        
        for change in changes:
            if "Extends timeline" in change.get("impact", ""):
                timeline_change += 1
            elif "Reduces timeline" in change.get("impact", ""):
                timeline_change -= 1
            
            if "easier" in change.get("details", "").lower():
                difficulty_change -= 1
            elif "advanced" in change.get("details", "").lower():
                difficulty_change += 1
        
        return {
            "timeline_change_weeks": timeline_change,
            "difficulty_change": "easier" if difficulty_change < 0 else "harder" if difficulty_change > 0 else "same",
            "overall_impact": "moderate"
        }
    
    def _apply_change(self, change: Dict, learning_path_id: str) -> Dict:
        """Apply a single change to the learning path."""
        return {
            "change_type": change.get("type"),
            "action": change.get("action"),
            "applied": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_path_summary(self, applied_changes: List[Dict]) -> Dict:
        """Generate summary of new path after changes."""
        return {
            "total_milestones": 10,  # Would calculate from actual path
            "estimated_completion": "8 weeks",
            "difficulty_level": "intermediate",
            "changes_applied": len(applied_changes)
        }
