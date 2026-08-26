"""Comment Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    """Schema for creating a comment."""

    comment: str = Field(..., min_length=1, max_length=2000)
    user_id: int


class CommentResponse(BaseModel):
    """Schema for comment response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    user_id: int
    comment: str
    created_at: datetime
    user_name: Optional[str] = None
