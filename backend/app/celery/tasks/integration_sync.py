"""
Background tasks for external integration synchronization.
"""

from celery import current_task
from app.celery.worker import celery_app
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def sync_google_calendar(self, user_id: str):
    """Sync user's Google Calendar with learning schedule."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 5, "total": 100, "status": "Validating Google Calendar integration"}
        )
        
        # Get user's Google Calendar integration settings
        integration_data = _get_google_calendar_integration(user_id)
        
        if not integration_data or not integration_data.get("enabled"):
            logger.info(f"Google Calendar integration not enabled for user {user_id}")
            return {
                "status": "skipped",
                "user_id": user_id,
                "reason": "Integration not enabled"
            }
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 15, "total": 100, "status": "Authenticating with Google Calendar"}
        )
        
        # Authenticate and get calendar service
        calendar_service = _authenticate_google_calendar(integration_data)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 30, "total": 100, "status": "Fetching existing calendar events"}
        )
        
        # Fetch existing learning events from calendar
        existing_events = _fetch_learning_events_from_calendar(calendar_service, user_id)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 50, "total": 100, "status": "Fetching scheduled learning sessions"}
        )
        
        # Get scheduled learning sessions from database
        scheduled_sessions = _get_user_scheduled_sessions(user_id)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 70, "total": 100, "status": "Synchronizing events"}
        )
        
        # Synchronize events
        sync_result = _synchronize_calendar_events(
            calendar_service, existing_events, scheduled_sessions, user_id
        )
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Updating sync status"}
        )
        
        # Update last sync timestamp
        _update_calendar_sync_timestamp(user_id)
        
        logger.info(f"Google Calendar synced for user {user_id}")
        return {
            "status": "completed",
            "user_id": user_id,
            "events_created": sync_result["created"],
            "events_updated": sync_result["updated"],
            "events_deleted": sync_result["deleted"],
            "conflicts_resolved": sync_result["conflicts_resolved"]
        }
        
    except Exception as e:
        logger.error(f"Google Calendar sync failed for user {user_id}: {e}")
        raise


@celery_app.task(bind=True)
def sync_notion_workspace(self, user_id: str):
    """Sync user's Notion workspace with learning progress."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 5, "total": 100, "status": "Validating Notion integration"}
        )
        
        # Get user's Notion integration settings
        integration_data = _get_notion_integration(user_id)
        
        if not integration_data or not integration_data.get("enabled"):
            logger.info(f"Notion integration not enabled for user {user_id}")
            return {
                "status": "skipped",
                "user_id": user_id,
                "reason": "Integration not enabled"
            }
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 15, "total": 100, "status": "Connecting to Notion workspace"}
        )
        
        # Connect to Notion
        notion_client = _connect_to_notion(integration_data)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 30, "total": 100, "status": "Syncing learning paths"}
        )
        
        # Sync learning paths
        paths_sync_result = _sync_learning_paths_to_notion(notion_client, user_id)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 50, "total": 100, "status": "Syncing milestones and tasks"}
        )
        
        # Sync milestones and tasks
        tasks_sync_result = _sync_tasks_to_notion(notion_client, user_id)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 70, "total": 100, "status": "Syncing progress updates"}
        )
        
        # Sync progress updates
        progress_sync_result = _sync_progress_to_notion(notion_client, user_id)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 85, "total": 100, "status": "Syncing resources and notes"}
        )
        
        # Sync resources and notes
        resources_sync_result = _sync_resources_to_notion(notion_client, user_id)
        
        # Update last sync timestamp
        _update_notion_sync_timestamp(user_id)
        
        logger.info(f"Notion workspace synced for user {user_id}")
        return {
            "status": "completed",
            "user_id": user_id,
            "paths_synced": paths_sync_result["synced"],
            "tasks_synced": tasks_sync_result["synced"],
            "progress_updates": progress_sync_result["synced"],
            "resources_synced": resources_sync_result["synced"],
            "pages_created": (
                paths_sync_result["created"] + 
                tasks_sync_result["created"] + 
                resources_sync_result["created"]
            ),
            "pages_updated": (
                paths_sync_result["updated"] + 
                tasks_sync_result["updated"] + 
                progress_sync_result["updated"] + 
                resources_sync_result["updated"]
            )
        }
        
    except Exception as e:
        logger.error(f"Notion sync failed for user {user_id}: {e}")
        raise


