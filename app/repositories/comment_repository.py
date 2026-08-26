"""Comment data access layer."""

from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    """Repository for Comment entities."""

    def __init__(self, session: AsyncSession):
        super().__init__(Comment, session)

    async def get_by_task_id(self, task_id: int) -> Sequence[Comment]:
        """Fetch all comments for a task, ordered by newest first."""
        stmt = (
            select(Comment)
            .options(selectinload(Comment.user))
            .where(Comment.task_id == task_id)
            .order_by(Comment.created_at.desc())
        )
        result = await self.session.scalars(stmt)
        return result.all()

    async def count_by_task_id(self, task_id: int) -> int:
        """Count comments for a specific task."""
        stmt = select(func.count()).select_from(Comment).where(Comment.task_id == task_id)
        result = await self.session.scalar(stmt)
        return result or 0
