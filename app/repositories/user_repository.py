"""User data access layer."""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User entities."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Find a user by email address."""
        stmt = select(User).where(User.email == email.lower())
        result = await self.session.scalars(stmt)
        return result.first()

    async def is_email_taken(self, email: str) -> bool:
        """Check if an email is already registered."""
        user = await self.get_by_email(email)
        return user is not None

    async def get_all_users(self) -> Sequence[User]:
        """Fetch all users ordered by name."""
        stmt = select(User).order_by(User.name)
        result = await self.session.scalars(stmt)
        return result.all()
