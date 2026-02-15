"""
Celery management utilities for monitoring and controlling background jobs.
"""

from celery import current_app
from app.celery.worker import celery_app
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CeleryManager:
    """Utility class for managing Celery tasks and workers."""
    
    def __init__(self):
        self.app = celery_app
    
    def get_active_tasks(self) -> Dict[str, List[Dict]]:
        """Get all currently active tasks across all workers."""
        try:
            inspect = self.app.control.inspect()
            active_tasks = inspect.active()
            return active_tasks or {}
        except Exception as e:
            logger.error(f"Failed to get active tasks: {e}")
            return {}
    
    def get_scheduled_tasks(self) -> Dict[str, List[Dict]]:
        """Get all scheduled (pending) tasks."""
        try:
            inspect = self.app.control.inspect()
            scheduled_tasks = inspect.scheduled()
            return scheduled_tasks or {}
        except Exception as e:
            logger.error(f"Failed to get scheduled tasks: {e}")
            return {}
    
    def get_worker_stats(self) -> Dict[str, Dict]:
        """Get statistics for all workers."""
        try:
            inspect = self.app.control.inspect()
            stats = inspect.stats()
            return stats or {}
        except Exception as e:
            logger.error(f"Failed to get worker stats: {e}")
            return {}
    
    def get_registered_tasks(self) -> Dict[str, List[str]]:
        """Get all registered tasks for each worker."""
        try:
            inspect = self.app.control.inspect()
            registered = inspect.registered()
            return registered or {}
        except Exception as e:
            logger.error(f"Failed to get registered tasks: {e}")
            return {}
    
    def revoke_task(self, task_id: str, terminate: bool = False) -> bool:
        """Revoke a specific task."""
        try:
            self.app.control.revoke(task_id, terminate=terminate)
            logger.info(f"Task {task_id} revoked (terminate={terminate})")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke task {task_id}: {e}")
            return False
    
    def purge_queue(self, queue_name: str = None) -> int:
        """Purge all tasks from a queue."""
        try:
            if queue_name:
                purged = self.app.control.purge()
            else:
                purged = self.app.control.purge()
            logger.info(f"Purged {purged} tasks from queue")
            return purged
        except Exception as e:
            logger.error(f"Failed to purge queue: {e}")
            return 0
    
    def get_task_result(self, task_id: str) -> Optional[Dict]:
        """Get result of a completed task."""
        try:
            result = self.app.AsyncResult(task_id)
            return {
                "task_id": task_id,
                "status": result.status,
                "result": result.result,
                "traceback": result.traceback,
                "date_done": result.date_done
            }
        except Exception as e:
            logger.error(f"Failed to get task result for {task_id}: {e}")
            return None
    
    def get_task_info(self, task_id: str) -> Optional[Dict]:
        """Get detailed information about a task."""
        try:
            result = self.app.AsyncResult(task_id)
            return {
                "task_id": task_id,
                "status": result.status,
                "result": result.result,
                "info": result.info,
                "traceback": result.traceback,
                "date_done": result.date_done,
                "successful": result.successful(),
                "failed": result.failed(),
                "ready": result.ready()
            }
        except Exception as e:
            logger.error(f"Failed to get task info for {task_id}: {e}")
            return None
    
    def get_queue_length(self, queue_name: str = "celery") -> int:
        """Get the number of tasks in a specific queue."""
        try:
            # This requires Redis connection
            from app.core.redis import get_redis
            import asyncio
            
            async def _get_length():
                redis = await get_redis()
                return await redis.llen(queue_name)
            
            return asyncio.run(_get_length())
        except Exception as e:
            logger.error(f"Failed to get queue length for {queue_name}: {e}")
            return 0
    
    def get_failed_tasks(self, limit: int = 100) -> List[Dict]:
        """Get recently failed tasks."""
        try:
            # This would require implementing a failed task tracking mechanism
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Failed to get failed tasks: {e}")
            return []
    
    def retry_failed_task(self, task_id: str) -> bool:
        """Retry a failed task."""
        try:
            result = self.app.AsyncResult(task_id)
            if result.failed():
                # Get original task info and retry
                result.retry()
                logger.info(f"Task {task_id} queued for retry")
                return True
            else:
                logger.warning(f"Task {task_id} is not in failed state")
                return False
        except Exception as e:
            logger.error(f"Failed to retry task {task_id}: {e}")
            return False
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        try:
            stats = self.get_worker_stats()
            active = self.get_active_tasks()
            scheduled = self.get_scheduled_tasks()
            
            total_workers = len(stats)
            total_active_tasks = sum(len(tasks) for tasks in active.values())
            total_scheduled_tasks = sum(len(tasks) for tasks in scheduled.values())
            
            # Calculate average load
            total_load = 0
            for worker_stats in stats.values():
                if 'rusage' in worker_stats:
                    total_load += worker_stats['rusage'].get('utime', 0)
            
            avg_load = total_load / total_workers if total_workers > 0 else 0
            
            return {
                "timestamp": datetime.now().isoformat(),
                "workers": {
                    "total": total_workers,
                    "active": len([w for w in stats.values() if w.get('pool', {}).get('processes')]),
                },
                "tasks": {
                    "active": total_active_tasks,
                    "scheduled": total_scheduled_tasks,
                },
                "performance": {
                    "average_load": avg_load,
                    "memory_usage": "N/A",  # Would need to implement
                },
                "health_score": min(1.0, max(0.0, 1.0 - (total_active_tasks / 100)))
            }
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "health_score": 0.0
            }


# Global manager instance
celery_manager = CeleryManager()


def schedule_periodic_cleanup():
    """Schedule periodic cleanup tasks."""
    try:
        # Schedule analytics cleanup for every Sunday at 2 AM
        celery_app.conf.beat_schedule.update({
            "weekly-analytics-cleanup": {
                "task": "app.celery.tasks.analytics.cleanup_old_analytics_data",
                "schedule": 604800.0,  # Weekly (7 days * 24 hours * 60 minutes * 60 seconds)
            },
            "daily-health-report": {
                "task": "app.celery.tasks.analytics.generate_system_health_report",
                "schedule": 86400.0,  # Daily
            },
            "token-refresh": {
                "task": "app.celery.tasks.integration_sync.refresh_integration_tokens",
                "schedule": 21600.0,  # Every 6 hours
            }
        })
        logger.info("Periodic cleanup tasks scheduled")
    except Exception as e:
        logger.error(f"Failed to schedule periodic cleanup: {e}")


def get_task_monitoring_data() -> Dict[str, Any]:
    """Get comprehensive task monitoring data for dashboards."""
    try:
        manager = celery_manager
        
        return {
            "active_tasks": manager.get_active_tasks(),
            "scheduled_tasks": manager.get_scheduled_tasks(),
            "worker_stats": manager.get_worker_stats(),
            "system_health": manager.get_system_health(),
            "registered_tasks": manager.get_registered_tasks(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get monitoring data: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}