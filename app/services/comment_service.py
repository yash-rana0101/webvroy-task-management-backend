"""Comment business logic layer."""

from typing import Sequence

from app.core.exceptions import NotFoundException
from app.repositories.comment_repository import CommentRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.comment import CommentCreate, CommentResponse


class CommentService:
    """Service handling comment business logic."""

    def __init__(
        self,
        comment_repo: CommentRepository,
        task_repo: TaskRepository,
        user_repo: UserRepository,
    ):
        self.comment_repo = comment_repo
        self.task_repo = task_repo
        self.user_repo = user_repo

    async def add_comment(
        self, task_id: int, payload: CommentCreate
    ) -> CommentResponse:
        """Add a comment to a task."""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException(f"Task with ID {task_id} not found")

        user = await self.user_repo.get_by_id(payload.user_id)
        if not user:
            raise NotFoundException(f"User with ID {payload.user_id} not found")

        comment = await self.comment_repo.create(
            task_id=task_id,
            user_id=payload.user_id,
            comment=payload.comment,
        )
        return CommentResponse(
            id=comment.id,
            task_id=comment.task_id,
            user_id=comment.user_id,
            comment=comment.comment,
            created_at=comment.created_at,
            user_name=user.name,
        )

    async def list_comments(self, task_id: int) -> list[CommentResponse]:
        """Fetch all comments for a task."""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundException(f"Task with ID {task_id} not found")

        comments = await self.comment_repo.get_by_task_id(task_id)
        return [
            CommentResponse(
                id=c.id,
                task_id=c.task_id,
                user_id=c.user_id,
                comment=c.comment,
                created_at=c.created_at,
                user_name=c.user.name if c.user else None,
            )
            for c in comments
        ]