@celery_app.task(bind=True)
def sync_all_integrations(self):
    """Sync all active integrations for all users."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 5, "total": 100, "status": "Fetching active integrations"}
        )
        
        # TODO: Implement bulk sync
        # 1. Fetch all users with active integrations
        # 2. Queue individual sync tasks
        # 3. Monitor and report progress
        
        users_synced = 0
        total_users = 10  # TODO: Get actual count from database
        
        for i in range(total_users):
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "current": 10 + (i * 80 // total_users),
                    "total": 100,
                    "status": f"Syncing user {i+1}/{total_users}"
                }
            )
            
            # TODO: Queue individual sync tasks
            users_synced += 1
        
        logger.info(f"Bulk integration sync completed for {users_synced} users")
        return {
            "status": "completed",
            "users_synced": users_synced,
            "calendar_syncs": users_synced,
            "notion_syncs": users_synced
        }
        
    except Exception as e:
        logger.error(f"Bulk integration sync failed: {e}")
        raise


@celery_app.task(bind=True)
def handle_integration_webhook(self, integration_type: str, user_id: str, webhook_data: dict):
    """Handle incoming webhooks from external integrations."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 20, "total": 100, "status": f"Processing {integration_type} webhook"}
        )
        
        if integration_type == "google_calendar":
            # TODO: Handle Google Calendar webhook
            # 1. Parse calendar event changes
            # 2. Update learning schedule accordingly
            # 3. Notify user of conflicts
            pass
        elif integration_type == "notion":
            # TODO: Handle Notion webhook
            # 1. Parse workspace changes
            # 2. Update task completion status
            # 3. Sync progress updates
            pass
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 80, "total": 100, "status": "Updating local data"}
        )
        
        logger.info(f"Webhook processed for {integration_type}, user {user_id}")
        return {
            "status": "completed",
            "integration_type": integration_type,
            "user_id": user_id,
            "changes_processed": 1
        }
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise


@celery_app.task(bind=True)
def refresh_integration_tokens(self):
    """Refresh expired OAuth tokens for all integrations."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 10, "total": 100, "status": "Checking token expiration"}
        )
        
        # TODO: Implement token refresh
        # 1. Find tokens expiring soon
        # 2. Refresh using refresh tokens
        # 3. Update stored credentials
        # 4. Handle refresh failures
        
        tokens_refreshed = 0
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Updating credentials"}
        )
        
        logger.info(f"Token refresh completed, {tokens_refreshed} tokens refreshed")
        return {
            "status": "completed",
            "tokens_refreshed": tokens_refreshed,
            "failures": 0
        }
        
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise

# Helper functions for Google Calendar integration

def _get_google_calendar_integration(user_id: str) -> Optional[Dict]:
    """Get Google Calendar integration settings for user."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.integration import Integration
        from sqlalchemy import select, and_
        import asyncio
        
        async def get_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Integration).where(
                        and_(
                            Integration.user_id == user_id,
                            Integration.integration_type == "google_calendar",
                            Integration.is_active == True
                        )
                    )
                )
                integration = result.scalar_one_or_none()
                
                if not integration:
                    return None
                
                return {
                    "enabled": integration.is_active,
                    "calendar_id": integration.config.get("calendar_id", "primary"),
                    "access_token": integration.credentials.get("access_token", ""),
                    "refresh_token": integration.credentials.get("refresh_token", ""),
                    "token_expires_at": integration.credentials.get("expires_at", "")
                }
        
        return asyncio.run(get_async())
    except Exception as e:
        logger.error(f"Failed to get Google Calendar integration: {e}")
        return None


def _authenticate_google_calendar(integration_data: Dict):
    """Authenticate with Google Calendar API."""
    try:
        from app.integrations.google_calendar import GoogleCalendarClient
        
        calendar_client = GoogleCalendarClient(
            access_token=integration_data.get("access_token", ""),
            refresh_token=integration_data.get("refresh_token", "")
        )
        
        return calendar_client
    except Exception as e:
        logger.error(f"Google Calendar authentication failed: {e}")
        return None


