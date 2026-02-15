"""
Background tasks for learning schedule optimization and management.
"""

from celery import current_task
from app.celery.worker import celery_app
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def optimize_weekly_schedules(self):
    """Optimize weekly schedules for all active users."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 5, "total": 100, "status": "Fetching users for weekly optimization"}
        )
        
        # Get all users with active learning paths
        active_users = _get_users_with_active_paths()
        
        optimized_count = 0
        failed_count = 0
        
        for i, user_data in enumerate(active_users):
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "current": 10 + (i * 80 // len(active_users)),
                    "total": 100,
                    "status": f"Optimizing schedule for user {i+1}/{len(active_users)}"
                }
            )
            
            try:
                # Optimize schedule for each user
                optimization_result = _optimize_user_weekly_schedule(user_data)
                if optimization_result["success"]:
                    optimized_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Failed to optimize schedule for user {user_data['id']}: {e}")
                failed_count += 1
        
        logger.info(f"Weekly schedule optimization completed: {optimized_count} optimized, {failed_count} failed")
        return {
            "status": "completed",
            "users_processed": len(active_users),
            "optimized_count": optimized_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Weekly schedule optimization failed: {e}")
        raise


@celery_app.task(bind=True)
def detect_schedule_conflicts(self):
    """Detect and resolve schedule conflicts for all users."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 5, "total": 100, "status": "Scanning for schedule conflicts"}
        )
        
        # Get all scheduled learning sessions
        scheduled_sessions = _get_all_scheduled_sessions()
        
        conflicts_detected = []
        conflicts_resolved = 0
        
        for i, session in enumerate(scheduled_sessions):
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "current": 10 + (i * 70 // len(scheduled_sessions)),
                    "total": 100,
                    "status": f"Checking session {i+1}/{len(scheduled_sessions)}"
                }
            )
            
            # Check for conflicts with calendar events
            conflicts = _check_session_conflicts(session)
            
            if conflicts:
                conflicts_detected.extend(conflicts)
                
                # Attempt to resolve conflicts
                resolution_result = _resolve_session_conflicts(session, conflicts)
                if resolution_result["resolved"]:
                    conflicts_resolved += 1
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Finalizing conflict resolution"}
        )
        
        # Notify users of significant changes
        _notify_users_of_schedule_changes(conflicts_detected)
        
        logger.info(f"Conflict detection completed: {len(conflicts_detected)} conflicts found, {conflicts_resolved} resolved")
        return {
            "status": "completed",
            "sessions_checked": len(scheduled_sessions),
            "conflicts_detected": len(conflicts_detected),
            "conflicts_resolved": conflicts_resolved
        }
        
    except Exception as e:
        logger.error(f"Schedule conflict detection failed: {e}")
        raise


