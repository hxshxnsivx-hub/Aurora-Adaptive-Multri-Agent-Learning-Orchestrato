"""
Progress tracking and analytics models.
"""

from sqlalchemy import Column, String, DateTime, Integer, Float, Text, JSON, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.core.database import Base


class StudySession(Base):
    """Individual study session tracking."""
    
    __tablename__ = "study_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    learning_path_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    milestone_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    task_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    session_type = Column(String(50), nullable=False)  # focused_study, review, practice, assessment
    duration_minutes = Column(Integer, nullable=False)
    
    # Resources accessed during session
    resources_accessed = Column(JSON, nullable=False, default=list)  # List of resource IDs
    
    # Session metrics
    focus_score = Column(Float, nullable=True)  # 0-1, based on interaction patterns
    completion_rate = Column(Float, nullable=True)  # 0-1, percentage of planned tasks completed
    difficulty_rating = Column(Float, nullable=True)  # 1-5, user's perceived difficulty
    satisfaction_rating = Column(Float, nullable=True)  # 1-5, user's satisfaction
    
    # Session notes and feedback
    notes = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<StudySession(id={self.id}, user_id={self.user_id}, duration_minutes={self.duration_minutes})>"


class LearningAnalytics(Base):
    """Aggregated learning analytics and insights."""
    
    __tablename__ = "learning_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Time period for analytics
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Study metrics
    total_study_time = Column(Integer, nullable=False, default=0)  # minutes
    sessions_count = Column(Integer, nullable=False, default=0)
    average_session_duration = Column(Float, nullable=False, default=0.0)  # minutes
    
    # Progress metrics
    tasks_completed = Column(Integer, nullable=False, default=0)
    milestones_completed = Column(Integer, nullable=False, default=0)
    resources_consumed = Column(Integer, nullable=False, default=0)
    
    # Performance metrics
    average_focus_score = Column(Float, nullable=True)
    average_completion_rate = Column(Float, nullable=True)
    average_difficulty_rating = Column(Float, nullable=True)
    average_satisfaction_rating = Column(Float, nullable=True)
    
    # Learning patterns
    preferred_study_times = Column(JSON, nullable=False, default=list)  # Hours of day
    preferred_session_duration = Column(Integer, nullable=True)  # minutes
    most_productive_days = Column(JSON, nullable=False, default=list)  # Days of week
    
    # Skill progression
    skill_improvements = Column(JSON, nullable=False, default=dict)  # skill -> improvement_score
    
    # Streaks and consistency
    current_streak = Column(Integer, nullable=False, default=0)  # days
    longest_streak = Column(Integer, nullable=False, default=0)  # days
    consistency_score = Column(Float, nullable=True)  # 0-1
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<LearningAnalytics(id={self.id}, user_id={self.user_id}, period_type={self.period_type})>"


class Achievement(Base):
    """User achievements and milestones."""
    
    __tablename__ = "achievements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    achievement_type = Column(String(50), nullable=False)  # milestone, streak, skill_mastery, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Achievement criteria and progress
    criteria = Column(JSON, nullable=False, default=dict)
    progress = Column(JSON, nullable=False, default=dict)
    
    is_unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Reward information
    reward_type = Column(String(50), nullable=True)  # badge, points, unlock_feature
    reward_data = Column(JSON, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Achievement(id={self.id}, user_id={self.user_id}, title={self.title}, is_unlocked={self.is_unlocked})>"


class PerformanceMetric(Base):
    """Detailed performance metrics for analysis."""
    
    __tablename__ = "performance_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    metric_type = Column(String(50), nullable=False)  # completion_rate, accuracy, speed, retention
    metric_category = Column(String(50), nullable=False)  # skill, topic, resource_type, etc.
    metric_target = Column(String(255), nullable=False)  # specific skill/topic/resource
    
    value = Column(Float, nullable=False)
    baseline_value = Column(Float, nullable=True)  # For comparison
    
    # Context information
    context = Column(JSON, nullable=False, default=dict)
    
    measured_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PerformanceMetric(id={self.id}, user_id={self.user_id}, metric_type={self.metric_type}, value={self.value})>"