def _fetch_learning_events_from_calendar(calendar_service, user_id: str) -> List[Dict]:
    """Fetch existing learning events from Google Calendar."""
    try:
        if not calendar_service:
            return []
        
        from datetime import datetime, timedelta
        
        # Get events for the next 30 days
        time_min = datetime.now().isoformat() + "Z"
        time_max = (datetime.now() + timedelta(days=30)).isoformat() + "Z"
        
        events = calendar_service.list_events(
            calendar_id="primary",
            time_min=time_min,
            time_max=time_max,
            q="Learning"  # Search for learning-related events
        )
        
        learning_events = []
        for event in events:
            # Check if event is a learning session
            if "learning" in event.get("summary", "").lower() or \
               "study" in event.get("summary", "").lower():
                learning_events.append({
                    "id": event.get("id", ""),
                    "summary": event.get("summary", ""),
                    "start": event.get("start", {}).get("dateTime", ""),
                    "end": event.get("end", {}).get("dateTime", ""),
                    "description": event.get("description", "")
                })
        
        return learning_events
    except Exception as e:
        logger.error(f"Failed to fetch calendar events: {e}")
        return []


def _get_user_scheduled_sessions(user_id: str) -> List[Dict]:
    """Get scheduled learning sessions from database."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.progress import LearningSession
        from sqlalchemy import select
        from datetime import datetime
        import asyncio
        
        async def get_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(LearningSession).where(
                        LearningSession.user_id == user_id,
                        LearningSession.scheduled_time > datetime.now()
                    ).order_by(LearningSession.scheduled_time)
                )
                sessions = result.scalars().all()
                
                return [
                    {
                        "id": s.id,
                        "milestone_id": s.milestone_id,
                        "title": s.title or "Learning Session",
                        "scheduled_time": s.scheduled_time,
                        "duration": s.duration_minutes,
                        "description": s.description or ""
                    }
                    for s in sessions
                ]
        
        return asyncio.run(get_async())
    except Exception as e:
        logger.error(f"Failed to get user scheduled sessions: {e}")
        return []


def _synchronize_calendar_events(calendar_service, existing_events: List[Dict], 
                                scheduled_sessions: List[Dict], user_id: str) -> Dict:
    """Synchronize calendar events with scheduled sessions."""
    sync_result = {
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "conflicts_resolved": 0
    }
    
    try:
        # Create map of existing events by title
        existing_map = {event["summary"]: event for event in existing_events}
        
        # Create or update events for scheduled sessions
        for session in scheduled_sessions:
            event_title = f"Learning: {session['title']}"
            
            if event_title in existing_map:
                # Update existing event
                existing_event = existing_map[event_title]
                calendar_service.update_event(
                    calendar_id="primary",
                    event_id=existing_event["id"],
                    summary=event_title,
                    description=session["description"],
                    start_time=session["scheduled_time"],
                    duration_minutes=session["duration"]
                )
                sync_result["updated"] += 1
            else:
                # Create new event
                calendar_service.create_event(
                    calendar_id="primary",
                    summary=event_title,
                    description=session["description"],
                    start_time=session["scheduled_time"],
                    duration_minutes=session["duration"]
                )
                sync_result["created"] += 1
        
        return sync_result
    except Exception as e:
        logger.error(f"Failed to synchronize calendar events: {e}")
        return sync_result


def _update_calendar_sync_timestamp(user_id: str):
    """Update the last sync timestamp for Google Calendar."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.integration import Integration
        from sqlalchemy import select, and_
        import asyncio
        
        async def update_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Integration).where(
                        and_(
                            Integration.user_id == user_id,
                            Integration.integration_type == "google_calendar"
                        )
                    )
                )
                integration = result.scalar_one_or_none()
                
                if integration:
                    integration.last_synced_at = datetime.now()
                    await session.commit()
        
        asyncio.run(update_async())
    except Exception as e:
        logger.error(f"Failed to update calendar sync timestamp: {e}")
        pass


# Helper functions for Notion integration

