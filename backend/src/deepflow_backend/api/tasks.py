"""
Tasks API Router

Endpoints for updating individual task status.
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from ..deps import CurrentUser, QueueManager
from ..db import get_supabase_client
from ..schemas import TaskUpdate, TaskResponse, TaskStatus


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    request: TaskUpdate,
    user: CurrentUser,
    queue_manager: QueueManager,
):
    """Update task status or details."""
    supabase = get_supabase_client()

    # Verify task belongs to user
    existing = (
        supabase.table("tasks")
        .select("*")
        .eq("id", task_id)
        .eq("user_id", user["id"])
        .single()
        .execute()
    )

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
    if request.status:
        update_data["status"] = request.status.value

        # Handle status-specific logic
        if request.status == TaskStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow().isoformat()
            queue_manager.clear_current_task(user["id"])
            queue_manager.remove_task(user["id"], task_id)

        elif request.status == TaskStatus.BLOCKED:
            queue_manager.clear_current_task(user["id"])

        elif request.status == TaskStatus.DEFERRED:
            queue_manager.clear_current_task(user["id"])
            # Re-add to queue with lower priority
            queue_manager.add_task(user["id"], task_id, existing.data.get("urgency", 5) * 5)

    result = (
        supabase.table("tasks")
        .update(update_data)
        .eq("id", task_id)
        .execute()
    )

    # Fetch updated task
    updated = supabase.table("tasks").select("*").eq("id", task_id).single().execute()
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
