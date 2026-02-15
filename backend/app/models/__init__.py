"""
Database models for the Adaptive Learning Platform.
"""

from app.models.user import User, UserProfile
from app.models.learning_path import LearningPath, Milestone, Task
from app.models.resource import Resource, ResourceMetadata
from app.models.progress import UserProgress, PerformanceMetrics
from app.models.integration import CalendarIntegration, NotionIntegration, CalendarEvent, NotionPage

__all__ = [
    "User",
    "UserProfile",
    "LearningPath",
    "Milestone",
    "Task",
    "Resource",
    "ResourceMetadata",
    "UserProgress",
    "PerformanceMetrics",
    "CalendarIntegration",
    "NotionIntegration",
    "CalendarEvent",
    "NotionPage",
]
