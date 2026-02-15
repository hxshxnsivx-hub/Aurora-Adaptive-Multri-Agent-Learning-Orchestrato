"""
User and profile models for the Adaptive Learning Platform.
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.core.database import Base


class User(Base):
    """Core user model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    auth0_id = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    learning_paths = relationship("LearningPath", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class UserProfile(Base):
    """Extended user profile with learning preferences and skills."""
    
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    
    # Skill levels: {"python": 0.7, "algorithms": 0.5, ...}
    skill_levels = Column(JSON, nullable=False, default=dict)
    
    # Learning preferences
    learning_preferences = Column(JSON, nullable=False, default=dict)
    
    # Availability schedule: {"monday": [{"start": 9, "end": 12}, ...], ...}
    availability_schedule = Column(JSON, nullable=False, default=dict)
    
    timezone = Column(String(50), nullable=False, default="UTC")
    
    # Learning goals: [{"title": "...", "description": "...", "target_date": "..."}, ...]
    goals = Column(JSON, nullable=False, default=list)
    
    # Integration settings
    integrations = Column(JSON, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, display_name={self.display_name})>"


class UserProgress(Base):
    """User progress tracking across learning paths."""
    
    __tablename__ = "user_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    learning_path_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    current_milestone_id = Column(UUID(as_uuid=True), nullable=True)
    completed_milestones = Column(JSON, nullable=False, default=list)  # List of milestone IDs
    completed_tasks = Column(JSON, nullable=False, default=list)  # List of task IDs
    
    total_study_time = Column(Integer, default=0)  # minutes
    streak_days = Column(Integer, default=0)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Performance metrics
    performance_metrics = Column(JSON, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress")
    
    def __repr__(self):
        return f"<UserProgress(id={self.id}, user_id={self.user_id})>"


class ConversationContext(Base):
    """Voice assistant conversation context."""
    
    __tablename__ = "conversation_contexts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    
    # Conversation history: [{"timestamp": "...", "user_input": "...", "agent_response": "...", ...}, ...]
    conversation_history = Column(JSON, nullable=False, default=list)
    
    current_intent = Column(String(255), nullable=True)
    context_variables = Column(JSON, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ConversationContext(id={self.id}, user_id={self.user_id}, session_id={self.session_id})>"