@celery_app.task(bind=True)
def update_learning_velocity_metrics(self):
    """Update learning velocity metrics for schedule optimization."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 5, "total": 100, "status": "Fetching user learning data"}
        )
        
        # Get all users with learning activity
        users_with_activity = _get_users_with_recent_activity()
        
        updated_count = 0
        
        for i, user_data in enumerate(users_with_activity):
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "current": 10 + (i * 80 // len(users_with_activity)),
                    "total": 100,
                    "status": f"Updating metrics for user {i+1}/{len(users_with_activity)}"
                }
            )
            
            # Calculate learning velocity metrics
            velocity_metrics = _calculate_learning_velocity(user_data)
            
            # Update user profile with new metrics
            _update_user_velocity_metrics(user_data["id"], velocity_metrics)
            updated_count += 1
        
        logger.info(f"Learning velocity metrics updated for {updated_count} users")
        return {
            "status": "completed",
            "users_processed": len(users_with_activity),
            "metrics_updated": updated_count
        }
        
    except Exception as e:
        logger.error(f"Learning velocity metrics update failed: {e}")
        raise


@celery_app.task(bind=True)
def generate_schedule_recommendations(self, user_id: str):
    """Generate personalized schedule recommendations for a user."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 10, "total": 100, "status": "Analyzing user patterns"}
        )
        
        # Get user data and learning history
        user_data = _get_comprehensive_user_data(user_id)
        learning_history = _get_user_learning_history(user_id)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 30, "total": 100, "status": "Analyzing performance patterns"}
        )
        
        # Analyze performance patterns
        performance_analysis = _analyze_user_performance_patterns(learning_history)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 60, "total": 100, "status": "Generating recommendations"}
        )
        
        # Generate recommendations
        recommendations = _generate_personalized_recommendations(
            user_data, performance_analysis
        )
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 85, "total": 100, "status": "Saving recommendations"}
        )
        
        # Save recommendations
        _save_schedule_recommendations(user_id, recommendations)
        
        logger.info(f"Schedule recommendations generated for user {user_id}")
        return {
            "status": "completed",
            "user_id": user_id,
            "recommendations_count": len(recommendations),
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Schedule recommendations generation failed for user {user_id}: {e}")
        raise


@celery_app.task(bind=True)
def optimize_session_spacing(self, user_id: str, path_id: str):
    """Optimize spacing between learning sessions for better retention."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 10, "total": 100, "status": "Analyzing current session spacing"}
        )
        
        # Get current schedule and user performance data
        current_schedule = _get_current_schedule(user_id, path_id)
        retention_data = _get_user_retention_data(user_id)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 40, "total": 100, "status": "Calculating optimal spacing"}
        )
        
        # Calculate optimal spacing using spaced repetition principles
        optimal_spacing = _calculate_optimal_session_spacing(
            current_schedule, retention_data
        )
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 70, "total": 100, "status": "Applying spacing optimization"}
        )
        
        # Apply spacing optimization
        optimized_schedule = _apply_spacing_optimization(
            current_schedule, optimal_spacing
        )
        
        # Update schedule in database
        _update_learning_schedule(path_id, optimized_schedule)
        
        logger.info(f"Session spacing optimized for user {user_id}, path {path_id}")
        return {
            "status": "completed",
            "user_id": user_id,
            "path_id": path_id,
            "sessions_optimized": len(optimized_schedule),
            "average_spacing_improvement": _calculate_spacing_improvement(
                current_schedule, optimized_schedule
            )
        }
        
    except Exception as e:
        logger.error(f"Session spacing optimization failed: {e}")
        raise


# Helper functions for schedule optimization

def _get_users_with_active_paths() -> List[Dict]:
    """Get all users with active learning paths."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.learning_path import LearningPath
        from sqlalchemy import select, distinct
        import asyncio
        
        async def get_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(distinct(LearningPath.user_id)).where(
                        LearningPath.status == "active"
                    )
                )
                user_ids = result.scalars().all()
                
                users = []
                for user_id in user_ids:
                    paths_result = await session.execute(
                        select(LearningPath.id).where(
                            LearningPath.user_id == user_id,
                            LearningPath.status == "active"
                        )
                    )
                    path_ids = [p for p in paths_result.scalars().all()]
                    users.append({"id": user_id, "active_paths": path_ids})
                
                return users
        
        return asyncio.run(get_async())
    except Exception as e:
        logger.error(f"Failed to get users with active paths: {e}")
        return []


def _optimize_user_weekly_schedule(user_data: Dict) -> Dict:
    """Optimize weekly schedule for a specific user."""
    try:
        from app.agents.schedule_optimizer import ScheduleOptimizer
        import asyncio
        
        async def optimize_async():
            optimizer = ScheduleOptimizer()
            result = await optimizer.execute_task({
                "type": "optimize_weekly_schedule",
                "user_id": user_data["id"],
                "active_paths": user_data.get("active_paths", [])
            })
            return {"success": True, "changes_made": len(result.get("adjustments", []))}
        
        return asyncio.run(optimize_async())
    except Exception as e:
        logger.error(f"Failed to optimize weekly schedule for user {user_data['id']}: {e}")
        return {"success": False, "error": str(e)}


