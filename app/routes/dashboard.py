"""Dashboard API endpoint."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.dashboard import DashboardResponse
from app.services.task_service import TaskService

router = APIRouter()


def get_task_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> TaskService:
    return TaskService(TaskRepository(session), UserRepository(session))


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Optional[int] = Query(None, description="Current user ID for 'My Tasks' count"),
):
    """Fetch dashboard statistics and recent tasks."""
    return await service.get_dashboard(user_id)
