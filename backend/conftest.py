"""
Pytest configuration and shared fixtures for Adaptive Learning Platform tests.
"""
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from datetime import datetime, timedelta
from uuid import uuid4

from hypothesis import settings, Verbosity, HealthCheck
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings as app_settings
from app.core.database import Base, get_db
from app.models.user import User, UserProfile
from app.models.learning_path import LearningPath, Milestone, Task
from app.models.resource import Resource
from app.models.progress import UserProgress

# Configure Hypothesis profiles
settings.register_profile(
    "ci",
    max_examples=1000,
    verbosity=Verbosity.verbose,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)

settings.register_profile(
    "dev",
    max_examples=100,
    verbosity=Verbosity.normal,
    deadline=timedelta(milliseconds=500),
    suppress_health_check=[HealthCheck.too_slow]
)

settings.register_profile(
    "debug",
    max_examples=10,
    verbosity=Verbosity.verbose,
    deadline=None
)

# Load appropriate profile
settings.load_profile("dev")


# Database fixtures
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    # Use in-memory SQLite for tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=NullPool,
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


# User fixtures
@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "id": uuid4(),
        "email": "test@example.com",
        "auth0_id": "auth0|test123",
        "is_active": True
    }


@pytest.fixture
async def test_user(db_session: AsyncSession, test_user_data):
    """Create a test user in the database."""
    user = User(**test_user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def test_user_profile_data(test_user_data):
    """Sample user profile data for testing."""
    return {
        "user_id": test_user_data["id"],
        "display_name": "Test User",
        "skill_levels": {
            "python": 0.7,
            "javascript": 0.5,
            "algorithms": 0.6
        },
        "learning_preferences": {
            "preferred_content_types": ["video", "article", "code"],
            "learning_pace": "moderate",
            "difficulty_preference": "gradual",
            "session_duration_preference": 60
        },
        "availability_schedule": {
            "monday": [{"start": 9, "end": 12}, {"start": 14, "end": 17}],
            "tuesday": [{"start": 9, "end": 12}, {"start": 14, "end": 17}],
            "wednesday": [{"start": 9, "end": 12}, {"start": 14, "end": 17}]
        },
        "timezone": "UTC",
        "goals": [
            {"title": "Master Python", "target_level": "expert"},
            {"title": "Learn Web Development", "target_level": "advanced"}
        ],
        "integrations": {}
    }


@pytest.fixture
async def test_user_profile(db_session: AsyncSession, test_user, test_user_profile_data):
    """Create a test user profile in the database."""
    profile = UserProfile(**test_user_profile_data)
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)
    return profile


# Learning path fixtures
@pytest.fixture
def test_learning_path_data(test_user_data):
    """Sample learning path data for testing."""
    return {
        "user_id": test_user_data["id"],
        "title": "Python Mastery Path",
        "description": "Complete path to Python expertise",
        "difficulty_level": "intermediate",
        "estimated_total_hours": 120,
        "status": "active",
        "completion_percentage": 0.0
    }


@pytest.fixture
async def test_learning_path(db_session: AsyncSession, test_user, test_learning_path_data):
    """Create a test learning path in the database."""
    path = LearningPath(**test_learning_path_data)
    db_session.add(path)
    await db_session.commit()
    await db_session.refresh(path)
    return path


@pytest.fixture
def test_milestone_data(test_learning_path_data):
    """Sample milestone data for testing."""
    return {
        "learning_path_id": None,  # Will be set when creating
        "title": "Python Basics",
        "description": "Learn fundamental Python concepts",
        "order_index": 1,
        "completion_criteria": "Complete all basic syntax exercises",
        "estimated_hours": 20,
        "prerequisites": [],
        "status": "not_started"
    }


@pytest.fixture
async def test_milestone(db_session: AsyncSession, test_learning_path, test_milestone_data):
    """Create a test milestone in the database."""
    test_milestone_data["learning_path_id"] = test_learning_path.id
    milestone = Milestone(**test_milestone_data)
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)
    return milestone


@pytest.fixture
def test_task_data(test_milestone_data):
    """Sample task data for testing."""
    return {
        "milestone_id": None,  # Will be set when creating
        "title": "Learn Python Variables",
        "description": "Understand variable types and assignment",
        "task_type": "read",
        "estimated_minutes": 30,
        "completion_status": "not_started"
    }


@pytest.fixture
async def test_task(db_session: AsyncSession, test_milestone, test_task_data):
    """Create a test task in the database."""
    test_task_data["milestone_id"] = test_milestone.id
    task = Task(**test_task_data)
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


