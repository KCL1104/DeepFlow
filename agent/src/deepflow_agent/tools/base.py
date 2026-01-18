"""
Base utilities for DeepFlow Agent Tools

Provides common functionality for all tools including:
- Redis client connection
- Opik tracing decoration
- Error handling
"""

import os
from functools import wraps
from typing import Any, Callable
from opik import track
from upstash_redis import Redis

# Redis client singleton
_redis_client: Redis | None = None


def get_redis_client() -> Redis:
    """Get or create Redis client singleton."""
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
        redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        
        if not redis_url or not redis_token:
            raise ValueError(
                "Redis not configured. Set UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN"
            )
        
        _redis_client = Redis(url=redis_url, token=redis_token)
    
    return _redis_client


def tool_with_tracing(tool_name: str):
    """
    Decorator that adds Opik tracing to a tool function.
    
    Usage:
        @tool_with_tracing("add_to_queue")
        def add_to_queue(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @track(name=f"tool_{tool_name}", tags=["tool", tool_name])
        def wrapper(*args, **kwargs) -> Any:
            try:
                result = func(*args, **kwargs)
                return {
                    "success": True,
                    "tool": tool_name,
                    "result": result
                }
            except Exception as e:
                return {
                    "success": False,
                    "tool": tool_name,
                    "error": str(e)
                }
        return wrapper
    return decorator


# Priority score calculation constants
WEIGHT_URGENCY = 0.4
WEIGHT_DUE_TIME = 0.3
WEIGHT_WAIT_TIME = 0.2
WEIGHT_CONTEXT = 0.1


def calculate_priority_score(
    urgency: int,
    estimated_minutes: int = 30,
    context_match: bool = False
) -> float:
    """
    Calculate priority score for queue positioning.
    
    Formula: Score = (W1 * Urgency) + (W2 * 1/DueTime) + (W3 * WaitTime) + ContextBonus
    
    For new tasks, WaitTime = 0 and DueTime is estimated.
    """
    # Normalize urgency to 0-1 range
    normalized_urgency = urgency / 10.0
    
    # Inverse of estimated time (shorter = higher priority)
    time_factor = 1.0 / max(estimated_minutes, 1)
    
    # Context bonus
    context_bonus = WEIGHT_CONTEXT if context_match else 0.0
    
    # Calculate score (higher = more urgent)
    score = (
        WEIGHT_URGENCY * normalized_urgency * 100 +  # Scale up urgency
        WEIGHT_DUE_TIME * time_factor * 100 +
        context_bonus * 100
    )
    
    return round(score, 2)
