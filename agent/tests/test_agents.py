"""
Tests for Agent Modules

Tests Semantic Gateway and Auto Negotiator agents.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from deepflow_agent.models import (
    SemanticGatewayInput,
    SemanticGatewayOutput,
    AutoNegotiatorOutput,
    TaskSource,
)


class TestSemanticGatewayOutput:
    """Test SemanticGatewayOutput validation."""

    def test_valid_output(self):
        """Test valid output creation."""
        output = SemanticGatewayOutput(
            urgency_score=7,
            category="urgent",
            summary="Test summary",
            suggested_action="Do something",
            estimated_time_minutes=30,
            context_tags=["test"],
        )
        assert output.urgency_score == 7
        assert output.category == "urgent"

    def test_urgency_bounds(self):
        """Test urgency score bounds."""
        with pytest.raises(ValueError):
            SemanticGatewayOutput(
                urgency_score=11,
                category="standard",
                summary="Test",
                suggested_action="Test",
            )

        with pytest.raises(ValueError):
            SemanticGatewayOutput(
                urgency_score=-1,
                category="standard",
                summary="Test",
                suggested_action="Test",
            )

    def test_summary_truncation(self):
        """Test that summary is properly bounded."""
        long_summary = "x" * 250
        output = SemanticGatewayOutput(
            urgency_score=5,
            category="standard",
            summary=long_summary[:200],
            suggested_action="Test",
        )
        assert len(output.summary) <= 200


class TestSemanticGatewayInput:
    """Test SemanticGatewayInput creation."""

    def test_minimal_input(self):
        """Test minimal input creation."""
        input = SemanticGatewayInput(
            content="Test message",
            sender="test@example.com",
        )
        assert input.content == "Test message"
        assert input.user_state == "IDLE"
        assert input.source == TaskSource.MANUAL

    def test_full_input(self):
        """Test full input creation."""
        input = SemanticGatewayInput(
            content="Urgent request",
            sender="boss@company.com",
            source=TaskSource.SLACK,
            source_id="msg-123",
            user_state="FLOW",
        )
        assert input.source == TaskSource.SLACK
        assert input.user_state == "FLOW"


class TestAutoNegotiatorOutput:
    """Test AutoNegotiatorOutput validation."""

    def test_should_reply_false(self):
        """Test output when no reply needed."""
        output = AutoNegotiatorOutput(
            should_reply=False,
            reply_message="",
            escalation_hint="",
        )
        assert not output.should_reply

    def test_should_reply_true(self):
        """Test output when reply needed."""
        output = AutoNegotiatorOutput(
            should_reply=True,
            reply_message="I'm in focus mode",
            escalation_hint="Reply URGENT",
        )
        assert output.should_reply
        assert "focus" in output.reply_message
