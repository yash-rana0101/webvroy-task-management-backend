"""Task API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories.comment_repository import CommentRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.task import (
    TaskCreate,
    TaskFilterParams,
    TaskResponse,
    TaskUpdate,
)
from app.services.comment_service import CommentService
from app.services.task_service import TaskService

router = APIRouter()


def get_task_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> TaskService:
    return TaskService(TaskRepository(session), UserRepository(session))


def get_comment_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> CommentService:
    return CommentService(CommentRepository(session), TaskRepository(session), UserRepository(session))


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
CommentServiceDep = Annotated[CommentService, Depends(get_comment_service)]


@router.get("", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(
    service: TaskServiceDep,
    filters: Annotated[TaskFilterParams, Depends()],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List tasks with filtering, sorting, and pagination."""
    return await service.list_tasks(filters, pagination)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, service: TaskServiceDep):
    """Fetch a single task with details."""
    return await service.get_task(task_id)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, service: TaskServiceDep):
    """Create a new task."""
    return await service.create_task(payload)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, payload: TaskUpdate, service: TaskServiceDep):
    """Update an existing task."""
    return await service.update_task(task_id, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, service: TaskServiceDep):
    """Delete a task."""
    await service.delete_task(task_id)


@router.get("/{task_id}/comments", response_model=list[CommentResponse])
async def list_comments(task_id: int, service: CommentServiceDep):
    """List all comments for a task."""
    return await service.list_comments(task_id)


@router.post(
    "/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(task_id: int, payload: CommentCreate, service: CommentServiceDep):
    """Add a comment to a task."""
    return await service.add_comment(task_id, payload)
