"""
Pomodoro Settings API Router

Endpoints for managing Pomodoro timer settings.
"""

from fastapi import APIRouter

from ..deps import CurrentUser
from ..db import get_redis_client
from ..schemas import PomodoroSettings


router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])

POMODORO_KEY_PREFIX = "user:pomodoro:"


@router.get("/settings", response_model=PomodoroSettings)
async def get_pomodoro_settings(user: CurrentUser):
    """Get user's Pomodoro timer settings."""
    redis = get_redis_client()
    
    work = redis.get(f"{POMODORO_KEY_PREFIX}{user['id']}:work")
    break_mins = redis.get(f"{POMODORO_KEY_PREFIX}{user['id']}:break")
    
    return PomodoroSettings(
        work_minutes=int(work) if work else 30,
        break_minutes=int(break_mins) if break_mins else 5,
    )


@router.put("/settings", response_model=PomodoroSettings)
async def update_pomodoro_settings(
    request: PomodoroSettings,
    user: CurrentUser,
):
    """Update user's Pomodoro timer settings."""
    redis = get_redis_client()
    
    redis.set(f"{POMODORO_KEY_PREFIX}{user['id']}:work", request.work_minutes)
    redis.set(f"{POMODORO_KEY_PREFIX}{user['id']}:break", request.break_minutes)
    
    return request
