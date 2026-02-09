"""
Add to Queue Tool

Adds a task to the user's priority queue.
Uses Supabase for persistence and Redis for queue ordering.
"""

import json
import uuid
from datetime import datetime
from typing import Literal

from langchain.tools import tool

from ..config import get_settings
from .base import get_redis_client, calculate_priority_score, tool_with_tracing


@tool
def add_to_queue(
    user_id: str,
    task_summary: str,
    urgency_score: int,
    category: Literal["critical", "urgent", "standard", "low", "discard"],
    source: Literal["slack", "email", "telegram", "manual"],
    source_id: str = "",
    estimated_minutes: int = 15
) -> dict:
    """
    Add a task to the user's priority queue.
    
    Use this tool when a message needs to be queued for later attention.
    The task will be sorted by priority score based on urgency and other factors.
    
    Args:
        user_id: The user's unique identifier
        task_summary: Brief summary of the task (max 200 chars)
        urgency_score: Urgency level from 0-10
        category: Task category (critical/urgent/standard/low/discard)
        source: Where the task originated from
        source_id: Original message ID from the source
        estimated_minutes: Estimated time to complete (default 15)
    
    Returns:
        Dict with task_id, position in queue, and queue length
    """
    return _add_to_queue_impl(
        user_id=user_id,
        task_summary=task_summary,
        urgency_score=urgency_score,
        category=category,
        source=source,
        source_id=source_id,
        estimated_minutes=estimated_minutes
    )


@tool_with_tracing("add_to_queue")
def _add_to_queue_impl(
    user_id: str,
    task_summary: str,
    urgency_score: int,
    category: str,
    source: str,
    source_id: str,
    estimated_minutes: int
) -> dict:
    """Internal implementation with Supabase persistence and Redis queue."""
    settings = get_settings()
    redis = get_redis_client()
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Calculate priority score
    priority_score = calculate_priority_score(
        urgency=urgency_score,
        estimated_minutes=estimated_minutes
    )
    
    # Derive title from summary
    title = task_summary[:50] if len(task_summary) < 50 else f"Task from {source.title()}"
    
    # 1. Persist to Supabase (if configured)
    supabase_success = False
    if settings.supabase_url and settings.supabase_service_role_key:
        try:
            from supabase import create_client
            supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
            
            task_data = {
                "id": task_id,
                "user_id": user_id,
                "title": title,
                "summary": task_summary[:200],
                "suggested_action": f"Review {source} message",
                "urgency": urgency_score,
                "estimated_minutes": estimated_minutes,
                "context_tags": [category, source],
                "source": source,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
            }
            
            supabase.table("tasks").insert(task_data).execute()
            supabase_success = True
        except Exception as e:
            # Log but don't fail - still add to Redis queue
            print(f"Warning: Failed to persist to Supabase: {e}")
    
    # 2. Add to Redis queue (always)
    queue_key = f"user:queue:{user_id}"
    task_key = f"task:{task_id}"
    
    # Store task details in Redis as backup
    task = {
        "id": task_id,
        "summary": task_summary[:200],
        "urgency_score": urgency_score,
        "category": category,
        "source": source,
        "source_id": source_id,
        "estimated_minutes": estimated_minutes,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "priority_score": priority_score,
    }
    
    redis.set(task_key, json.dumps(task))
    redis.zadd(queue_key, {task_id: priority_score})
    
    # Get queue info
    queue_length = redis.zcard(queue_key)
    position = redis.zrevrank(queue_key, task_id)
    
    return {
        "task_id": task_id,
        "priority_score": priority_score,
        "position": position + 1 if position is not None else 1,
        "queue_length": queue_length,
        "persisted_to_db": supabase_success,
        "message": f"Task added to queue at position {position + 1 if position is not None else 1}"
    }
