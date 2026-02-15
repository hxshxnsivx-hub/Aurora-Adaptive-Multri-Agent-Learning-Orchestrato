"""
Background tasks for resource curation and discovery.
"""

from celery import current_task
from app.celery.worker import celery_app
from app.core.config import settings
import logging
import httpx
import asyncio
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def discover_new_resources(self, topics: list = None):
    """Discover and curate new educational resources from multiple sources."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Starting resource discovery"}
        )
        
        if not topics:
            topics = [
                "python programming", "machine learning", "web development",
                "data structures", "algorithms", "system design"
            ]
        
        all_resources = []
        total_sources = 4  # YouTube, GitHub, Articles, Courses
        
        for i, topic in enumerate(topics):
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "current": 10 + (i * 80 // len(topics)),
                    "total": 100,
                    "status": f"Discovering resources for: {topic}"
                }
            )
            
            # Discover from multiple sources
            topic_resources = []
            
            # YouTube resources
            youtube_resources = _discover_youtube_resources(topic)
            topic_resources.extend(youtube_resources)
            
            # GitHub repositories
            github_resources = _discover_github_resources(topic)
            topic_resources.extend(github_resources)
            
            # Articles and tutorials
            article_resources = _discover_article_resources(topic)
            topic_resources.extend(article_resources)
            
            # Course platforms
            course_resources = _discover_course_resources(topic)
            topic_resources.extend(course_resources)
            
            all_resources.extend(topic_resources)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Ranking and filtering resources"}
        )
        
        # Rank and filter resources
        ranked_resources = _rank_and_filter_resources(all_resources)
        
        # Store resources in database
        stored_count = _store_resources(ranked_resources)
        
        logger.info(f"Resource discovery completed: {stored_count} resources stored")
        return {
            "status": "completed",
            "resources_found": len(all_resources),
            "resources_stored": stored_count,
            "topics_processed": len(topics)
        }
        
    except Exception as e:
        logger.error(f"Resource discovery failed: {e}")
        raise


@celery_app.task(bind=True)
def curate_resources_for_milestone(self, milestone_id: str):
    """Curate resources for a specific milestone."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Analyzing milestone requirements"}
        )
        
        # TODO: Fetch milestone from database
        milestone_data = _get_milestone_data(milestone_id)
        
        if not milestone_data:
            raise ValueError(f"Milestone {milestone_id} not found")
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 20, "total": 100, "status": "Searching relevant resources"}
        )
        
        # Extract topics and requirements from milestone
        topics = milestone_data.get("topics", [])
        difficulty_level = milestone_data.get("difficulty_level", "intermediate")
        learning_objectives = milestone_data.get("learning_objectives", [])
        
        # Search for resources matching milestone requirements
        relevant_resources = []
        
        for topic in topics:
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "current": 20 + (len(relevant_resources) * 60 // len(topics)),
                    "total": 100,
                    "status": f"Curating resources for: {topic}"
                }
            )
            
            # Search existing resources
            existing_resources = _search_existing_resources(topic, difficulty_level)
            relevant_resources.extend(existing_resources)
            
            # Discover new resources if needed
            if len(existing_resources) < 5:  # Need more resources
                new_resources = _discover_topic_specific_resources(topic, difficulty_level)
                relevant_resources.extend(new_resources)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 80, "total": 100, "status": "Ranking and selecting best resources"}
        )
        
        # Rank resources based on relevance and quality
        ranked_resources = _rank_resources_for_milestone(
            relevant_resources, 
            milestone_data
        )
        
        # Select top resources (limit to 10 per milestone)
        selected_resources = ranked_resources[:10]
        
        # Associate resources with milestone
        _associate_resources_with_milestone(milestone_id, selected_resources)
        
        logger.info(f"Resource curation completed for milestone {milestone_id}")
        return {
            "status": "completed",
            "milestone_id": milestone_id,
            "resources_found": len(relevant_resources),
            "resources_selected": len(selected_resources)
        }
        
    except Exception as e:
        logger.error(f"Resource curation failed for milestone {milestone_id}: {e}")
        raise


