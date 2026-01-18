"""
Update Task Status Tool

Updates the status of a task in the queue.
"""

import json
from datetime import datetime
from typing import Literal

from langchain.tools import tool

from .base import get_redis_client, tool_with_tracing


@tool
def update_task_status(
    user_id: str,
    task_id: str,
    status: Literal["done", "blocked", "defer"],
    note: str = ""
) -> dict:
    """
    Update the status of a task in the user's queue.
    
    Use this tool when:
    - User completes a task (status = "done")
    - User is blocked on a task (status = "blocked")
    - User wants to defer a task to later (status = "defer")
    
    Args:
        user_id: The user's unique identifier
        task_id: The task's unique identifier
        status: New status (done/blocked/defer)
        note: Optional note explaining the status change
    
    Returns:
        Dict with updated task info and next task if available
    """
    return _update_task_status_impl(
        user_id=user_id,
        task_id=task_id,
        status=status,
        note=note
    )


@tool_with_tracing("update_task_status")
def _update_task_status_impl(
    user_id: str,
    task_id: str,
    status: str,
    note: str
) -> dict:
    """Internal implementation with Opik tracing."""
    redis = get_redis_client()
    
    queue_key = f"user:{user_id}:queue"
    task_key = f"task:{task_id}"
    
    # Get task details
    task_data = redis.get(task_key)
    if not task_data:
        return {
            "status": "error",
            "message": f"Task {task_id} not found"
        }
    
    task = json.loads(task_data)
    
    # Update task status
    task["status"] = status
    task["updated_at"] = datetime.utcnow().isoformat()
    if note:
        task["status_note"] = note
    
    # Handle different status types
    if status == "done":
        # Remove from active queue
        redis.zrem(queue_key, task_id)
        # Move to completed set
        completed_key = f"user:{user_id}:completed"
        redis.zadd(completed_key, {task_id: datetime.utcnow().timestamp()})
        
    elif status == "blocked":
        # Lower priority but keep in queue
        current_score = redis.zscore(queue_key, task_id)
        if current_score:
            new_score = current_score * 0.5  # Reduce priority
            redis.zadd(queue_key, {task_id: new_score})
            task["priority_score"] = new_score
            
    elif status == "defer":
        # Move to bottom of queue
        redis.zadd(queue_key, {task_id: 0.1})  # Very low priority
        task["priority_score"] = 0.1
    
    # Save updated task
    redis.set(task_key, json.dumps(task))
    
    # Get next task if current was completed
    next_task = None
    if status == "done":
        # Get highest priority task
        next_tasks = redis.zrevrange(queue_key, 0, 0, withscores=True)
        if next_tasks:
            next_task_id = next_tasks[0][0]
            next_task_data = redis.get(f"task:{next_task_id}")
            if next_task_data:
                next_task = json.loads(next_task_data)
    
    return {
        "status": "updated",
        "task_id": task_id,
        "new_status": status,
        "next_task": next_task,
        "message": f"Task status updated to {status}"
    }