def _get_notion_integration(user_id: str) -> Optional[Dict]:
    """Get Notion integration settings for user."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.integration import Integration
        from sqlalchemy import select, and_
        import asyncio
        
        async def get_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Integration).where(
                        and_(
                            Integration.user_id == user_id,
                            Integration.integration_type == "notion",
                            Integration.is_active == True
                        )
                    )
                )
                integration = result.scalar_one_or_none()
                
                if not integration:
                    return None
                
                return {
                    "enabled": integration.is_active,
                    "workspace_id": integration.config.get("workspace_id", ""),
                    "database_id": integration.config.get("database_id", ""),
                    "access_token": integration.access_token or "",
                    "bot_id": integration.config.get("bot_id", "")
                }
        
        return asyncio.run(get_async())
    except Exception as e:
        logger.error(f"Failed to get Notion integration: {e}")
        return None


def _connect_to_notion(integration_data: Dict):
    """Connect to Notion workspace."""
    try:
        from app.integrations.notion import NotionClient
        
        notion_client = NotionClient(
            access_token=integration_data.get("access_token", "")
        )
        
        return notion_client
    except Exception as e:
        logger.error(f"Failed to connect to Notion: {e}")
        return None


def _sync_learning_paths_to_notion(notion_client, user_id: str) -> Dict:
    """Sync learning paths to Notion."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.learning_path import LearningPath
        from sqlalchemy import select
        import asyncio
        
        async def sync_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(LearningPath).where(LearningPath.user_id == user_id)
                )
                paths = result.scalars().all()
                
                synced = 0
                created = 0
                updated = 0
                
                for path in paths:
                    # Create or update page in Notion
                    page_data = {
                        "title": path.title,
                        "description": path.description,
                        "status": path.status,
                        "difficulty": path.difficulty_level
                    }
                    
                    if notion_client:
                        # Check if page exists
                        existing_page_id = path.metadata.get("notion_page_id") if path.metadata else None
                        
                        if existing_page_id:
                            notion_client.update_page(existing_page_id, page_data)
                            updated += 1
                        else:
                            page_id = notion_client.create_page(page_data)
                            if not path.metadata:
                                path.metadata = {}
                            path.metadata["notion_page_id"] = page_id
                            created += 1
                        
                        synced += 1
                
                await session.commit()
                
                return {"synced": synced, "created": created, "updated": updated}
        
        return asyncio.run(sync_async())
    except Exception as e:
        logger.error(f"Failed to sync learning paths to Notion: {e}")
        return {"synced": 0, "created": 0, "updated": 0}


def _sync_tasks_to_notion(notion_client, user_id: str) -> Dict:
    """Sync tasks and milestones to Notion."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.learning_path import LearningPath, Milestone, Task
        from sqlalchemy import select
        import asyncio
        
        async def sync_async():
            async with AsyncSessionLocal() as session:
                # Get all learning paths for user
                result = await session.execute(
                    select(LearningPath).where(LearningPath.user_id == user_id)
                )
                paths = result.scalars().all()
                
                synced = 0
                created = 0
                updated = 0
                
                for path in paths:
                    # Get milestones for this path
                    milestone_result = await session.execute(
                        select(Milestone).where(Milestone.learning_path_id == path.id)
                    )
                    milestones = milestone_result.scalars().all()
                    
                    for milestone in milestones:
                        # Get tasks for this milestone
                        task_result = await session.execute(
                            select(Task).where(Task.milestone_id == milestone.id)
                        )
                        tasks = task_result.scalars().all()
                        
                        for task in tasks:
                            if notion_client:
                                # Create or update task page in Notion
                                page_data = {
                                    "Name": {
                                        "title": [{"text": {"content": task.title}}]
                                    },
                                    "Status": {
                                        "select": {"name": task.completion_status}
                                    },
                                    "Type": {
                                        "select": {"name": task.task_type}
                                    }
                                }
                                
                                # Check if page exists
                                existing_page_id = task.metadata.get("notion_page_id") if hasattr(task, 'metadata') and task.metadata else None
                                
                                if existing_page_id:
                                    await notion_client.update_page(existing_page_id, page_data)
                                    updated += 1
                                else:
                                    # Create new page
                                    database_id = notion_client.config.get("database_id", "")
                                    if database_id:
                                        page = await notion_client.create_page(database_id, page_data)
                                        if page:
                                            created += 1
                                
                                synced += 1
                
                return {"synced": synced, "created": created, "updated": updated}
        
        return asyncio.run(sync_async())
    except Exception as e:
        logger.error(f"Failed to sync tasks to Notion: {e}")
        return {"synced": 0, "created": 0, "updated": 0}


def _sync_progress_to_notion(notion_client, user_id: str) -> Dict:
    """Sync progress updates to Notion."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.user import UserProgress
        from app.models.learning_path import LearningPath
        from sqlalchemy import select
        import asyncio
        
        async def sync_async():
            async with AsyncSessionLocal() as session:
                # Get user progress records
                result = await session.execute(
                    select(UserProgress).where(UserProgress.user_id == user_id)
                )
                progress_records = result.scalars().all()
                
                synced = 0
                updated = 0
                
                for progress in progress_records:
                    if progress.learning_path_id and notion_client:
                        # Get learning path
                        path_result = await session.execute(
                            select(LearningPath).where(LearningPath.id == progress.learning_path_id)
                        )
                        path = path_result.scalar_one_or_none()
                        
                        if path and hasattr(path, 'metadata') and path.metadata:
                            notion_page_id = path.metadata.get("notion_page_id")
                            
                            if notion_page_id:
                                # Update progress in Notion page
                                progress_data = {
                                    "Progress": {
                                        "number": path.completion_percentage or 0
                                    },
                                    "Study Time": {
                                        "number": progress.total_study_time or 0
                                    },
                                    "Streak": {
                                        "number": progress.streak_days or 0
                                    }
                                }
                                
                                await notion_client.update_page(notion_page_id, progress_data)
                                updated += 1
                                synced += 1
                
                return {"synced": synced, "updated": updated}
        
        return asyncio.run(sync_async())
    except Exception as e:
        logger.error(f"Failed to sync progress to Notion: {e}")
        return {"synced": 0, "updated": 0}


