"""
Learning path and milestone models.
"""

from sqlalchemy import Column, String, DateTime, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from typing import List, Optional, Dict

from app.core.database import Base


class LearningPath(Base):
    """Learning path model with milestones and progression."""
    
    __tablename__ = "learning_paths"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    difficulty_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced, expert
    estimated_total_hours = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="active")  # active, completed, paused
    completion_percentage = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="learning_paths")
    milestones = relationship("Milestone", back_populates="learning_path", cascade="all, delete-orphan")
    reallocations = relationship("Reallocation", back_populates="learning_path", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LearningPath(id={self.id}, title={self.title}, user_id={self.user_id})>"


class Milestone(Base):
    """Milestone model with tasks and resources."""
    
    __tablename__ = "milestones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learning_path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=False, index=True)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    completion_criteria = Column(Text, nullable=True)
    estimated_hours = Column(Integer, nullable=False)
    
    # Prerequisites: list of milestone IDs that must be completed first
    prerequisites = Column(ARRAY(UUID(as_uuid=True)), default=list)
    
    status = Column(String(20), nullable=False, default="not_started")  # not_started, in_progress, completed
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    learning_path = relationship("LearningPath", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Milestone(id={self.id}, title={self.title}, learning_path_id={self.learning_path_id})>"


class Task(Base):
    """Individual task within a milestone."""
    
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    milestone_id = Column(UUID(as_uuid=True), ForeignKey("milestones.id"), nullable=False, index=True)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String(50), nullable=False)  # read, watch, code, practice, quiz
    estimated_minutes = Column(Integer, nullable=False)
    
    # Associated resources for this task
    resources = Column(JSON, nullable=False, default=list)  # List of resource IDs
    
    completion_status = Column(String(20), nullable=False, default="not_started")  # not_started, in_progress, completed
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    milestone = relationship("Milestone", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, milestone_id={self.milestone_id})>"


class Reallocation(Base):
    """Learning path reallocation tracking."""
    
    __tablename__ = "reallocations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    learning_path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=False, index=True)
    
    trigger_reason = Column(String(50), nullable=False)  # behind_schedule, too_easy, too_hard, user_feedback
    original_milestone_id = Column(UUID(as_uuid=True), nullable=False)
    new_milestone_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Changes made: [{"change_type": "...", "target_id": "...", "old_value": {...}, "new_value": {...}, "reasoning": "..."}, ...]
    changes_made = Column(JSON, nullable=False, default=list)
    
    confidence_score = Column(Float, nullable=False)  # AI confidence in the reallocation
    user_approved = Column(String(20), nullable=True)  # approved, rejected, pending
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    applied_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    learning_path = relationship("LearningPath", back_populates="reallocations")
    
    def __repr__(self):
        return f"<Reallocation(id={self.id}, learning_path_id={self.learning_path_id}, trigger_reason={self.trigger_reason})>"