"""External API integration endpoints."""

from typing import Any

from fastapi import APIRouter

from app.services.external_service import fetch_external_users

router = APIRouter()


@router.get("/users", response_model=list[dict[str, Any]])
async def get_external_users():
    """Fetch random users from the external randomuser.me API."""
    return await fetch_external_users(count=10)