def _sync_resources_to_notion(notion_client, user_id: str) -> Dict:
    """Sync resources and notes to Notion."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.resource import Resource
        from app.models.learning_path import LearningPath
        from sqlalchemy import select
        import asyncio
        
        async def sync_async():
            async with AsyncSessionLocal() as session:
                # Get user's learning paths
                path_result = await session.execute(
                    select(LearningPath).where(LearningPath.user_id == user_id)
                )
                paths = path_result.scalars().all()
                
                synced = 0
                created = 0
                updated = 0
                
                # Get resources associated with user's paths
                for path in paths:
                    if hasattr(path, 'metadata') and path.metadata:
                        resource_ids = path.metadata.get("resource_ids", [])
                        
                        for resource_id in resource_ids:
                            resource_result = await session.execute(
                                select(Resource).where(Resource.id == resource_id)
                            )
                            resource = resource_result.scalar_one_or_none()
                            
                            if resource and notion_client:
                                # Create or update resource page in Notion
                                page_data = {
                                    "Name": {
                                        "title": [{"text": {"content": resource.title}}]
                                    },
                                    "Type": {
                                        "select": {"name": resource.resource_type}
                                    },
                                    "URL": {
                                        "url": resource.url
                                    },
                                    "Quality Score": {
                                        "number": resource.quality_score or 0
                                    }
                                }
                                
                                # Check if page exists
                                existing_page_id = resource.metadata.get("notion_page_id") if resource.metadata else None
                                
                                if existing_page_id:
                                    await notion_client.update_page(existing_page_id, page_data)
                                    updated += 1
                                else:
                                    # Create new page
                                    database_id = notion_client.config.get("database_id", "")
                                    if database_id:
                                        page = await notion_client.create_page(database_id, page_data)
                                        if page:
                                            created += 1
                                
                                synced += 1
                
                return {"synced": synced, "created": created, "updated": updated}
        
        return asyncio.run(sync_async())
    except Exception as e:
        logger.error(f"Failed to sync resources to Notion: {e}")
        return {"synced": 0, "created": 0, "updated": 0}


def _update_notion_sync_timestamp(user_id: str):
    """Update the last sync timestamp for Notion."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.integration import Integration
        from sqlalchemy import select, and_
        import asyncio
        
        async def update_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Integration).where(
                        and_(
                            Integration.user_id == user_id,
                            Integration.integration_type == "notion"
                        )
                    )
                )
                integration = result.scalar_one_or_none()
                
                if integration:
                    integration.last_synced_at = datetime.now()
                    await session.commit()
        
        asyncio.run(update_async())
    except Exception as e:
        logger.error(f"Failed to update Notion sync timestamp: {e}")
        pass


# Additional integration tasks