@celery_app.task(bind=True)
def update_resource_quality_scores(self):
    """Update quality scores for all resources based on user feedback."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Fetching resources for quality update"}
        )
        
        # TODO: Fetch all resources from database
        resources = _get_all_resources()
        
        updated_count = 0
        total_resources = len(resources)
        
        for i, resource in enumerate(resources):
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "current": 10 + (i * 80 // total_resources),
                    "total": 100,
                    "status": f"Updating quality score for resource {i+1}/{total_resources}"
                }
            )
            
            # Calculate new quality score based on:
            # - User ratings and feedback
            # - Completion rates
            # - Time spent on resource
            # - User progress after consuming resource
            new_score = _calculate_resource_quality_score(resource)
            
            if abs(new_score - resource.get("quality_score", 0)) > 0.05:  # Significant change
                _update_resource_quality_score(resource["id"], new_score)
                updated_count += 1
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 95, "total": 100, "status": "Finalizing quality updates"}
        )
        
        logger.info(f"Quality score update completed: {updated_count} resources updated")
        return {
            "status": "completed",
            "resources_processed": total_resources,
            "resources_updated": updated_count
        }
        
    except Exception as e:
        logger.error(f"Quality score update failed: {e}")
        raise


@celery_app.task(bind=True)
def refresh_resource_metadata(self):
    """Refresh metadata for all resources from their original sources."""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Fetching resources for metadata refresh"}
        )
        
        resources = _get_resources_needing_refresh()
        refreshed_count = 0
        
        for i, resource in enumerate(resources):
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "current": 10 + (i * 80 // len(resources)),
                    "total": 100,
                    "status": f"Refreshing metadata for {resource['title']}"
                }
            )
            
            try:
                updated_metadata = _fetch_fresh_metadata(resource)
                if updated_metadata:
                    _update_resource_metadata(resource["id"], updated_metadata)
                    refreshed_count += 1
            except Exception as e:
                logger.warning(f"Failed to refresh metadata for resource {resource['id']}: {e}")
                continue
        
        logger.info(f"Metadata refresh completed: {refreshed_count} resources updated")
        return {
            "status": "completed",
            "resources_processed": len(resources),
            "resources_refreshed": refreshed_count
        }
        
    except Exception as e:
        logger.error(f"Metadata refresh failed: {e}")
        raise


# Helper functions for resource discovery

def _discover_youtube_resources(topic: str) -> List[Dict]:
    """Discover YouTube videos for a topic."""
    try:
        if not settings.YOUTUBE_API_KEY:
            logger.warning("YouTube API key not configured")
            return []
        
        # Import YouTube client
        from app.integrations.youtube import YouTubeClient
        
        youtube_client = YouTubeClient(settings.YOUTUBE_API_KEY)
        
        # Search for videos
        videos = youtube_client.search_videos(
            query=topic,
            max_results=5,
            order="relevance"
        )
        
        resources = []
        for video in videos:
            resources.append({
                "title": video.get("title", ""),
                "url": video.get("url", ""),
                "source": "youtube",
                "type": "video",
                "duration": video.get("duration", 0),
                "quality_score": _calculate_youtube_quality_score(video),
                "metadata": {
                    "views": video.get("view_count", 0),
                    "likes": video.get("like_count", 0),
                    "channel": video.get("channel_title", ""),
                    "published_date": video.get("published_at", "")
                }
            })
        
        return resources
    except Exception as e:
        logger.error(f"YouTube discovery failed for topic {topic}: {e}")
        return []


def _calculate_youtube_quality_score(video: Dict) -> float:
    """Calculate quality score for a YouTube video."""
    score = 0.5
    
    views = video.get("view_count", 0)
    likes = video.get("like_count", 0)
    
    # High view count
    if views > 100000:
        score += 0.2
    elif views > 10000:
        score += 0.1
    
    # Good like ratio
    if views > 0:
        like_ratio = likes / views
        if like_ratio > 0.05:
            score += 0.2
        elif like_ratio > 0.02:
            score += 0.1
    
    # Recent content
    published = video.get("published_at", "")
    if published:
        try:
            from datetime import datetime
            pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
            days_old = (datetime.now() - pub_date).days
            if days_old < 365:
                score += 0.1
        except:
            pass
    
    return min(score, 1.0)


def _discover_github_resources(topic: str) -> List[Dict]:
    """Discover GitHub repositories for a topic."""
    try:
        if not settings.GITHUB_TOKEN:
            logger.warning("GitHub token not configured")
            return []
        
        # Import GitHub client
        from app.integrations.github import GitHubClient
        
        github_client = GitHubClient(settings.GITHUB_TOKEN)
        
        # Search for repositories
        repos = github_client.search_repositories(
            query=topic,
            sort="stars",
            max_results=5
        )
        
        resources = []
        for repo in repos:
            resources.append({
                "title": repo.get("name", ""),
                "url": repo.get("html_url", ""),
                "source": "github",
                "type": "repository",
                "quality_score": _calculate_github_quality_score(repo),
                "metadata": {
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "language": repo.get("language", ""),
                    "updated_at": repo.get("updated_at", ""),
                    "description": repo.get("description", "")
                }
            })
        
        return resources
    except Exception as e:
        logger.error(f"GitHub discovery failed for topic {topic}: {e}")
        return []


def _calculate_github_quality_score(repo: Dict) -> float:
    """Calculate quality score for a GitHub repository."""
    score = 0.5
    
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    
    # High star count
    if stars > 5000:
        score += 0.25
    elif stars > 1000:
        score += 0.15
    elif stars > 100:
        score += 0.1
    
    # Good fork ratio
    if stars > 0:
        fork_ratio = forks / stars
        if fork_ratio > 0.1:
            score += 0.15
    
    # Recently updated
    updated = repo.get("updated_at", "")
    if updated:
        try:
            from datetime import datetime
            update_date = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            days_old = (datetime.now() - update_date).days
            if days_old < 180:
                score += 0.1
        except:
            pass
    
    return min(score, 1.0)


def _discover_article_resources(topic: str) -> List[Dict]:
    """Discover articles and tutorials for a topic."""
    try:
        if not settings.TAVILY_API_KEY:
            logger.warning("Tavily API key not configured")
            return []
        
        # Import Tavily client
        from app.integrations.tavily import TavilyClient
        
        tavily_client = TavilyClient(settings.TAVILY_API_KEY)
        
        # Search for articles
        results = tavily_client.search(
            query=f"{topic} tutorial guide",
            search_depth="advanced",
            max_results=5
        )
        
        resources = []
        for result in results:
            resources.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "source": "web",
                "type": "article",
                "quality_score": result.get("score", 0.7),
                "metadata": {
                    "content": result.get("content", ""),
                    "published_date": result.get("published_date", ""),
                    "reading_time": _estimate_reading_time(result.get("content", ""))
                }
            })
        
        return resources
    except Exception as e:
        logger.error(f"Article discovery failed for topic {topic}: {e}")
        return []


def _estimate_reading_time(content: str) -> int:
    """Estimate reading time in minutes based on content length."""
    words = len(content.split())
    # Average reading speed: 200 words per minute
    return max(1, words // 200)


def _discover_course_resources(topic: str) -> List[Dict]:
    """Discover online courses for a topic."""
    try:
        # TODO: Implement course platform APIs (Coursera, Udemy, etc.)
        # This is a placeholder implementation
        return [
            {
                "title": f"Master {topic} - Complete Course",
                "url": f"https://example-course-platform.com/course/{topic.replace(' ', '-')}",
                "source": "course_platform",
                "type": "course",
                "quality_score": 0.9,
                "metadata": {
                    "instructor": "Expert Instructor",
                    "duration": 40,  # hours
                    "students": 10000,
                    "rating": 4.5
                }
            }
        ]
    except Exception as e:
        logger.error(f"Course discovery failed for topic {topic}: {e}")
        return []


def _rank_and_filter_resources(resources: List[Dict]) -> List[Dict]:
    """Rank and filter resources based on quality and relevance."""
    try:
        # Remove duplicates based on URL
        unique_resources = {}
        for resource in resources:
            url = resource.get("url", "")
            if url and url not in unique_resources:
                unique_resources[url] = resource
        
        # Sort by quality score
        ranked_resources = sorted(
            unique_resources.values(),
            key=lambda x: x.get("quality_score", 0),
            reverse=True
        )
        
        # Filter out low-quality resources
        filtered_resources = [
            r for r in ranked_resources 
            if r.get("quality_score", 0) >= 0.6
        ]
        
        return filtered_resources
    except Exception as e:
        logger.error(f"Resource ranking failed: {e}")
        return resources


def _store_resources(resources: List[Dict]) -> int:
    """Store resources in the database."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.resource import Resource
        from sqlalchemy import select
        import asyncio
        
        async def store_async():
            stored_count = 0
            async with AsyncSessionLocal() as session:
                for resource in resources:
                    # Check if resource already exists
                    url = resource.get("url", "")
                    if not url:
                        continue
                    
                    result = await session.execute(
                        select(Resource).where(Resource.url == url)
                    )
                    existing = result.scalar_one_or_none()
                    
                    if not existing:
                        # Create new resource
                        new_resource = Resource(
                            title=resource.get("title", ""),
                            url=url,
                            resource_type=resource.get("type", "article"),
                            source=resource.get("source", "web"),
                            quality_score=resource.get("quality_score", 0.5),
                            difficulty_level=_determine_difficulty_from_metadata(resource),
                            estimated_duration=resource.get("duration", 30),
                            metadata=resource.get("metadata", {})
                        )
                        session.add(new_resource)
                        stored_count += 1
                
                await session.commit()
            return stored_count
        
        # Run async function
        return asyncio.run(store_async())
    except Exception as e:
        logger.error(f"Resource storage failed: {e}")
        return 0


