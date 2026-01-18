"""
Tests for Priority Engine Service

Tests the dynamic priority scoring algorithm.
"""

import pytest
from datetime import datetime, timedelta

from deepflow_backend.services.priority_engine import PriorityEngine, priority_engine


class TestPriorityEngine:
    """Test cases for PriorityEngine."""

    def test_basic_urgency_score(self):
        """Test that urgency contributes to score."""
        engine = PriorityEngine()

        low_urgency = engine.calculate_score(urgency=2)
        high_urgency = engine.calculate_score(urgency=9)

        assert high_urgency > low_urgency
        assert low_urgency > 0

    def test_deadline_increases_score(self):
        """Test that closer deadline increases score."""
        engine = PriorityEngine()

        far_deadline = datetime.utcnow() + timedelta(days=7)
        near_deadline = datetime.utcnow() + timedelta(hours=2)

        score_far = engine.calculate_score(urgency=5, deadline=far_deadline)
        score_near = engine.calculate_score(urgency=5, deadline=near_deadline)

        assert score_near > score_far

    def test_past_deadline_maximum_urgency(self):
        """Test that past deadline gives maximum deadline score."""
        engine = PriorityEngine()

        past_deadline = datetime.utcnow() - timedelta(hours=1)
        future_deadline = datetime.utcnow() + timedelta(hours=2)  # Give more time

        score_past = engine.calculate_score(urgency=5, deadline=past_deadline)
        score_future = engine.calculate_score(urgency=5, deadline=future_deadline)

        assert score_past >= score_future

    def test_wait_time_prevents_starvation(self):
        """Test that wait time increases score over time."""
        engine = PriorityEngine()

        old_task = datetime.utcnow() - timedelta(hours=24)
        new_task = datetime.utcnow() - timedelta(hours=1)

        score_old = engine.calculate_score(urgency=3, created_at=old_task)
        score_new = engine.calculate_score(urgency=3, created_at=new_task)

        assert score_old > score_new

    def test_context_bonus(self):
        """Test that matching context gives bonus."""
        engine = PriorityEngine()

        base_score = engine.calculate_score(
            urgency=5,
            context_tags=["backend", "api"],
            current_context="frontend",
        )

        context_match_score = engine.calculate_score(
            urgency=5,
            context_tags=["backend", "api"],
            current_context="backend",
        )

        assert context_match_score > base_score

    def test_recalculate_all(self):
        """Test bulk recalculation of priority scores."""
        engine = PriorityEngine()

        tasks = [
            {"id": "1", "urgency": 8},
            {"id": "2", "urgency": 3},
            {"id": "3", "urgency": 5},
        ]

        scores = engine.recalculate_all(tasks)

        assert len(scores) == 3
        assert scores["1"] > scores["2"]
        assert scores["1"] > scores["3"]

    def test_global_instance_exists(self):
        """Test that global priority_engine instance is available."""
        assert priority_engine is not None
        assert isinstance(priority_engine, PriorityEngine)
