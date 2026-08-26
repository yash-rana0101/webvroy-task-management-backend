"""API router aggregation."""

from fastapi import APIRouter

from app.routes.dashboard import router as dashboard_router
from app.routes.external import router as external_router
from app.routes.tasks import router as tasks_router
from app.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(external_router, prefix="/external", tags=["External"])
