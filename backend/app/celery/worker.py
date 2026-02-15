"""
Celery worker configuration and task definitions.
"""

from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "adaptive_learning_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.celery.tasks.resource_curation",
        "app.celery.tasks.path_generation", 
        "app.celery.tasks.integration_sync",
        "app.celery.tasks.analytics",
        "app.celery.tasks.schedule_optimization",
        "app.celery.tasks.monitoring"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    "sync-integrations": {
        "task": "app.celery.tasks.integration_sync.sync_all_integrations",
        "schedule": 300.0,  # Every 5 minutes
    },
    "update-analytics": {
        "task": "app.celery.tasks.analytics.update_daily_analytics",
        "schedule": 3600.0,  # Every hour
    },
    "curate-new-resources": {
        "task": "app.celery.tasks.resource_curation.discover_new_resources",
        "schedule": 1800.0,  # Every 30 minutes
    },
    "update-resource-quality": {
        "task": "app.celery.tasks.resource_curation.update_resource_quality_scores",
        "schedule": 7200.0,  # Every 2 hours
    },
    "refresh-tokens": {
        "task": "app.celery.tasks.integration_sync.refresh_integration_tokens",
        "schedule": 21600.0,  # Every 6 hours
    },
    "update-resource-analytics": {
        "task": "app.celery.tasks.analytics.update_resource_analytics",
        "schedule": 14400.0,  # Every 4 hours
    },
    "generate-health-report": {
        "task": "app.celery.tasks.analytics.generate_system_health_report",
        "schedule": 86400.0,  # Daily
    },
    "cleanup-old-data": {
        "task": "app.celery.tasks.analytics.cleanup_old_analytics_data",
        "schedule": 604800.0,  # Weekly
    },
    "optimize-weekly-schedules": {
        "task": "app.celery.tasks.schedule_optimization.optimize_weekly_schedules",
        "schedule": 604800.0,  # Weekly (Sunday)
    },
    "detect-schedule-conflicts": {
        "task": "app.celery.tasks.schedule_optimization.detect_schedule_conflicts",
        "schedule": 3600.0,  # Every hour
    },
    "update-velocity-metrics": {
        "task": "app.celery.tasks.schedule_optimization.update_learning_velocity_metrics",
        "schedule": 86400.0,  # Daily
    },
    "refresh-resource-metadata": {
        "task": "app.celery.tasks.resource_curation.refresh_resource_metadata",
        "schedule": 43200.0,  # Every 12 hours
    },
    "monitor-task-health": {
        "task": "app.celery.tasks.monitoring.monitor_task_health",
        "schedule": 1800.0,  # Every 30 minutes
    },
    "handle-failed-tasks": {
        "task": "app.celery.tasks.monitoring.handle_failed_tasks",
        "schedule": 3600.0,  # Every hour
    },
    "cleanup-stale-tasks": {
        "task": "app.celery.tasks.monitoring.cleanup_stale_tasks",
        "schedule": 7200.0,  # Every 2 hours
    },
    "monitor-resource-usage": {
        "task": "app.celery.tasks.monitoring.monitor_resource_usage",
        "schedule": 900.0,  # Every 15 minutes
    },
    "generate-performance-insights": {
        "task": "app.celery.tasks.monitoring.generate_performance_insights",
        "schedule": 86400.0,  # Daily
    },
}