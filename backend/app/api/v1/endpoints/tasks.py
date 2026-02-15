"""
API endpoints for Celery task management and monitoring.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

from app.celery.management import celery_manager, get_task_monitoring_data
from app.celery.worker import celery_app
from app.core.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


class TaskSubmissionRequest(BaseModel):
    """Request model for submitting a new task."""
    task_name: str
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}
    queue: str = "celery"
    countdown: Optional[int] = None
    eta: Optional[str] = None


class TaskResponse(BaseModel):
    """Response model for task operations."""
    task_id: str
    status: str
    message: str


class TaskResult(BaseModel):
    """Model for task result information."""
    task_id: str
    status: str
    result: Any
    traceback: Optional[str] = None
    date_done: Optional[str] = None


class SystemHealth(BaseModel):
    """Model for system health information."""
    timestamp: str
    health_score: float
    workers: Dict[str, int]
    tasks: Dict[str, int]
    performance: Dict[str, Any]


@router.get("/health", response_model=SystemHealth)
async def get_system_health():
    """Get overall system health metrics."""
    try:
        health_data = celery_manager.get_system_health()
        return SystemHealth(**health_data)
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system health")


@router.get("/monitoring")
async def get_monitoring_data():
    """Get comprehensive task monitoring data."""
    try:
        return get_task_monitoring_data()
    except Exception as e:
        logger.error(f"Failed to get monitoring data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve monitoring data")


@router.get("/active")
async def get_active_tasks():
    """Get all currently active tasks."""
    try:
        active_tasks = celery_manager.get_active_tasks()
        return {"active_tasks": active_tasks}
    except Exception as e:
        logger.error(f"Failed to get active tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve active tasks")


@router.get("/scheduled")
async def get_scheduled_tasks():
    """Get all scheduled tasks."""
    try:
        scheduled_tasks = celery_manager.get_scheduled_tasks()
        return {"scheduled_tasks": scheduled_tasks}
    except Exception as e:
        logger.error(f"Failed to get scheduled tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve scheduled tasks")


@router.get("/workers")
async def get_worker_stats():
    """Get worker statistics."""
    try:
        worker_stats = celery_manager.get_worker_stats()
        return {"worker_stats": worker_stats}
    except Exception as e:
        logger.error(f"Failed to get worker stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve worker statistics")


@router.get("/registered")
async def get_registered_tasks():
    """Get all registered tasks."""
    try:
        registered_tasks = celery_manager.get_registered_tasks()
        return {"registered_tasks": registered_tasks}
    except Exception as e:
        logger.error(f"Failed to get registered tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve registered tasks")


@router.get("/{task_id}/result", response_model=TaskResult)
async def get_task_result(task_id: str):
    """Get result of a specific task."""
    try:
        result = celery_manager.get_task_result(task_id)
        if not result:
            raise HTTPException(status_code=404, detail="Task not found")
        return TaskResult(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task result for {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve task result")


@router.get("/{task_id}/info")
async def get_task_info(task_id: str):
    """Get detailed information about a task."""
    try:
        info = celery_manager.get_task_info(task_id)
        if not info:
            raise HTTPException(status_code=404, detail="Task not found")
        return info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task info for {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve task information")


@router.post("/submit", response_model=TaskResponse)
async def submit_task(
    request: TaskSubmissionRequest,
    current_user: User = Depends(get_current_user)
):
    """Submit a new task for execution."""
    try:
        # Validate task name
        registered_tasks = celery_manager.get_registered_tasks()
        all_tasks = []
        for worker_tasks in registered_tasks.values():
            all_tasks.extend(worker_tasks)
        
        if request.task_name not in all_tasks:
            raise HTTPException(
                status_code=400, 
                detail=f"Task '{request.task_name}' is not registered"
            )
        
        # Submit task
        task_kwargs = {
            "args": request.args,
            "kwargs": request.kwargs,
            "queue": request.queue
        }
        
        if request.countdown:
            task_kwargs["countdown"] = request.countdown
        
        if request.eta:
            from datetime import datetime
            task_kwargs["eta"] = datetime.fromisoformat(request.eta)
        
        result = celery_app.send_task(request.task_name, **task_kwargs)
        
        logger.info(f"Task {request.task_name} submitted by user {current_user.id} with ID {result.id}")
        
        return TaskResponse(
            task_id=result.id,
            status="PENDING",
            message=f"Task {request.task_name} submitted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit task {request.task_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit task")


@router.post("/{task_id}/revoke", response_model=TaskResponse)
async def revoke_task(
    task_id: str,
    terminate: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Revoke a task."""
    try:
        success = celery_manager.revoke_task(task_id, terminate=terminate)
        
        if success:
            action = "terminated" if terminate else "revoked"
            logger.info(f"Task {task_id} {action} by user {current_user.id}")
            return TaskResponse(
                task_id=task_id,
                status="REVOKED",
                message=f"Task {action} successfully"
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to revoke task")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke task")


