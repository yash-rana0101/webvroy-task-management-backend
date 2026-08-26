"""Dashboard Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DashboardStats(BaseModel):
    """Aggregate task statistics."""

    total_tasks: int = 0
    pending: int = 0
    in_progress: int = 0
    completed: int = 0
    blocked: int = 0
    overdue: int = 0
    my_tasks: int = 0


class RecentTask(BaseModel):
    """Abbreviated task for dashboard display."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: str
    priority: str
    due_date: Optional[datetime] = None
    assignee_name: Optional[str] = None


class DashboardResponse(BaseModel):
    """Complete dashboard payload."""

    stats: DashboardStats
    recent_tasks: list[RecentTask]