def _determine_difficulty_from_metadata(resource: Dict) -> str:
    """Determine difficulty level from resource metadata."""
    title = resource.get("title", "").lower()
    
    if any(word in title for word in ["beginner", "intro", "basics", "fundamentals", "getting started"]):
        return "beginner"
    elif any(word in title for word in ["advanced", "expert", "master", "deep dive"]):
        return "advanced"
    else:
        return "intermediate"


def _get_milestone_data(milestone_id: str) -> Optional[Dict]:
    """Get milestone data from database."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.learning_path import Milestone
        from sqlalchemy import select
        import asyncio
        
        async def get_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Milestone).where(Milestone.id == milestone_id)
                )
                milestone = result.scalar_one_or_none()
                
                if not milestone:
                    return None
                
                return {
                    "id": milestone.id,
                    "topics": milestone.metadata.get("topics", []) if milestone.metadata else [],
                    "difficulty_level": milestone.difficulty_level,
                    "learning_objectives": milestone.metadata.get("learning_objectives", []) if milestone.metadata else []
                }
        
        return asyncio.run(get_async())
    except Exception as e:
        logger.error(f"Failed to get milestone data: {e}")
        return None


def _search_existing_resources(topic: str, difficulty_level: str) -> List[Dict]:
    """Search existing resources in database."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.resource import Resource
        from sqlalchemy import select, and_, or_
        import asyncio
        
        async def search_async():
            async with AsyncSessionLocal() as session:
                # Search by title, difficulty, and type
                query = select(Resource).where(
                    and_(
                        Resource.difficulty_level == difficulty_level,
                        or_(
                            Resource.title.ilike(f"%{topic}%"),
                            Resource.metadata["description"].astext.ilike(f"%{topic}%")
                        )
                    )
                ).limit(10)
                
                result = await session.execute(query)
                resources = result.scalars().all()
                
                return [
                    {
                        "id": r.id,
                        "title": r.title,
                        "url": r.url,
                        "type": r.resource_type,
                        "source": r.source,
                        "quality_score": r.quality_score,
                        "difficulty_level": r.difficulty_level,
                        "metadata": r.metadata
                    }
                    for r in resources
                ]
        
        return asyncio.run(search_async())
    except Exception as e:
        logger.error(f"Failed to search existing resources: {e}")
        return []


