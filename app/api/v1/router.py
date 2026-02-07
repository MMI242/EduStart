from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    children,
    modules,
    progress,
    recommendations
)
from . import analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    children.router,
    prefix="/children",
    tags=["Children Management"]
)

api_router.include_router(
    modules.router,
    prefix="/modules",
    tags=["Learning Modules"]
)

api_router.include_router(
    progress.router,
    prefix="/progress",
    tags=["Progress & Reports"]
)

api_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["AI Recommendations"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)