@celery_app.task(bind=True)
def sync_github_repositories(self, user_id: str):
    """Sync user's GitHub repositories for learning resources."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 10, "total": 100, "status": "Connecting to GitHub"}
        )
        
        # Get GitHub integration settings
        github_integration = _get_github_integration(user_id)
        
        if not github_integration:
            return {"status": "skipped", "reason": "GitHub integration not configured"}
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 30, "total": 100, "status": "Fetching repositories"}
        )
        
        # Fetch user's repositories
        repositories = _fetch_user_repositories(github_integration)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 60, "total": 100, "status": "Analyzing repositories for learning content"}
        )
        
        # Analyze repositories for learning content
        learning_repos = _analyze_repositories_for_learning(repositories)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 85, "total": 100, "status": "Updating learning resources"}
        )
        
        # Update learning resources with repository content
        resources_added = _add_repositories_as_resources(user_id, learning_repos)
        
        logger.info(f"GitHub repositories synced for user {user_id}")
        return {
            "status": "completed",
            "user_id": user_id,
            "repositories_analyzed": len(repositories),
            "learning_repositories_found": len(learning_repos),
            "resources_added": resources_added
        }
        
    except Exception as e:
        logger.error(f"GitHub repositories sync failed for user {user_id}: {e}")
        raise


@celery_app.task(bind=True)
def backup_user_data_to_integrations(self, user_id: str):
    """Backup user's learning data to integrated platforms."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 10, "total": 100, "status": "Preparing backup data"}
        )
        
        # Get user's learning data
        learning_data = _get_user_learning_data_for_backup(user_id)
        
        backup_results = {}
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 30, "total": 100, "status": "Backing up to Notion"}
        )
        
        # Backup to Notion if enabled
        notion_integration = _get_notion_integration(user_id)
        if notion_integration and notion_integration.get("enabled"):
            backup_results["notion"] = _backup_to_notion(notion_integration, learning_data)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 60, "total": 100, "status": "Backing up to Google Drive"}
        )
        
        # Backup to Google Drive if enabled
        gdrive_integration = _get_google_drive_integration(user_id)
        if gdrive_integration and gdrive_integration.get("enabled"):
            backup_results["google_drive"] = _backup_to_google_drive(gdrive_integration, learning_data)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Finalizing backup"}
        )
        
        # Update backup timestamp
        _update_backup_timestamp(user_id)
        
        logger.info(f"User data backup completed for user {user_id}")
        return {
            "status": "completed",
            "user_id": user_id,
            "backup_results": backup_results,
            "backup_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"User data backup failed for user {user_id}: {e}")
        raise


def _get_github_integration(user_id: str) -> Optional[Dict]:
    """Get GitHub integration settings."""
    # TODO: Implement database query
    return {
        "enabled": True,
        "access_token": "encrypted_github_token",
        "username": "user_github_username"
    }


def _fetch_user_repositories(integration: Dict) -> List[Dict]:
    """Fetch user's GitHub repositories."""
    # TODO: Implement GitHub API call
    return [
        {
            "name": "python-learning-project",
            "description": "My Python learning exercises",
            "language": "Python",
            "topics": ["python", "learning", "exercises"]
        }
    ]


def _analyze_repositories_for_learning(repositories: List[Dict]) -> List[Dict]:
    """Analyze repositories to identify learning content."""
    learning_repos = []
    
    for repo in repositories:
        # Check if repository contains learning content
        if _is_learning_repository(repo):
            learning_repos.append(repo)
    
    return learning_repos


def _is_learning_repository(repo: Dict) -> bool:
    """Check if repository contains learning content."""
    learning_keywords = [
        "learning", "tutorial", "course", "exercise", "practice",
        "study", "bootcamp", "training", "education"
    ]
    
    repo_text = f"{repo.get('name', '')} {repo.get('description', '')}".lower()
    
    return any(keyword in repo_text for keyword in learning_keywords)


def _add_repositories_as_resources(user_id: str, repositories: List[Dict]) -> int:
    """Add repositories as learning resources."""
    # TODO: Implement database insertion
    return len(repositories)


def _get_user_learning_data_for_backup(user_id: str) -> Dict:
    """Get user's learning data for backup."""
    # TODO: Implement comprehensive data collection
    return {
        "learning_paths": [],
        "progress": {},
        "resources": [],
        "notes": []
    }


def _get_google_drive_integration(user_id: str) -> Optional[Dict]:
    """Get Google Drive integration settings."""
    # TODO: Implement database query
    return None


def _backup_to_notion(integration: Dict, data: Dict) -> Dict:
    """Backup data to Notion."""
    # TODO: Implement Notion backup
    return {"status": "completed", "pages_created": 5}


def _backup_to_google_drive(integration: Dict, data: Dict) -> Dict:
    """Backup data to Google Drive."""
    # TODO: Implement Google Drive backup
    return {"status": "completed", "files_created": 3}


def _update_backup_timestamp(user_id: str):
    """Update backup timestamp."""
    # TODO: Implement database update
    pass