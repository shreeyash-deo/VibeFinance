"""
backend/app/deps.py - Application Dependencies
"""

from fastapi import Header
from backend.app.config import settings

async def get_current_user_id(x_user_id: str | None = Header(None)) -> str:
    """
    Returns active user ID / persona slug.
    Reads X-User-Id header if provided, falls back to settings.DEFAULT_USER_ID ('meena').
    """
    if x_user_id and x_user_id.strip():
        return x_user_id.strip().lower()
    return settings.DEFAULT_USER_ID

