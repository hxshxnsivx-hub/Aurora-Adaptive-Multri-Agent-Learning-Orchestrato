"""
Main API router for v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    onboarding,
    learning_paths,
    resources,
    voice,
    integrations,
    analytics,
    tasks
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])
api_router.include_router(learning_paths.router, prefix="/learning-paths", tags=["learning-paths"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])