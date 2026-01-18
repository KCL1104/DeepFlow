"""
Redis Client Module

Provides async Redis client for state storage and priority queue.
Uses Upstash Redis (serverless).
"""

from functools import lru_cache
from typing import Optional, List
import json

import redis

from ..config import get_settings


@lru_cache
def get_redis_client() -> redis.Redis:
    """Get cached Redis client."""
    settings = get_settings()
    return redis.from_url(settings.upstash_redis_url, decode_responses=True)


class UserStateManager:
    """Manage user focus state in Redis."""

    STATE_KEY_PREFIX = "user:state:"
    VALID_STATES = {"FLOW", "SHALLOW", "IDLE"}

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def get_state(self, user_id: str) -> str:
        """Get user's current focus state."""
        state = self.redis.get(f"{self.STATE_KEY_PREFIX}{user_id}")
        return state if state in self.VALID_STATES else "IDLE"

    def set_state(self, user_id: str, state: str) -> bool:
        """Set user's focus state."""
        if state not in self.VALID_STATES:
            return False
        self.redis.set(f"{self.STATE_KEY_PREFIX}{user_id}", state)
        return True


class TaskQueueManager:
    """Manage task priority queue in Redis using Sorted Sets."""

    QUEUE_KEY_PREFIX = "user:queue:"
    CURRENT_TASK_PREFIX = "user:current:"

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def _queue_key(self, user_id: str) -> str:
        return f"{self.QUEUE_KEY_PREFIX}{user_id}"

    def _current_key(self, user_id: str) -> str:
        return f"{self.CURRENT_TASK_PREFIX}{user_id}"

    def add_task(self, user_id: str, task_id: str, score: float) -> None:
        """Add task to priority queue with score."""
        self.redis.zadd(self._queue_key(user_id), {task_id: score})

    def pop_next(self, user_id: str) -> Optional[str]:
        """Pop highest priority task from queue."""
        result = self.redis.zpopmax(self._queue_key(user_id), count=1)
        if result:
            task_id, _ = result[0]
            return task_id
        return None

    def peek(self, user_id: str, count: int = 5) -> List[tuple]:
        """Get top N tasks without removing them."""
        return self.redis.zrevrange(
            self._queue_key(user_id), 0, count - 1, withscores=True
        )

    def get_queue_length(self, user_id: str) -> int:
        """Get number of tasks in queue."""
        return self.redis.zcard(self._queue_key(user_id))

    def remove_task(self, user_id: str, task_id: str) -> bool:
        """Remove specific task from queue."""
        return self.redis.zrem(self._queue_key(user_id), task_id) > 0

    def update_score(self, user_id: str, task_id: str, new_score: float) -> None:
        """Update task's priority score."""
        self.redis.zadd(self._queue_key(user_id), {task_id: new_score})

    def set_current_task(self, user_id: str, task_id: str) -> None:
        """Set current active task."""
        self.redis.set(self._current_key(user_id), task_id)

    def get_current_task(self, user_id: str) -> Optional[str]:
        """Get current active task ID."""
        return self.redis.get(self._current_key(user_id))

    def clear_current_task(self, user_id: str) -> None:
        """Clear current task."""
        self.redis.delete(self._current_key(user_id))