@router.post("/{task_id}/retry", response_model=TaskResponse)
async def retry_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Retry a failed task."""
    try:
        success = celery_manager.retry_failed_task(task_id)
        
        if success:
            logger.info(f"Task {task_id} queued for retry by user {current_user.id}")
            return TaskResponse(
                task_id=task_id,
                status="RETRY",
                message="Task queued for retry"
            )
        else:
            raise HTTPException(status_code=400, detail="Task is not in failed state or retry failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retry task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retry task")


@router.delete("/purge")
async def purge_queue(
    queue: str = "celery",
    current_user: User = Depends(get_current_user)
):
    """Purge all tasks from a queue."""
    try:
        purged = celery_manager.purge_queue(queue)
        logger.warning(f"Queue '{queue}' purged by user {current_user.id}, {purged} tasks removed")
        
        return {
            "message": f"Purged {purged} tasks from queue '{queue}'",
            "queue": queue,
            "tasks_purged": purged
        }
        
    except Exception as e:
        logger.error(f"Failed to purge queue {queue}: {e}")
        raise HTTPException(status_code=500, detail="Failed to purge queue")


# User-specific task endpoints
@router.post("/learning-path/generate", response_model=TaskResponse)
async def generate_learning_path(
    goals: List[str],
    preferences: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Generate a learning path for the current user."""
    try:
        result = celery_app.send_task(
            "app.celery.tasks.path_generation.generate_learning_path",
            args=[str(current_user.id), goals, preferences]
        )
        
        logger.info(f"Learning path generation started for user {current_user.id}")
        
        return TaskResponse(
            task_id=result.id,
            status="PENDING",
            message="Learning path generation started"
        )
        
    except Exception as e:
        logger.error(f"Failed to start learning path generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to start learning path generation")


@router.post("/integrations/sync", response_model=TaskResponse)
async def sync_integrations(
    current_user: User = Depends(get_current_user)
):
    """Sync all integrations for the current user."""
    try:
        # Start Google Calendar sync
        calendar_result = celery_app.send_task(
            "app.celery.tasks.integration_sync.sync_google_calendar",
            args=[str(current_user.id)]
        )
        
        # Start Notion sync
        notion_result = celery_app.send_task(
            "app.celery.tasks.integration_sync.sync_notion_workspace",
            args=[str(current_user.id)]
        )
        
        logger.info(f"Integration sync started for user {current_user.id}")
        
        return {
            "message": "Integration sync started",
            "calendar_task_id": calendar_result.id,
            "notion_task_id": notion_result.id
        }
        
    except Exception as e:
        logger.error(f"Failed to start integration sync: {e}")
        raise HTTPException(status_code=500, detail="Failed to start integration sync")


@router.post("/analytics/generate", response_model=TaskResponse)
async def generate_user_analytics(
    current_user: User = Depends(get_current_user)
):
    """Generate analytics for the current user."""
    try:
        # Start performance metrics calculation
        metrics_result = celery_app.send_task(
            "app.celery.tasks.analytics.calculate_user_performance_metrics",
            args=[str(current_user.id)]
        )
        
        # Start insights generation
        insights_result = celery_app.send_task(
            "app.celery.tasks.analytics.generate_learning_insights",
            args=[str(current_user.id)]
        )
        
        logger.info(f"Analytics generation started for user {current_user.id}")
        
        return {
            "message": "Analytics generation started",
            "metrics_task_id": metrics_result.id,
            "insights_task_id": insights_result.id
        }
        
    except Exception as e:
        logger.error(f"Failed to start analytics generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to start analytics generation")