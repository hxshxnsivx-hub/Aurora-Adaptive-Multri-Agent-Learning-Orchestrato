"""
GraphQL schema definition using Strawberry.
"""

import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional
from datetime import datetime

from app.core.config import settings


@strawberry.type
class User:
    id: strawberry.ID
    email: str
    created_at: datetime
    is_active: bool


@strawberry.type
class UserProfile:
    id: strawberry.ID
    display_name: str
    skill_levels: strawberry.scalars.JSON
    learning_preferences: strawberry.scalars.JSON
    timezone: str


@strawberry.type
class LearningPath:
    id: strawberry.ID
    title: str
    description: Optional[str]
    difficulty_level: str
    estimated_total_hours: int
    status: str
    completion_percentage: float
    created_at: datetime


@strawberry.type
class Milestone:
    id: strawberry.ID
    title: str
    description: Optional[str]
    order_index: int
    estimated_hours: int
    status: str
    due_date: Optional[datetime]


@strawberry.type
class Resource:
    id: strawberry.ID
    title: str
    description: Optional[str]
    resource_type: str
    source_platform: str
    url: str
    difficulty_level: str
    estimated_duration: int
    quality_score: float


@strawberry.type
class Query:
    """GraphQL queries."""
    
    @strawberry.field
    def hello(self) -> str:
        return "Hello from Adaptive Learning Platform GraphQL API!"
    
    @strawberry.field
    async def user(self, id: strawberry.ID) -> Optional[User]:
        """Get user by ID."""
        # TODO: Implement user retrieval
        return None
    
    @strawberry.field
    async def learning_paths(self, user_id: strawberry.ID) -> List[LearningPath]:
        """Get learning paths for a user."""
        # TODO: Implement learning path retrieval
        return []
    
    @strawberry.field
    async def resources(
        self, 
        query: Optional[str] = None,
        resource_type: Optional[str] = None,
        difficulty_level: Optional[str] = None
    ) -> List[Resource]:
        """Search resources with optional filters."""
        # TODO: Implement resource search
        return []


@strawberry.type
class Mutation:
    """GraphQL mutations."""
    
    @strawberry.field
    async def create_learning_path(
        self,
        user_id: strawberry.ID,
        title: str,
        goals: List[str]
    ) -> Optional[LearningPath]:
        """Create a new learning path."""
        # TODO: Implement learning path creation
        return None
    
    @strawberry.field
    async def update_task_completion(
        self,
        task_id: strawberry.ID,
        completed: bool
    ) -> bool:
        """Update task completion status."""
        # TODO: Implement task completion update
        return True


@strawberry.type
class Subscription:
    """GraphQL subscriptions for real-time updates."""
    
    @strawberry.subscription
    async def progress_updates(self, user_id: strawberry.ID):
        """Subscribe to progress updates for a user."""
        # TODO: Implement real-time progress updates
        yield {"message": "Progress updated"}


# Create GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)

# Create GraphQL router
graphql_app = GraphQLRouter(
    schema,
    graphiql=settings.ENVIRONMENT != "production"
)