"""
Queue API Router

Endpoints for managing task priority queue.
"""

from datetime import datetime
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, status

from ..deps import CurrentUser, get_current_user, get_queue_manager
from ..db import get_supabase_admin_client, TaskQueueManager
from .error_handling import raise_db_http_exception
from ..schemas import (
    TaskCreate,
    TaskResponse,
    TaskStatus,
    QueueResponse,
)


router = APIRouter(prefix="/queue", tags=["queue"])


def calculate_priority_score(urgency: int, deadline: datetime | None = None) -> float:
    """Calculate task priority score."""
    score = urgency * 10.0

    if deadline:
        hours_until = (deadline - datetime.utcnow()).total_seconds() / 3600
        if hours_until > 0:
            score += min(50, 100 / hours_until)  # Closer deadline = higher score

    return score


@router.get("", response_model=QueueResponse)
async def get_queue(
    user: CurrentUser = Depends(get_current_user),
    queue_manager: TaskQueueManager = Depends(get_queue_manager),
):
    """Get user's task queue with current task."""
    try:
        supabase = get_supabase_admin_client()
    except Exception as exc:
        raise_db_http_exception(exc, "loading queue data")

    # Get current task ID from Redis
    current_task_id = queue_manager.get_current_task(user.id)

    # Get queue from Redis (task IDs with scores)
    queue_items = queue_manager.peek(user.id, count=10)

    # Fetch task details from Supabase
    task_ids = [tid for tid, _ in queue_items]
    if current_task_id and current_task_id not in task_ids:
        task_ids.append(current_task_id)

    tasks = []
    current_task = None

    if task_ids:
        try:
            result = (
                supabase.table("tasks")
                .select("*")
                .eq("user_id", user.id)
                .in_("id", task_ids)
                .execute()
            )
        except Exception as exc:
            raise_db_http_exception(exc, "loading queue tasks")

        task_map = {t["id"]: t for t in (result.data or [])}

        for tid, score in queue_items:
            if tid in task_map:
                t = task_map[tid]
                tasks.append(
                    TaskResponse(
                        id=t["id"],
                        title=t["title"],
                        summary=t.get("summary"),
                        suggested_action=t.get("suggested_action"),
                        urgency=t.get("urgency", 5),
                        estimated_minutes=t.get("estimated_minutes"),
                        status=TaskStatus(t.get("status", "pending")),
                        priority_score=score,
                        created_at=t["created_at"],
                        completed_at=t.get("completed_at"),
                    )
                )

        if current_task_id and current_task_id in task_map:
            t = task_map[current_task_id]
            current_task = TaskResponse(
                id=t["id"],
                title=t["title"],
                summary=t.get("summary"),
                suggested_action=t.get("suggested_action"),
                urgency=t.get("urgency", 5),
                estimated_minutes=t.get("estimated_minutes"),
                status=TaskStatus.IN_PROGRESS,
                priority_score=0,
                created_at=t["created_at"],
            )

    return QueueResponse(
        current_task=current_task,
        queue=tasks,
        total_count=queue_manager.get_queue_length(user.id),
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreate,
    user: CurrentUser = Depends(get_current_user),
    queue_manager: TaskQueueManager = Depends(get_queue_manager),
):
    """Create a new task and add to queue."""
    try:
        supabase = get_supabase_admin_client()
    except Exception as exc:
        raise_db_http_exception(exc, "creating task")

    task_id = str(uuid4())
    score = calculate_priority_score(request.urgency, request.deadline)

    # Store task in Supabase
    task_data = {
        "id": task_id,
        "user_id": user.id,
        "title": request.title,
        "summary": request.summary,
        "suggested_action": request.suggested_action,
        "urgency": request.urgency,
        "estimated_minutes": request.estimated_minutes,
        "deadline": request.deadline.isoformat() if request.deadline else None,
        "context_tags": request.context_tags,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        result = supabase.table("tasks").insert(task_data).execute()
        if not result.data:
            raise RuntimeError("Insert returned no rows")
    except Exception as exc:
        raise_db_http_exception(exc, "creating task")

    # Add to Redis queue
    queue_manager.add_task(user.id, task_id, score)

    return TaskResponse(
        id=task_id,
        title=request.title,
        summary=request.summary,
        suggested_action=request.suggested_action,
        urgency=request.urgency,
        estimated_minutes=request.estimated_minutes,
        status=TaskStatus.PENDING,
        priority_score=score,
        created_at=datetime.utcnow(),
    )


@router.post("/pop", response_model=TaskResponse | None)
async def pop_next_task(
    user: CurrentUser = Depends(get_current_user),
    queue_manager: TaskQueueManager = Depends(get_queue_manager),
):
    """Pop next highest priority task from queue."""
    try:
        supabase = get_supabase_admin_client()
    except Exception as exc:
        raise_db_http_exception(exc, "popping next task")

    # Pop from Redis
    task_id = queue_manager.pop_next(user.id)

    if not task_id:
        return None

    # Set as current task
    queue_manager.set_current_task(user.id, task_id)

    try:
        # Update status in Supabase
        supabase.table("tasks").update({"status": "in_progress"}).eq("id", task_id).eq("user_id", user.id).execute()

        # Fetch task details
        result = (
            supabase.table("tasks")
            .select("*")
            .eq("id", task_id)
            .eq("user_id", user.id)
            .single()
            .execute()
        )
    except Exception as exc:
        raise_db_http_exception(exc, "loading next task")

    if not result.data:
        return None

    t = result.data
    return TaskResponse(
        id=t["id"],
        title=t["title"],
        summary=t.get("summary"),
        suggested_action=t.get("suggested_action"),
        urgency=t.get("urgency", 5),
        estimated_minutes=t.get("estimated_minutes"),
        status=TaskStatus.IN_PROGRESS,
        priority_score=0,
        created_at=t["created_at"],
    )


@router.get("/current", response_model=TaskResponse | None)
async def get_current_task(
    user: CurrentUser = Depends(get_current_user),
    queue_manager: TaskQueueManager = Depends(get_queue_manager),
):
    """Get current active task."""
    try:
        supabase = get_supabase_admin_client()
    except Exception as exc:
        raise_db_http_exception(exc, "loading current task")

    task_id = queue_manager.get_current_task(user.id)

    if not task_id:
        return None

    try:
        result = (
            supabase.table("tasks")
            .select("*")
            .eq("id", task_id)
            .eq("user_id", user.id)
            .single()
            .execute()
        )
    except Exception as exc:
        raise_db_http_exception(exc, "loading current task")

    if not result.data:
        return None

    t = result.data
    return TaskResponse(
        id=t["id"],
        title=t["title"],
        summary=t.get("summary"),
        suggested_action=t.get("suggested_action"),
        urgency=t.get("urgency", 5),
        estimated_minutes=t.get("estimated_minutes"),
        status=TaskStatus.IN_PROGRESS,
        priority_score=0,
        created_at=t["created_at"],
    )


@router.get("/history", response_model=List[TaskResponse])
async def get_task_history(
    user: CurrentUser = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0,
):
    """Get completed tasks history."""
    try:
        supabase = get_supabase_admin_client()
    except Exception as exc:
        raise_db_http_exception(exc, "loading task history")

    try:
        result = (
            supabase.table("tasks")
            .select("*")
            .eq("user_id", user.id)
            .eq("status", "completed")
            .order("completed_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
    except Exception as exc:
        raise_db_http_exception(exc, "loading task history")

    tasks = []
    for t in (result.data or []):
        tasks.append(
            TaskResponse(
                id=t["id"],
                title=t["title"],
                summary=t.get("summary"),
                suggested_action=t.get("suggested_action"),
                urgency=t.get("urgency", 5),
                estimated_minutes=t.get("estimated_minutes"),
                status=TaskStatus.COMPLETED,
                priority_score=0,
                created_at=t["created_at"],
                completed_at=t.get("completed_at"),
            )
        )

    return tasks
