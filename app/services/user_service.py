"""User business logic layer."""

from typing import Sequence

from app.core.exceptions import ConflictError, NotFoundException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:
    """Service handling user business logic."""

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, payload: UserCreate) -> User:
        """Create a new user after checking email uniqueness."""
        if await self.repo.is_email_taken(payload.email):
            raise ConflictError(f"User with email '{payload.email}' already exists")
        return await self.repo.create(
            name=payload.name,
            email=payload.email.lower(),
            role=payload.role,
        )

    async def get_user(self, user_id: int) -> User:
        """Fetch a user by ID or raise NotFoundException."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        return user

    async def list_users(self) -> Sequence[User]:
        """Fetch all users."""
        return await self.repo.get_all_users()
