"""Task business logic layer."""

from typing import Optional, Sequence

from app.core.exceptions import BadRequestError, NotFoundException
from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.dashboard import DashboardResponse, DashboardStats, RecentTask
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.task import (
    TaskCreate,
    TaskFilterParams,
    TaskResponse,
    TaskUpdate,
)


class TaskService:
    """Service handling task business logic."""

    def __init__(self, task_repo: TaskRepository, user_repo: UserRepository):
        self.task_repo = task_repo
        self.user_repo = user_repo

    def _to_response(self, task: Task, comment_count: int = 0) -> TaskResponse:
        """Convert a Task ORM instance to a TaskResponse schema."""
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            assigned_to=task.assigned_to,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
            assignee_name=task.assignee.name if task.assignee else None,
            comment_count=comment_count,
        )

    async def _validate_assignee(self, assignee_id: Optional[int]) -> None:
        """Validate that the assignee exists."""
        if assignee_id is not None:
            user = await self.user_repo.get_by_id(assignee_id)
            if not user:
                raise BadRequestError(f"Assignee with ID {assignee_id} does not exist")

    async def create_task(self, payload: TaskCreate) -> TaskResponse:
        await self._validate_assignee(payload.assigned_to)
        task = await self.task_repo.create(
            title=payload.title,
            description=payload.description,
            status=payload.status.value,
            priority=payload.priority.value,
            assigned_to=payload.assigned_to,
            due_date=payload.due_date,
        )
        # Reload with relationships
        task = await self.task_repo.get_task_with_details(task.id)
        return self._to_response(task)

    async def update_task(self, task_id: int, payload: TaskUpdate) -> TaskResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException(f"Task with ID {task_id} not found")

        update_data = payload.model_dump(exclude_unset=True)
        if "assigned_to" in update_data:
            await self._validate_assignee(update_data["assigned_to"])
        if "status" in update_data and update_data["status"]:
            update_data["status"] = update_data["status"].value
        if "priority" in update_data and update_data["priority"]:
            update_data["priority"] = update_data["priority"].value

        await self.task_repo.update(task, **update_data)
        task = await self.task_repo.get_task_with_details(task_id)
        return self._to_response(task, len(task.comments) if task.comments else 0)

    async def delete_task(self, task_id: int) -> None:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException(f"Task with ID {task_id} not found")
        await self.task_repo.delete(task)

    async def get_task(self, task_id: int) -> TaskResponse:
        task = await self.task_repo.get_task_with_details(task_id)
        if not task:
            raise NotFoundException(f"Task with ID {task_id} not found")
        return self._to_response(task, len(task.comments) if task.comments else 0)

    async def list_tasks(
        self, filters: TaskFilterParams, pagination: PaginationParams
    ) -> PaginatedResponse[TaskResponse]:
        tasks, total = await self.task_repo.get_filtered_tasks(filters, pagination)
        items = [self._to_response(t, len(t.comments) if t.comments else 0) for t in tasks]
        return PaginatedResponse.create(items=items, total=total, params=pagination)

    async def get_dashboard(
        self, user_id: Optional[int] = None
    ) -> DashboardResponse:
        stats_dict = await self.task_repo.get_dashboard_stats(user_id)
        stats = DashboardStats(**stats_dict)

        recent_tasks_raw = await self.task_repo.get_recent_tasks(limit=5)
        recent_tasks = [
            RecentTask(
                id=t.id,
                title=t.title,
                status=t.status,
                priority=t.priority,
                due_date=t.due_date,
                assignee_name=t.assignee.name if t.assignee else None,
            )
            for t in recent_tasks_raw
        ]
        return DashboardResponse(stats=stats, recent_tasks=recent_tasks)
