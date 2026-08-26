"""External API integration with randomuser.me."""

import time
from typing import Any

import httpx

# Simple in-memory cache
_cache: dict[str, Any] = {"data": None, "timestamp": 0}
CACHE_TTL = 300  # 5 minutes


async def fetch_external_users(count: int = 10) -> list[dict[str, Any]]:
    """Fetch random users from the external API with caching."""
    now = time.time()

    # Return cached data if still fresh
    if _cache["data"] is not None and (now - _cache["timestamp"]) < CACHE_TTL:
        return _cache["data"]

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"https://randomuser.me/api/?results={count}&nat=us,gb,au"
            )
            response.raise_for_status()
            data = response.json()

        users = []
        for user in data.get("results", []):
            users.append({
                "name": f"{user['name']['first']} {user['name']['last']}",
                "email": user["email"],
                "phone": user["phone"],
                "location": f"{user['location']['city']}, {user['location']['country']}",
                "picture": user["picture"]["medium"],
                "nationality": user["nat"],
            })

        _cache["data"] = users
        _cache["timestamp"] = now
        return users

    except (httpx.HTTPError, httpx.TimeoutException, KeyError) as e:
        # Return cached data on error, or empty list
        if _cache["data"] is not None:
            return _cache["data"]
        return []
