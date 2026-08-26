"""Generic base repository with common CRUD operations."""

from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Abstract base repository providing standard CRUD operations."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: int) -> Optional[ModelType]:
        """Fetch a single entity by primary key."""
        return await self.session.get(self.model, entity_id)

    async def list_all(
        self, *, offset: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        """Fetch a paginated list of entities."""
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.session.scalars(stmt)
        return result.all()

    async def count(self) -> int:
        """Return total count of entities."""
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.scalar(stmt)
        return result or 0

    async def create(self, **kwargs: Any) -> ModelType:
        """Create and persist a new entity."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelType, **kwargs: Any) -> ModelType:
        """Update an existing entity's attributes."""
        for key, value in kwargs.items():
            if value is not None:
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        """Delete an entity."""
        await self.session.delete(instance)
        await self.session.flush()