def _get_all_scheduled_sessions() -> List[Dict]:
    """Get all scheduled learning sessions."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.progress import LearningSession
        from sqlalchemy import select
        from datetime import datetime
        import asyncio
        
        async def get_async():
            async with AsyncSessionLocal() as session:
                # Get future sessions
                result = await session.execute(
                    select(LearningSession).where(
                        LearningSession.scheduled_time > datetime.now()
                    ).limit(1000)
                )
                sessions = result.scalars().all()
                
                return [
                    {
                        "id": s.id,
                        "user_id": s.user_id,
                        "scheduled_time": s.scheduled_time,
                        "duration": s.duration_minutes,
                        "milestone_id": s.milestone_id
                    }
                    for s in sessions
                ]
        
        return asyncio.run(get_async())
    except Exception as e:
        logger.error(f"Failed to get scheduled sessions: {e}")
        return []


def _check_session_conflicts(session: Dict) -> List[Dict]:
    """Check for conflicts with a learning session."""
    try:
        from app.integrations.google_calendar import GoogleCalendarClient
        from app.core.database import AsyncSessionLocal
        from app.models.integration import Integration
        from sqlalchemy import select, and_
        import asyncio
        
        async def check_async():
            async with AsyncSessionLocal() as db_session:
                # Get user's calendar integration
                result = await db_session.execute(
                    select(Integration).where(
                        and_(
                            Integration.user_id == session["user_id"],
                            Integration.integration_type == "google_calendar",
                            Integration.is_active == True
                        )
                    )
                )
                integration = result.scalar_one_or_none()
                
                if not integration:
                    return []
                
                # Check calendar for conflicts
                calendar_client = GoogleCalendarClient(
                    access_token=integration.credentials.get("access_token", ""),
                    refresh_token=integration.credentials.get("refresh_token", "")
                )
                
                scheduled_time = session["scheduled_time"]
                duration = session["duration"]
                end_time = scheduled_time + timedelta(minutes=duration)
                
                events = calendar_client.list_events(
                    calendar_id="primary",
                    time_min=scheduled_time.isoformat() + "Z",
                    time_max=end_time.isoformat() + "Z"
                )
                
                return [
                    {
                        "event_id": event.get("id"),
                        "summary": event.get("summary"),
                        "start": event.get("start", {}).get("dateTime"),
                        "end": event.get("end", {}).get("dateTime")
                    }
                    for event in events
                ]
        
        return asyncio.run(check_async())
    except Exception as e:
        logger.error(f"Failed to check session conflicts: {e}")
        return []


def _resolve_session_conflicts(session: Dict, conflicts: List[Dict]) -> Dict:
    """Resolve conflicts for a learning session."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.progress import LearningSession
        from sqlalchemy import select
        import asyncio
        
        async def resolve_async():
            async with AsyncSessionLocal() as db_session:
                result = await db_session.execute(
                    select(LearningSession).where(LearningSession.id == session["id"])
                )
                learning_session = result.scalar_one_or_none()
                
                if not learning_session:
                    return {"resolved": False}
                
                # Find next available slot (1 hour later)
                new_time = session["scheduled_time"] + timedelta(hours=1)
                learning_session.scheduled_time = new_time
                
                await db_session.commit()
                
                return {"resolved": True, "new_time": new_time}
        
        return asyncio.run(resolve_async())
    except Exception as e:
        logger.error(f"Failed to resolve session conflicts: {e}")
        return {"resolved": False, "error": str(e)}


def _notify_users_of_schedule_changes(conflicts: List[Dict]):
    """Notify users of significant schedule changes."""
    try:
        # Group conflicts by user
        user_conflicts = {}
        for conflict in conflicts:
            user_id = conflict.get("user_id")
            if user_id not in user_conflicts:
                user_conflicts[user_id] = []
            user_conflicts[user_id].append(conflict)
        
        # Send notifications (placeholder for notification system)
        for user_id, user_conflict_list in user_conflicts.items():
            logger.info(f"Notifying user {user_id} of {len(user_conflict_list)} schedule changes")
            # TODO: Integrate with notification system (email, push, etc.)
    except Exception as e:
        logger.error(f"Failed to notify users: {e}")
        pass


