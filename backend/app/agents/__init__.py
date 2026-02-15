"""
Multi-agent system for the Adaptive Learning Platform.
"""

from app.agents.base import BaseAgent, AgentMessage, AgentState
from app.agents.orchestrator import CentralOrchestrator
from app.agents.context_analyzer import ContextAnalyzer
from app.agents.user_profile import UserProfileAgent
from app.agents.goal_interpreter import GoalInterpreterAgent
from app.agents.path_planner import PathPlanner
from app.agents.schedule_optimizer import ScheduleOptimizerAgent
from app.agents.research import ResearchAgent
from app.agents.resource_curator import ResourceCuratorAgent
from app.agents.task_manager import TaskManagerAgent
from app.agents.calendar import CalendarAgent
from app.agents.notion_sync import NotionSyncAgent
from app.agents.voice_assistant import VoiceAssistantAgent
from app.agents.reallocation import ReallocationAgent

__all__ = [
    "BaseAgent",
    "AgentMessage",
    "AgentState",
    "CentralOrchestrator",
    "ContextAnalyzer",
    "UserProfileAgent",
    "GoalInterpreterAgent",
    "PathPlanner",
    "ScheduleOptimizerAgent",
    "ResearchAgent",
    "ResourceCuratorAgent",
    "TaskManagerAgent",
    "CalendarAgent",
    "NotionSyncAgent",
    "VoiceAssistantAgent",
    "ReallocationAgent",
]
