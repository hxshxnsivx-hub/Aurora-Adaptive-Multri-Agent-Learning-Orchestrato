"""
External integration models for Calendar, Notion, etc.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.core.database import Base


class Integration(Base):
    """Base integration model for external services."""
    
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    integration_type = Column(String(50), nullable=False)  # google_calendar, notion, github
    service_name = Column(String(100), nullable=False)
    
    # Encrypted credentials
    access_token = Column(Text, nullable=True)  # Encrypted
    refresh_token = Column(Text, nullable=True)  # Encrypted
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Service-specific configuration
    config = Column(JSON, nullable=False, default=dict)
    
    is_active = Column(Boolean, default=True)
    sync_enabled = Column(Boolean, default=True)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Sync preferences
    sync_preferences = Column(JSON, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="integrations")
    calendar_events = relationship("CalendarEvent", back_populates="integration", cascade="all, delete-orphan")
    notion_pages = relationship("NotionPage", back_populates="integration", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Integration(id={self.id}, user_id={self.user_id}, integration_type={self.integration_type})>"


class CalendarEvent(Base):
    """Google Calendar event synchronization."""
    
    __tablename__ = "calendar_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False, index=True)
    
    # Google Calendar event ID
    external_event_id = Column(String(255), nullable=False, index=True)
    calendar_id = Column(String(255), nullable=False)
    
    # Associated learning entities
    task_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    milestone_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String(50), nullable=False, default="UTC")
    
    event_type = Column(String(50), nullable=False)  # learning_session, milestone_deadline, review
    
    # Sync status
    sync_status = Column(String(20), nullable=False, default="synced")  # synced, pending, failed
    last_synced = Column(DateTime(timezone=True), server_default=func.now())
    
    # Event metadata
    metadata = Column(JSON, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    integration = relationship("Integration", back_populates="calendar_events")
    
    def __repr__(self):
        return f"<CalendarEvent(id={self.id}, title={self.title}, start_time={self.start_time})>"


class NotionPage(Base):
    """Notion page synchronization."""
    
    __tablename__ = "notion_pages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False, index=True)
    
    # Notion page ID
    external_page_id = Column(String(255), nullable=False, index=True)
    database_id = Column(String(255), nullable=True)
    
    # Associated learning entities
    task_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    milestone_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    
    page_type = Column(String(50), nullable=False)  # task, milestone, notes, progress
    
    # Sync status
    sync_status = Column(String(20), nullable=False, default="synced")  # synced, pending, failed
    last_synced = Column(DateTime(timezone=True), server_default=func.now())
    
    # Page metadata
    metadata = Column(JSON, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    integration = relationship("Integration", back_populates="notion_pages")
    
    def __repr__(self):
        return f"<NotionPage(id={self.id}, title={self.title}, page_type={self.page_type})>"


class SyncLog(Base):
    """Integration synchronization logging."""
    
    __tablename__ = "sync_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False, index=True)
    
    sync_type = Column(String(50), nullable=False)  # full_sync, incremental_sync, push, pull
    sync_direction = Column(String(20), nullable=False)  # inbound, outbound, bidirectional
    
    # Sync results
    status = Column(String(20), nullable=False)  # success, partial_success, failed
    items_processed = Column(Integer, nullable=False, default=0)
    items_succeeded = Column(Integer, nullable=False, default=0)
    items_failed = Column(Integer, nullable=False, default=0)
    
    # Error information
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=False, default=dict)
    
    # Performance metrics
    duration_ms = Column(Integer, nullable=False)
    
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SyncLog(id={self.id}, integration_id={self.integration_id}, status={self.status})>"


class WebhookEvent(Base):
    """Webhook events from external services."""
    
    __tablename__ = "webhook_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id"), nullable=True, index=True)
    
    source_service = Column(String(50), nullable=False)  # google_calendar, notion, github
    event_type = Column(String(100), nullable=False)
    event_id = Column(String(255), nullable=True, index=True)
    
    # Raw webhook payload
    payload = Column(JSON, nullable=False)
    
    # Processing status
    processing_status = Column(String(20), nullable=False, default="pending")  # pending, processed, failed
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error information
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<WebhookEvent(id={self.id}, source_service={self.source_service}, event_type={self.event_type})>"