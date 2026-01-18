"""
Tests for Evaluation Metrics

Tests the custom Opik evaluation metrics.
"""

import pytest

from deepflow_agent.metrics import (
    UrgencyAccuracyMetric,
    CategoryAccuracyMetric,
    SummaryQualityMetric,
    ActionabilityMetric,
)


class TestUrgencyAccuracyMetric:
    """Test UrgencyAccuracyMetric."""

    def test_perfect_match(self):
        """Test perfect urgency match."""
        metric = UrgencyAccuracyMetric()
        score = metric.score(
            output={"urgency_score": 7},
            expected={"urgency_score": 7},
        )
        assert score == 1.0

    def test_off_by_one(self):
        """Test off by one urgency."""
        metric = UrgencyAccuracyMetric()
        score = metric.score(
            output={"urgency_score": 7},
            expected={"urgency_score": 8},
        )
        assert score == 0.9

    def test_off_by_five(self):
        """Test off by five urgency."""
        metric = UrgencyAccuracyMetric()
        score = metric.score(
            output={"urgency_score": 10},
            expected={"urgency_score": 5},
        )
        assert score == 0.5

    def test_maximum_difference(self):
        """Test maximum urgency difference."""
        metric = UrgencyAccuracyMetric()
        score = metric.score(
            output={"urgency_score": 0},
            expected={"urgency_score": 10},
        )
        assert score == 0.0


class TestCategoryAccuracyMetric:
    """Test CategoryAccuracyMetric."""

    def test_matching_category(self):
        """Test matching categories."""
        metric = CategoryAccuracyMetric()
        score = metric.score(
            output={"category": "urgent"},
            expected={"category": "urgent"},
        )
        assert score == 1.0

    def test_non_matching_category(self):
        """Test non-matching categories."""
        metric = CategoryAccuracyMetric()
        score = metric.score(
            output={"category": "urgent"},
            expected={"category": "low"},
        )
        assert score == 0.0


class TestSummaryQualityMetric:
    """Test SummaryQualityMetric."""

    def test_empty_summary(self):
        """Test empty summary."""
        metric = SummaryQualityMetric()
        score = metric.score(
            output={"summary": ""},
            input={"content": "Some content here"},
        )
        assert score == 0.0

    def test_good_summary(self):
        """Test a good summary."""
        metric = SummaryQualityMetric()
        score = metric.score(
            output={"summary": "This is a summary about important tasks"},
            input={"content": "Some content about important tasks to complete"},
        )
        assert score >= 0.5


class TestActionabilityMetric:
    """Test ActionabilityMetric."""

    def test_empty_action(self):
        """Test empty action."""
        metric = ActionabilityMetric()
        score = metric.score(output={"suggested_action": ""})
        assert score == 0.0

    def test_actionable_action(self):
        """Test actionable suggestion."""
        metric = ActionabilityMetric()
        score = metric.score(
            output={"suggested_action": "Review the pull request and approve if tests pass"}
        )
        assert score >= 0.7

    def test_non_actionable_action(self):
        """Test non-actionable suggestion."""
        metric = ActionabilityMetric()
        score = metric.score(output={"suggested_action": "ok"})
        assert score < 0.5
