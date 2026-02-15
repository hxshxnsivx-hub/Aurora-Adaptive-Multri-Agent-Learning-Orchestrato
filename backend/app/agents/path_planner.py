"""
Path Planner Agent - generates structured learning paths.
"""

from typing import Dict, Any, List, Optional
from app.agents.base import BaseAgent, AgentMessage
import logging
import uuid
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PathPlanner(BaseAgent):
    """Agent responsible for generating structured learning paths."""
    
    def __init__(self):
        super().__init__("path_planner", "Path Planner")
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process path planning messages."""
        self.add_message_to_history(message)
        
        if message.message_type == "generate_path":
            result = await self._generate_learning_path(message.content)
            return await self.send_message(
                message.sender,
                "path_generated",
                result
            )
        
        return None
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute path planning tasks."""
        task_type = task.get("type")
        
        self.update_state("processing", task_type)
        
        try:
            if task_type == "generate_path_structure":
                return await self._generate_path_structure(task)
            elif task_type == "optimize_path":
                return await self._optimize_existing_path(task)
            elif task_type == "validate_path":
                return await self._validate_path(task)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
        finally:
            self.update_state("idle")
    
    async def _generate_path_structure(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate learning path structure based on context and goals."""
        context = task.get("context", {})
        goals = task.get("goals", [])
        
        skill_analysis = context.get("skill_analysis", {})
        goal_analysis = context.get("goal_analysis", {})
        availability = context.get("availability_analysis", {})
        
        # Create milestone progression following Beginner → Intermediate → Advanced → Expert
        milestones = await self._create_milestone_sequence(skill_analysis, goal_analysis)
        
        # Optimize milestone order based on dependencies
        optimized_milestones = await self._optimize_milestone_order(milestones)
        
        # Calculate time estimates
        time_estimates = await self._calculate_time_estimates(optimized_milestones, availability)
        
        learning_path = {
            "id": str(uuid.uuid4()),
            "title": self._generate_path_title(goals),
            "description": self._generate_path_description(goals, skill_analysis),
            "difficulty_level": self._determine_overall_difficulty(skill_analysis, goal_analysis),
            "estimated_total_hours": time_estimates["total_hours"],
            "milestones": optimized_milestones,
            "progression_strategy": context.get("recommended_approach", {}).get("approach", "sequential"),
            "created_at": datetime.now(),
            "metadata": {
                "skill_gaps_addressed": skill_analysis.get("critical_gaps", []),
                "goals_covered": [goal["title"] for goal in goals],
                "confidence_score": context.get("context_confidence", 0.8)
            }
        }
        
        return learning_path
    
    async def _create_milestone_sequence(self, skill_analysis: Dict, goal_analysis: Dict) -> List[Dict]:
        """Create milestone sequence following difficulty progression."""
        milestones = []
        skill_gaps = skill_analysis.get("skill_gaps", {})
        
        # Group skills by difficulty level
        beginner_skills = [skill for skill, gap in skill_gaps.items() if gap["current_level"] < 0.3]
        intermediate_skills = [skill for skill, gap in skill_gaps.items() if 0.3 <= gap["current_level"] < 0.6]
        advanced_skills = [skill for skill, gap in skill_gaps.items() if gap["current_level"] >= 0.6]
        
        milestone_order = 1
        
        # Beginner milestones
        if beginner_skills:
            for skill in beginner_skills:
                milestone = await self._create_milestone(
                    skill, "beginner", milestone_order, skill_gaps[skill]
                )
                milestones.append(milestone)
                milestone_order += 1
        
        # Intermediate milestones
        if intermediate_skills:
            for skill in intermediate_skills:
                milestone = await self._create_milestone(
                    skill, "intermediate", milestone_order, skill_gaps[skill]
                )
                milestones.append(milestone)
                milestone_order += 1
        
        # Advanced milestones
        if advanced_skills:
            for skill in advanced_skills:
                milestone = await self._create_milestone(
                    skill, "advanced", milestone_order, skill_gaps[skill]
                )
                milestones.append(milestone)
                milestone_order += 1
        
        # Expert-level project milestones
        expert_milestones = await self._create_expert_milestones(goal_analysis, milestone_order)
        milestones.extend(expert_milestones)
        
        return milestones
    
    async def _create_milestone(self, skill: str, level: str, order: int, gap_info: Dict) -> Dict:
        """Create a milestone for a specific skill and level."""
        milestone_id = str(uuid.uuid4())
        
        # Generate milestone content based on skill and level
        milestone_templates = {
            "beginner": {
                "title_template": "Master {skill} Fundamentals",
                "description_template": "Learn the core concepts and basic applications of {skill}",
                "estimated_hours": 15
            },
            "intermediate": {
                "title_template": "Apply {skill} in Practice",
                "description_template": "Build practical projects and solve real-world problems using {skill}",
                "estimated_hours": 25
            },
            "advanced": {
                "title_template": "Advanced {skill} Techniques",
                "description_template": "Master advanced concepts and optimization techniques in {skill}",
                "estimated_hours": 35
            }
        }
        
        template = milestone_templates.get(level, milestone_templates["intermediate"])
        
        milestone = {
            "id": milestone_id,
            "title": template["title_template"].format(skill=skill.replace("_", " ").title()),
            "description": template["description_template"].format(skill=skill.replace("_", " ")),
            "order_index": order,
            "difficulty_level": level,
            "estimated_hours": template["estimated_hours"],
            "skill_focus": skill,
            "completion_criteria": await self._generate_completion_criteria(skill, level),
            "prerequisites": await self._determine_prerequisites(skill, level, order),
            "status": "not_started",
            "tasks": [],  # Will be populated by Task Manager agent
            "resources": [],  # Will be populated by Resource Curator agent
            "metadata": {
                "skill_gap": gap_info["gap"],
                "priority": gap_info["priority"],
                "current_level": gap_info["current_level"],
                "target_level": gap_info["required_level"]
            }
        }
        
        return milestone
    
    async def _create_expert_milestones(self, goal_analysis: Dict, start_order: int) -> List[Dict]:
        """Create expert-level project milestones based on goals."""
        expert_milestones = []
        goals = goal_analysis.get("goals", [])
        
        for i, goal_info in enumerate(goals):
            goal = goal_info["goal"]
            milestone_id = str(uuid.uuid4())
            
            milestone = {
                "id": milestone_id,
                "title": f"Capstone Project: {goal.get('title', 'Advanced Project')}",
                "description": goal.get("description", "Apply all learned skills in a comprehensive project"),
                "order_index": start_order + i,
                "difficulty_level": "expert",
                "estimated_hours": goal_info.get("estimated_duration", 40),
                "skill_focus": "integration",
                "completion_criteria": await self._generate_project_criteria(goal),
                "prerequisites": [m["id"] for m in expert_milestones[-2:]] if expert_milestones else [],
                "status": "not_started",
                "tasks": [],
                "resources": [],
                "metadata": {
                    "goal_id": goal.get("id"),
                    "complexity": goal_info.get("complexity", "high"),
                    "project_type": "capstone"
                }
            }
            
            expert_milestones.append(milestone)
        
        return expert_milestones
    
    def _generate_path_title(self, goals: List[Dict]) -> str:
        """Generate a descriptive title for the learning path."""
        if len(goals) == 1:
            return f"{goals[0].get('title', 'Learning')} Mastery Path"
        elif len(goals) <= 3:
            topics = [goal.get('title', 'Topic') for goal in goals]
            return f"{' & '.join(topics)} Learning Journey"
        else:
            return "Comprehensive Multi-Skill Development Path"
    
    def get_capabilities(self) -> List[str]:
        """Return path planner capabilities."""
        return [
            "learning_path_generation",
            "milestone_sequencing",
            "difficulty_progression",
            "prerequisite_analysis",
            "time_estimation",
            "path_optimization"
        ]