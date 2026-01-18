"""
Task Models

Pydantic models for normalized task representation.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TaskSource(str, Enum):
    """Input source types."""
    SLACK = "slack"
    EMAIL = "email"
    JIRA = "jira"
    NOTION = "notion"
    MANUAL = "manual"


class TaskCategory(str, Enum):
    """Task urgency categories."""
    CRITICAL = "critical"    # 9-10: Interrupt immediately
    URGENT = "urgent"        # 7-8: Queue top
    STANDARD = "standard"    # 4-6: Queue normal
    LOW = "low"              # 1-3: Queue low
    DISCARD = "discard"      # 0: Ignore


class NormalizedTask(BaseModel):
    """
    Unified task representation after AI processing.
    """
    id: UUID = Field(default_factory=uuid4)
    source: TaskSource
    source_id: str
    content: str
    sender: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # AI-enriched fields
    ai_urgency: int = Field(default=0, ge=0, le=10)
    ai_category: TaskCategory = TaskCategory.STANDARD
    ai_summary: str = ""
    ai_suggested_action: str = ""
    ai_estimated_minutes: int = 15

    # Scheduling
    priority_score: float = 0.0
    context_tags: List[str] = Field(default_factory=list)


class SemanticGatewayInput(BaseModel):
    """Input for Semantic Gateway Agent."""
    content: str
    sender: str
    source: TaskSource = TaskSource.MANUAL
    source_id: str = ""
    user_state: str = "IDLE"  # FLOW, SHALLOW, IDLE


class SemanticGatewayOutput(BaseModel):
    """Output from Semantic Gateway Agent."""
    urgency_score: int = Field(ge=0, le=10)
    category: str
    summary: str = Field(max_length=200)
    suggested_action: str = Field(max_length=300)
    estimated_time_minutes: int = Field(ge=1, default=15)
    context_tags: List[str] = Field(default_factory=list)


class AutoNegotiatorOutput(BaseModel):
    """Output from Auto Negotiator Agent."""
    should_reply: bool
    reply_message: str = ""
    escalation_hint: str = "Reply 'URGENT' to bypass this filter"