def _get_users_with_recent_activity() -> List[Dict]:
    """Get users with recent learning activity."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.progress import LearningSession
        from sqlalchemy import select, distinct, func
        from datetime import datetime, timedelta
        import asyncio
        
        async def get_async():
            async with AsyncSessionLocal() as session:
                cutoff_date = datetime.now() - timedelta(days=7)
                result = await session.execute(
                    select(
                        LearningSession.user_id,
                        func.max(LearningSession.completed_at).label("last_activity")
                    ).where(
                        LearningSession.completed_at > cutoff_date
                    ).group_by(LearningSession.user_id)
                )
                
                return [
                    {"id": row.user_id, "last_activity": row.last_activity}
                    for row in result
                ]
        
        return asyncio.run(get_async())
    except Exception as e:
        logger.error(f"Failed to get users with recent activity: {e}")
        return []


def _calculate_learning_velocity(user_data: Dict) -> Dict:
    """Calculate learning velocity metrics for a user."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.progress import LearningSession, TaskCompletion
        from sqlalchemy import select, func
        from datetime import datetime, timedelta
        import asyncio
        
        async def calculate_async():
            async with AsyncSessionLocal() as session:
                user_id = user_data["id"]
                week_ago = datetime.now() - timedelta(days=7)
                
                # Get sessions in last week
                sessions_result = await session.execute(
                    select(LearningSession).where(
                        LearningSession.user_id == user_id,
                        LearningSession.completed_at > week_ago
                    )
                )
                sessions = sessions_result.scalars().all()
                
                # Get task completions
                tasks_result = await session.execute(
                    select(func.count(TaskCompletion.id)).where(
                        TaskCompletion.user_id == user_id,
                        TaskCompletion.completed_at > week_ago
                    )
                )
                tasks_count = tasks_result.scalar()
                
                total_hours = sum(s.duration_minutes for s in sessions) / 60 if sessions else 0
                
                return {
                    "tasks_per_hour": tasks_count / total_hours if total_hours > 0 else 0,
                    "concepts_mastered_per_week": tasks_count,
                    "retention_rate": 0.85,  # Placeholder
                    "optimal_session_length": 75
                }
        
        return asyncio.run(calculate_async())
    except Exception as e:
        logger.error(f"Failed to calculate learning velocity: {e}")
        return {
            "tasks_per_hour": 1.5,
            "concepts_mastered_per_week": 8,
            "retention_rate": 0.85,
            "optimal_session_length": 75
        }


def _update_user_velocity_metrics(user_id: str, metrics: Dict):
    """Update user velocity metrics in database."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.user import UserProfile
        from sqlalchemy import select
        import asyncio
        
        async def update_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(UserProfile).where(UserProfile.id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if user:
                    if not user.metadata:
                        user.metadata = {}
                    user.metadata["velocity_metrics"] = metrics
                    user.metadata["velocity_updated_at"] = datetime.now().isoformat()
                    await session.commit()
        
        asyncio.run(update_async())
    except Exception as e:
        logger.error(f"Failed to update velocity metrics: {e}")
        pass


def _get_comprehensive_user_data(user_id: str) -> Dict:
    """Get comprehensive user data for recommendations."""
    # TODO: Implement database query
    return {
        "id": user_id,
        "learning_style": "visual",
        "preferred_times": ["morning", "evening"],
        "attention_span": 90,  # minutes
        "current_goals": ["python", "web development"]
    }


def _get_user_learning_history(user_id: str) -> List[Dict]:
    """Get user's learning history."""
    # TODO: Implement database query
    return [
        {
            "session_date": datetime.now() - timedelta(days=1),
            "duration": 60,
            "tasks_completed": 3,
            "performance_score": 0.8
        }
    ]


def _analyze_user_performance_patterns(history: List[Dict]) -> Dict:
    """Analyze user performance patterns."""
    # TODO: Implement pattern analysis algorithm
    return {
        "peak_performance_times": [9, 10, 11],
        "optimal_session_length": 75,
        "best_days": ["monday", "tuesday", "wednesday"],
        "learning_curve": "steady"
    }


