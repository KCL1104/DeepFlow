"""
Statistics API Router

Provides dynamic statistics for the Dashboard.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from ..deps import CurrentUser
from ..db import get_supabase_client


router = APIRouter(prefix="/stats", tags=["stats"])


class DailyStatsResponse(BaseModel):
    """Daily statistics response."""
    deep_work_minutes: int
    context_switches: int
    tasks_completed: int
    tasks_intercepted: int
    flow_sessions: int


class WeeklyStatsResponse(BaseModel):
    """Weekly statistics response."""
    total_deep_work_hours: float
    avg_daily_tasks: float
    total_context_switches: int
    busiest_day: str
    daily_breakdown: List[dict]


@router.get("/daily", response_model=DailyStatsResponse)
async def get_daily_stats(user: CurrentUser):
    """
    Get today's statistics for the dashboard.
    """
    supabase = get_supabase_client()
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get completed tasks today
    completed_result = (
        supabase.table("tasks")
        .select("*", count="exact")
        .eq("user_id", user["id"])
        .eq("status", "completed")
        .gte("completed_at", today_start.isoformat())
        .execute()
    )
    tasks_completed = completed_result.count or 0
    
    # Get all tasks created today (intercepted signals)
    all_tasks_result = (
        supabase.table("tasks")
        .select("*", count="exact")
        .eq("user_id", user["id"])
        .gte("created_at", today_start.isoformat())
        .execute()
    )
    tasks_intercepted = all_tasks_result.count or 0
    
    # Get flow sessions from state changes (simplified: count tasks marked in_progress)
    flow_result = (
        supabase.table("tasks")
        .select("*", count="exact")
        .eq("user_id", user["id"])
        .gte("created_at", today_start.isoformat())
        .neq("status", "pending")
        .execute()
    )
    flow_sessions = flow_result.count or 0
    
    # Calculate estimated deep work time (25 min per flow session)
    deep_work_minutes = flow_sessions * 25
    
    # Context switches estimated as tasks_intercepted - tasks_completed
    context_switches = max(0, tasks_intercepted - tasks_completed)
    
    return DailyStatsResponse(
        deep_work_minutes=deep_work_minutes,
        context_switches=context_switches,
        tasks_completed=tasks_completed,
        tasks_intercepted=tasks_intercepted,
        flow_sessions=flow_sessions,
    )


@router.get("/weekly", response_model=WeeklyStatsResponse)
async def get_weekly_stats(user: CurrentUser):
    """
    Get weekly statistics for the dashboard.
    """
    supabase = get_supabase_client()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today - timedelta(days=7)
    
    # Get all tasks from the past week
    week_result = (
        supabase.table("tasks")
        .select("*")
        .eq("user_id", user["id"])
        .gte("created_at", week_start.isoformat())
        .execute()
    )
    
    tasks = week_result.data or []
    
    # Calculate daily breakdown
    daily_counts = {}
    for task in tasks:
        created = datetime.fromisoformat(task["created_at"].replace("Z", "+00:00"))
        day_key = created.strftime("%A")  # Day name
        daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
    
    # Find busiest day
    busiest_day = max(daily_counts, key=daily_counts.get) if daily_counts else "N/A"
    
    # Build daily breakdown
    daily_breakdown = [
        {"day": day, "tasks": count}
        for day, count in daily_counts.items()
    ]
    
    # Calculate totals
    completed_tasks = [t for t in tasks if t.get("status") == "completed"]
    total_deep_work_hours = len(completed_tasks) * 0.4  # ~25 min per task
    avg_daily_tasks = len(tasks) / 7 if tasks else 0
    
    return WeeklyStatsResponse(
        total_deep_work_hours=round(total_deep_work_hours, 1),
        avg_daily_tasks=round(avg_daily_tasks, 1),
        total_context_switches=len(tasks) - len(completed_tasks),
        busiest_day=busiest_day,
        daily_breakdown=daily_breakdown,
    )
