"""
Tests for Pydantic Schemas

Tests schema validation and serialization.
"""

import pytest
from datetime import datetime

from deepflow_backend.schemas import (
    FlowState,
    TaskStatus,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    PomodoroSettings,
    StateUpdateRequest,
)


class TestFlowState:
    """Test FlowState enum."""

    def test_valid_states(self):
        """Test all valid flow states."""
        assert FlowState.FLOW == "FLOW"
        assert FlowState.SHALLOW == "SHALLOW"
        assert FlowState.IDLE == "IDLE"


class TestTaskCreate:
    """Test TaskCreate schema."""

    def test_minimal_task(self):
        """Test creating task with minimal data."""
        task = TaskCreate(title="Test Task")
        assert task.title == "Test Task"
        assert task.urgency == 5  # default
        assert task.summary is None

    def test_full_task(self):
        """Test creating task with all fields."""
        task = TaskCreate(
            title="Full Task",
            summary="A complete task",
            suggested_action="Do something",
            urgency=8,
            estimated_minutes=45,
            context_tags=["backend", "urgent"],
        )
        assert task.title == "Full Task"
        assert task.urgency == 8
        assert len(task.context_tags) == 2

    def test_urgency_bounds(self):
        """Test urgency validation bounds."""
        with pytest.raises(ValueError):
            TaskCreate(title="Test", urgency=-1)

        with pytest.raises(ValueError):
            TaskCreate(title="Test", urgency=11)


class TestPomodoroSettings:
    """Test PomodoroSettings schema."""

    def test_default_values(self):
        """Test default pomodoro settings."""
        settings = PomodoroSettings()
        assert settings.work_minutes == 30
        assert settings.break_minutes == 5

    def test_custom_values(self):
        """Test custom pomodoro settings."""
        settings = PomodoroSettings(work_minutes=50, break_minutes=10)
        assert settings.work_minutes == 50
        assert settings.break_minutes == 10

    def test_validation_bounds(self):
        """Test validation of pomodoro time bounds."""
        with pytest.raises(ValueError):
            PomodoroSettings(work_minutes=0)

        with pytest.raises(ValueError):
            PomodoroSettings(work_minutes=121)


class TestStateUpdateRequest:
    """Test StateUpdateRequest schema."""

    def test_valid_state_update(self):
        """Test valid state update request."""
        request = StateUpdateRequest(state=FlowState.FLOW)
        assert request.state == FlowState.FLOW
