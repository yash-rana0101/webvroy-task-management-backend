"""Task data access layer with filtering, pagination, and aggregation."""

from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy import Select, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.pagination import PaginationParams
from app.schemas.task import TaskFilterParams


class TaskRepository(BaseRepository[Task]):
    """Repository for Task entities with advanced querying."""

    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    def _apply_filters(self, stmt: Select, filters: TaskFilterParams) -> Select:
        """Apply dynamic where clauses based on filter params."""
        if filters.status:
            stmt = stmt.where(Task.status == filters.status.value)
        if filters.priority:
            stmt = stmt.where(Task.priority == filters.priority.value)
        if filters.assignee:
            stmt = stmt.where(Task.assigned_to == filters.assignee)
        if filters.search:
            search_term = f"%{filters.search}%"
            stmt = stmt.where(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term),
                )
            )
        return stmt

    def _apply_sorting(self, stmt: Select, filters: TaskFilterParams) -> Select:
        """Apply sorting based on filter params."""
        allowed_sort_fields = {
            "created_at": Task.created_at,
            "updated_at": Task.updated_at,
            "title": Task.title,
            "status": Task.status,
            "priority": Task.priority,
            "due_date": Task.due_date,
        }
        sort_column = allowed_sort_fields.get(filters.sort_by, Task.created_at)
        if filters.sort_order == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())
        return stmt

    async def get_filtered_tasks(
        self, filters: TaskFilterParams, pagination: PaginationParams
    ) -> tuple[Sequence[Task], int]:
        """Fetch filtered, sorted, paginated tasks with assignee eagerly loaded."""
        # Count query
        count_stmt = select(func.count()).select_from(Task)
        count_stmt = self._apply_filters(count_stmt, filters)
        total = await self.session.scalar(count_stmt) or 0

        # Data query
        data_stmt = select(Task).options(
            selectinload(Task.assignee),
            selectinload(Task.comments),
        )
        data_stmt = self._apply_filters(data_stmt, filters)
        data_stmt = self._apply_sorting(data_stmt, filters)
        data_stmt = data_stmt.offset(pagination.offset).limit(pagination.limit)

        result = await self.session.scalars(data_stmt)
        items = result.all()
        return items, total

    async def get_task_with_details(self, task_id: int) -> Optional[Task]:
        """Fetch a single task with assignee and comments eagerly loaded."""
        from app.models.comment import Comment

        stmt = (
            select(Task)
            .options(
                selectinload(Task.assignee),
                selectinload(Task.comments).selectinload(Comment.user),
            )
            .where(Task.id == task_id)
        )
        result = await self.session.scalars(stmt)
        return result.first()

    async def get_dashboard_stats(self, user_id: Optional[int] = None) -> dict:
        """Compute aggregate task statistics in a single query."""
        now = datetime.now(timezone.utc)
        stmt = select(
            func.count().label("total_tasks"),
            func.count(case((Task.status == "pending", 1))).label("pending"),
            func.count(case((Task.status == "in_progress", 1))).label("in_progress"),
            func.count(case((Task.status == "completed", 1))).label("completed"),
            func.count(case((Task.status == "blocked", 1))).label("blocked"),
            func.count(
                case(
                    (
                        (Task.due_date < now) & (Task.status != "completed"),
                        1,
                    )
                )
            ).label("overdue"),
        )
        result = await self.session.execute(stmt)
        row = result.one()

        stats = {
            "total_tasks": row.total_tasks,
            "pending": row.pending,
            "in_progress": row.in_progress,
            "completed": row.completed,
            "blocked": row.blocked,
            "overdue": row.overdue,
            "my_tasks": 0,
        }

        if user_id:
            my_stmt = select(func.count()).select_from(Task).where(Task.assigned_to == user_id)
            my_count = await self.session.scalar(my_stmt) or 0
            stats["my_tasks"] = my_count

        return stats

    async def get_recent_tasks(self, limit: int = 5) -> Sequence[Task]:
        """Fetch the most recently created tasks."""
        stmt = (
            select(Task)
            .options(selectinload(Task.assignee))
            .order_by(Task.created_at.desc())
            .limit(limit)
        )
        result = await self.session.scalars(stmt)
        return result.all()
