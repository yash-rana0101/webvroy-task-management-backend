"""Task Pydantic schemas for request/response validation."""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task. All fields optional."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    """Schema for task response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    assignee_name: Optional[str] = None
    comment_count: int = 0


class TaskFilterParams:
    """Dependency-injectable task filter parameters."""

    def __init__(
        self,
        status: Optional[TaskStatus] = Query(None, description="Filter by status"),
        priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
        assignee: Optional[int] = Query(None, description="Filter by assignee user ID"),
        search: Optional[str] = Query(None, description="Search in title and description"),
        sort_by: str = Query("created_at", description="Sort field"),
        sort_order: Literal["asc", "desc"] = Query("desc", description="Sort order"),
    ):
        self.status = status
        self.priority = priority
        self.assignee = assignee
        self.search = search
        self.sort_by = sort_by
        self.sort_order = sort_order
