"""
Resource and content models.
"""

from sqlalchemy import Column, String, DateTime, Integer, Float, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import List, Optional, Dict

from app.core.database import Base


class Resource(Base):
    """Educational resource model."""
    
    __tablename__ = "resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(String(50), nullable=False)  # video, article, repository, course, pdf
    source_platform = Column(String(50), nullable=False)  # youtube, github, web, etc.
    url = Column(Text, nullable=False)
    
    # Resource metadata: {"author": "...", "published_date": "...", "view_count": 123, ...}
    metadata = Column(JSON, nullable=False, default=dict)
    
    difficulty_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced, expert
    estimated_duration = Column(Integer, nullable=False)  # minutes
    tags = Column(ARRAY(String), default=list)
    quality_score = Column(Float, nullable=False, default=0.0)  # 0-1, based on curation algorithm
    
    # Vector embedding for semantic search (stored in Pinecone)
    embedding_id = Column(String(255), nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Resource(id={self.id}, title={self.title}, resource_type={self.resource_type})>"


class ResourceCollection(Base):
    """Curated collection of resources for specific topics."""
    
    __tablename__ = "resource_collections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    topic = Column(String(255), nullable=False, index=True)
    difficulty_level = Column(String(20), nullable=False)
    
    # Resource IDs in this collection
    resource_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)
    
    # Collection metadata
    metadata = Column(JSON, nullable=False, default=dict)
    
    is_public = Column(Boolean, default=True)
    created_by = Column(String(50), nullable=False, default="system")  # system, user_id, or agent_name
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ResourceCollection(id={self.id}, name={self.name}, topic={self.topic})>"


class ResourceRating(Base):
    """User ratings and feedback for resources."""
    
    __tablename__ = "resource_ratings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    rating = Column(Float, nullable=False)  # 1-5 stars
    difficulty_rating = Column(Float, nullable=True)  # 1-5, how difficult user found it
    relevance_rating = Column(Float, nullable=True)  # 1-5, how relevant to learning goals
    
    feedback = Column(Text, nullable=True)
    completion_time = Column(Integer, nullable=True)  # actual time spent in minutes
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ResourceRating(id={self.id}, resource_id={self.resource_id}, user_id={self.user_id}, rating={self.rating})>"


class SearchQuery(Base):
    """Search query tracking for analytics and improvement."""
    
    __tablename__ = "search_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50), nullable=False)  # semantic, keyword, hybrid
    filters = Column(JSON, nullable=False, default=dict)  # Applied filters
    
    # Results
    results_count = Column(Integer, nullable=False, default=0)
    selected_results = Column(ARRAY(UUID(as_uuid=True)), default=list)  # Resource IDs user clicked
    
    # Performance metrics
    response_time_ms = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SearchQuery(id={self.id}, query_text={self.query_text[:50]}...)>"