def _discover_topic_specific_resources(topic: str, difficulty_level: str) -> List[Dict]:
    """Discover new resources for specific topic and difficulty."""
    # Combine all discovery methods for the specific topic
    resources = []
    resources.extend(_discover_youtube_resources(f"{topic} {difficulty_level}"))
    resources.extend(_discover_github_resources(f"{topic} {difficulty_level}"))
    resources.extend(_discover_article_resources(f"{topic} {difficulty_level}"))
    resources.extend(_discover_course_resources(f"{topic} {difficulty_level}"))
    return resources


def _rank_resources_for_milestone(resources: List[Dict], milestone_data: Dict) -> List[Dict]:
    """Rank resources specifically for a milestone."""
    # TODO: Implement milestone-specific ranking algorithm
    # Consider: topic relevance, difficulty match, learning objectives alignment
    return sorted(resources, key=lambda x: x.get("quality_score", 0), reverse=True)


def _associate_resources_with_milestone(milestone_id: str, resources: List[Dict]):
    """Associate selected resources with a milestone."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.learning_path import Milestone
        from sqlalchemy import select
        import asyncio
        
        async def associate_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Milestone).where(Milestone.id == milestone_id)
                )
                milestone = result.scalar_one_or_none()
                
                if milestone:
                    # Store resource IDs in milestone metadata
                    if not milestone.metadata:
                        milestone.metadata = {}
                    
                    milestone.metadata["resource_ids"] = [r.get("id") for r in resources if r.get("id")]
                    milestone.metadata["resources"] = resources
                    
                    await session.commit()
        
        asyncio.run(associate_async())
    except Exception as e:
        logger.error(f"Failed to associate resources with milestone: {e}")
        pass


def _get_all_resources() -> List[Dict]:
    """Get all resources from database."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.resource import Resource
        from sqlalchemy import select
        import asyncio
        
        async def get_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Resource))
                resources = result.scalars().all()
                
                return [
                    {
                        "id": r.id,
                        "title": r.title,
                        "url": r.url,
                        "type": r.resource_type,
                        "source": r.source,
                        "quality_score": r.quality_score,
                        "difficulty_level": r.difficulty_level,
                        "metadata": r.metadata
                    }
                    for r in resources
                ]
        
        return asyncio.run(get_async())
    except Exception as e:
        logger.error(f"Failed to get all resources: {e}")
        return []


