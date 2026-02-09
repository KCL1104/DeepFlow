"""
Tasks API Router

Endpoints for updating individual task status.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from ..deps import CurrentUser, get_current_user, get_queue_manager
from ..db import get_supabase_admin_client, TaskQueueManager
from .error_handling import raise_db_http_exception
from ..schemas import TaskUpdate, TaskResponse, TaskStatus


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    request: TaskUpdate,
    user: CurrentUser = Depends(get_current_user),
    queue_manager: TaskQueueManager = Depends(get_queue_manager),
):
    """Update task status or details."""
    try:
        supabase = get_supabase_admin_client()
    except Exception as exc:
        raise_db_http_exception(exc, "updating task")

    # Verify task belongs to user
    try:
        existing = (
            supabase.table("tasks")
            .select("*")
            .eq("id", task_id)
            .eq("user_id", user.id)
            .single()
            .execute()
        )
    except Exception as exc:
        raise_db_http_exception(exc, "loading task")

    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    update_data = {}

    if request.title:
        update_data["title"] = request.title
    if request.summary is not None:
        update_data["summary"] = request.summary
    if request.urgency is not None:
        update_data["urgency"] = request.urgency
    clear_current = False
    remove_from_queue = False
    deferred_score = None
    if request.status:
        update_data["status"] = request.status.value

        # Handle status-specific logic
        if request.status == TaskStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow().isoformat()
        if request.status in {TaskStatus.COMPLETED, TaskStatus.BLOCKED, TaskStatus.DEFERRED}:
            clear_current = True

        if request.status == TaskStatus.COMPLETED:
            remove_from_queue = True
        elif request.status == TaskStatus.DEFERRED:
            # Re-add to queue with lower priority
            deferred_score = existing.data.get("urgency", 5) * 5

    try:
        (
            supabase.table("tasks")
            .update(update_data)
            .eq("id", task_id)
            .eq("user_id", user.id)
            .execute()
        )
    except Exception as exc:
        raise_db_http_exception(exc, "updating task")

    if clear_current:
        queue_manager.clear_current_task(user.id)
    if remove_from_queue:
        queue_manager.remove_task(user.id, task_id)
    if deferred_score is not None:
        queue_manager.add_task(user.id, task_id, deferred_score)

    # Fetch updated task
    try:
        updated = (
            supabase.table("tasks")
            .select("*")
            .eq("id", task_id)
            .eq("user_id", user.id)
            .single()
            .execute()
        )
    except Exception as exc:
        raise_db_http_exception(exc, "loading updated task")
    t = updated.data

    return TaskResponse(
        id=t["id"],
        title=t["title"],
        summary=t.get("summary"),
        suggested_action=t.get("suggested_action"),
        urgency=t.get("urgency", 5),
        estimated_minutes=t.get("estimated_minutes"),
        status=TaskStatus(t.get("status", "pending")),
        priority_score=0,
        created_at=t["created_at"],
        completed_at=t.get("completed_at"),
    )
