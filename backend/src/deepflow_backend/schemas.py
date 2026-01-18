"""
Pydantic Schemas for API requests and responses.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class FlowState(str, Enum):
    """User focus state."""

    FLOW = "FLOW"
    SHALLOW = "SHALLOW"
    IDLE = "IDLE"


class TaskStatus(str, Enum):
    """Task status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    DEFERRED = "deferred"


# --- State Schemas ---


class StateResponse(BaseModel):
    """Response for user state."""

    state: FlowState
    user_id: str


class StateUpdateRequest(BaseModel):
    """Request to update user state."""

    state: FlowState


# --- Task Schemas ---


class TaskBase(BaseModel):
    """Base task model."""

    title: str
    summary: Optional[str] = None
    suggested_action: Optional[str] = None
    urgency: int = Field(default=5, ge=0, le=10)
    estimated_minutes: Optional[int] = None
    deadline: Optional[datetime] = None
    context_tags: List[str] = Field(default_factory=list)


class TaskCreate(TaskBase):
    """Request to create a task."""

    pass


class TaskUpdate(BaseModel):
    """Request to update a task."""

    title: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[TaskStatus] = None
    urgency: Optional[int] = Field(default=None, ge=0, le=10)


class TaskResponse(TaskBase):
    """Task response model."""

    id: str
    status: TaskStatus
    priority_score: float = 0.0
    created_at: datetime
    completed_at: Optional[datetime] = None


class QueueResponse(BaseModel):
    """Response for task queue."""

    current_task: Optional[TaskResponse] = None
    queue: List[TaskResponse]
    total_count: int


# --- Pomodoro Schemas ---


class PomodoroSettings(BaseModel):
    """Pomodoro timer settings."""

    work_minutes: int = Field(default=30, ge=1, le=120)
    break_minutes: int = Field(default=5, ge=1, le=60)