def _calculate_resource_quality_score(resource: Dict) -> float:
    """Calculate quality score based on user feedback and engagement."""
    # TODO: Implement quality scoring algorithm
    # Factors: user ratings, completion rates, time spent, learning outcomes
    return resource.get("quality_score", 0.7)


def _update_resource_quality_score(resource_id: str, score: float):
    """Update resource quality score in database."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.resource import Resource
        from sqlalchemy import select
        import asyncio
        
        async def update_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Resource).where(Resource.id == resource_id)
                )
                resource = result.scalar_one_or_none()
                
                if resource:
                    resource.quality_score = score
                    await session.commit()
        
        asyncio.run(update_async())
    except Exception as e:
        logger.error(f"Failed to update resource quality score: {e}")
        pass


def _get_resources_needing_refresh() -> List[Dict]:
    """Get resources that need metadata refresh."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.resource import Resource
        from sqlalchemy import select
        from datetime import datetime, timedelta
        import asyncio
        
        async def get_async():
            async with AsyncSessionLocal() as session:
                # Get resources not updated in last 7 days
                cutoff_date = datetime.now() - timedelta(days=7)
                result = await session.execute(
                    select(Resource).where(Resource.updated_at < cutoff_date).limit(100)
                )
                resources = result.scalars().all()
                
                return [
                    {
                        "id": r.id,
                        "title": r.title,
                        "url": r.url,
                        "type": r.resource_type,
                        "source": r.source,
                        "metadata": r.metadata
                    }
                    for r in resources
                ]
        
        return asyncio.run(get_async())
    except Exception as e:
        logger.error(f"Failed to get resources needing refresh: {e}")
        return []


def _fetch_fresh_metadata(resource: Dict) -> Optional[Dict]:
    """Fetch fresh metadata from resource source."""
    try:
        source = resource.get("source", "")
        url = resource.get("url", "")
        
        if source == "youtube":
            from app.integrations.youtube import YouTubeClient
            if settings.YOUTUBE_API_KEY:
                client = YouTubeClient(settings.YOUTUBE_API_KEY)
                video_id = url.split("v=")[-1] if "v=" in url else None
                if video_id:
                    video_data = client.get_video_details(video_id)
                    return {
                        "views": video_data.get("view_count", 0),
                        "likes": video_data.get("like_count", 0),
                        "updated_at": datetime.now().isoformat()
                    }
        
        elif source == "github":
            from app.integrations.github import GitHubClient
            if settings.GITHUB_TOKEN:
                client = GitHubClient(settings.GITHUB_TOKEN)
                # Extract owner/repo from URL
                parts = url.split("github.com/")[-1].split("/")
                if len(parts) >= 2:
                    repo_data = client.get_repository(parts[0], parts[1])
                    return {
                        "stars": repo_data.get("stargazers_count", 0),
                        "forks": repo_data.get("forks_count", 0),
                        "updated_at": repo_data.get("updated_at", "")
                    }
        
        return None
    except Exception as e:
        logger.error(f"Failed to fetch fresh metadata: {e}")
        return None


def _update_resource_metadata(resource_id: str, metadata: Dict):
    """Update resource metadata in database."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.resource import Resource
        from sqlalchemy import select
        import asyncio
        
        async def update_async():
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Resource).where(Resource.id == resource_id)
                )
                resource = result.scalar_one_or_none()
                
                if resource:
                    # Merge new metadata with existing
                    if not resource.metadata:
                        resource.metadata = {}
                    resource.metadata.update(metadata)
                    resource.updated_at = datetime.now()
                    await session.commit()
        
        asyncio.run(update_async())
    except Exception as e:
        logger.error(f"Failed to update resource metadata: {e}")
        pass


def _resource_exists(url: str) -> bool:
    """Check if resource already exists in database."""
    # TODO: Implement database check
    return False


def _create_resource_record(resource: Dict):
    """Create new resource record in database."""
    # TODO: Implement database insertion
    pass