def _generate_personalized_recommendations(user_data: Dict, analysis: Dict) -> List[Dict]:
    """Generate personalized schedule recommendations."""
    recommendations = []
    
    # Example recommendations based on analysis
    if analysis["optimal_session_length"] > user_data.get("attention_span", 60):
        recommendations.append({
            "type": "session_length",
            "recommendation": "Consider shorter sessions for better focus",
            "suggested_length": user_data.get("attention_span", 60),
            "confidence": 0.8
        })
    
    if "morning" in analysis["peak_performance_times"]:
        recommendations.append({
            "type": "timing",
            "recommendation": "Schedule important topics in the morning",
            "suggested_times": analysis["peak_performance_times"],
            "confidence": 0.9
        })
    
    return recommendations


def _save_schedule_recommendations(user_id: str, recommendations: List[Dict]):
    """Save schedule recommendations to database."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.user import UserProfile
        from sqlalchemy import select
        import asyncio
        
        async def save_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(UserProfile).where(UserProfile.id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if user:
                    if not user.metadata:
                        user.metadata = {}
                    user.metadata["schedule_recommendations"] = recommendations
                    user.metadata["recommendations_generated_at"] = datetime.now().isoformat()
                    await session.commit()
        
        asyncio.run(save_async())
    except Exception as e:
        logger.error(f"Failed to save schedule recommendations: {e}")
        pass


def _get_current_schedule(user_id: str, path_id: str) -> List[Dict]:
    """Get current learning schedule."""
    # TODO: Implement database query
    return [
        {
            "session_id": "session1",
            "scheduled_time": datetime.now() + timedelta(days=1),
            "duration": 60,
            "topics": ["variables", "functions"]
        }
    ]


def _get_user_retention_data(user_id: str) -> Dict:
    """Get user retention data for spacing optimization."""
    # TODO: Implement database query and analysis
    return {
        "average_retention_rate": 0.75,
        "forgetting_curve": "exponential",
        "optimal_review_intervals": [1, 3, 7, 14]  # days
    }


def _calculate_optimal_session_spacing(schedule: List[Dict], retention_data: Dict) -> Dict:
    """Calculate optimal spacing between sessions."""
    # TODO: Implement spaced repetition algorithm
    return {
        "recommended_intervals": [1, 2, 4, 7, 14],  # days
        "spacing_strategy": "exponential_backoff"
    }


def _apply_spacing_optimization(schedule: List[Dict], spacing: Dict) -> List[Dict]:
    """Apply spacing optimization to schedule."""
    # TODO: Implement spacing application algorithm
    optimized_schedule = schedule.copy()
    
    # Apply spacing recommendations
    for i, session in enumerate(optimized_schedule):
        if i > 0:
            # Adjust spacing based on recommendations
            previous_session = optimized_schedule[i-1]
            recommended_interval = spacing["recommended_intervals"][min(i-1, len(spacing["recommended_intervals"])-1)]
            
            # Update session time
            session["scheduled_time"] = previous_session["scheduled_time"] + timedelta(days=recommended_interval)
    
    return optimized_schedule


def _update_learning_schedule(path_id: str, schedule: List[Dict]):
    """Update learning schedule in database."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.learning_path import LearningPath
        from sqlalchemy import select
        import asyncio
        
        async def update_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(LearningPath).where(LearningPath.id == path_id)
                )
                path = result.scalar_one_or_none()
                
                if path:
                    if not path.metadata:
                        path.metadata = {}
                    path.metadata["optimized_schedule"] = schedule
                    path.metadata["schedule_updated_at"] = datetime.now().isoformat()
                    await session.commit()
        
        asyncio.run(update_async())
    except Exception as e:
        logger.error(f"Failed to update learning schedule: {e}")
        pass


def _calculate_spacing_improvement(old_schedule: List[Dict], new_schedule: List[Dict]) -> float:
    """Calculate improvement in session spacing."""
    # TODO: Implement improvement calculation
    return 0.15  # 15% improvement