# Resource fixtures
@pytest.fixture
def test_resource_data():
    """Sample resource data for testing."""
    return {
        "title": "Python Tutorial for Beginners",
        "description": "Comprehensive Python tutorial",
        "resource_type": "video",
        "source_platform": "youtube",
        "url": "https://youtube.com/watch?v=test123",
        "metadata": {
            "author": "Tech Educator",
            "published_date": "2024-01-01",
            "view_count": 100000,
            "rating": 4.8,
            "duration": 3600
        },
        "difficulty_level": "beginner",
        "estimated_duration": 60,
        "tags": ["python", "programming", "tutorial"],
        "quality_score": 0.85
    }


@pytest.fixture
async def test_resource(db_session: AsyncSession, test_resource_data):
    """Create a test resource in the database."""
    resource = Resource(**test_resource_data)
    db_session.add(resource)
    await db_session.commit()
    await db_session.refresh(resource)
    return resource


# Progress fixtures
@pytest.fixture
def test_progress_data(test_user_data, test_learning_path_data):
    """Sample progress data for testing."""
    return {
        "user_id": test_user_data["id"],
        "learning_path_id": None,  # Will be set when creating
        "completed_milestones": [],
        "completed_tasks": [],
        "total_study_time": 0,
        "streak_days": 0,
        "performance_metrics": {
            "completion_rate": 0.0,
            "average_session_duration": 0,
            "preferred_study_times": [],
            "difficulty_adaptation_score": 0.5,
            "engagement_score": 0.5
        }
    }


@pytest.fixture
async def test_progress(db_session: AsyncSession, test_user, test_learning_path, test_progress_data):
    """Create a test progress record in the database."""
    test_progress_data["learning_path_id"] = test_learning_path.id
    progress = UserProgress(**test_progress_data)
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)
    return progress


# Agent fixtures
@pytest.fixture
def mock_agent_state():
    """Create a mock agent state for testing."""
    from app.agents.base import AgentState
    return AgentState(
        agent_id="test_agent",
        context={},
        conversation_history=[],
        current_task=None
    )


@pytest.fixture
def mock_agent_message():
    """Create a mock agent message for testing."""
    from app.agents.base import AgentMessage
    return AgentMessage(
        sender="test_sender",
        receiver="test_receiver",
        message_type="request",
        content={"action": "test_action"},
        timestamp=datetime.utcnow()
    )


# API fixtures
@pytest.fixture
def mock_auth_token():
    """Create a mock authentication token for testing."""
    return "Bearer test_token_12345"


@pytest.fixture
def mock_auth_headers(mock_auth_token):
    """Create mock authentication headers for testing."""
    return {"Authorization": mock_auth_token}


# External API mocks
@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from OpenAI"
                }
            }
        ]
    }


@pytest.fixture
def mock_youtube_response():
    """Mock YouTube API response."""
    return {
        "items": [
            {
                "id": {"videoId": "test123"},
                "snippet": {
                    "title": "Test Video",
                    "description": "Test description",
                    "publishedAt": "2024-01-01T00:00:00Z"
                },
                "contentDetails": {"duration": "PT10M30S"},
                "statistics": {
                    "viewCount": "10000",
                    "likeCount": "500"
                }
            }
        ]
    }


@pytest.fixture
def mock_github_response():
    """Mock GitHub API response."""
    return {
        "items": [
            {
                "name": "test-repo",
                "full_name": "user/test-repo",
                "description": "Test repository",
                "html_url": "https://github.com/user/test-repo",
                "stargazers_count": 100,
                "forks_count": 20,
                "language": "Python"
            }
        ]
    }


# Utility fixtures
@pytest.fixture
def freeze_time():
    """Fixture to freeze time for testing."""
    frozen_time = datetime(2024, 1, 1, 12, 0, 0)
    return frozen_time


@pytest.fixture
def sample_skill_levels():
    """Sample skill levels for testing."""
    return {
        "python": 0.7,
        "javascript": 0.5,
        "algorithms": 0.6,
        "data_structures": 0.5,
        "web_development": 0.4
    }


@pytest.fixture
def sample_learning_goals():
    """Sample learning goals for testing."""
    return [
        {
            "title": "Master Python",
            "description": "Become proficient in Python programming",
            "target_level": "expert",
            "priority": "high"
        },
        {
            "title": "Learn Web Development",
            "description": "Build full-stack web applications",
            "target_level": "advanced",
            "priority": "medium"
        }
    ]
