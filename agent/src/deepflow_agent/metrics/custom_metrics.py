"""
Custom Evaluation Metrics for Opik

Defines metrics for evaluating agent performance.
"""

from typing import Any, Dict

# Try to import opik metrics
try:
    from opik.evaluation.metrics import BaseMetric

    OPIK_METRICS_AVAILABLE = True
except ImportError:
    OPIK_METRICS_AVAILABLE = False
    BaseMetric = object


class UrgencyAccuracyMetric(BaseMetric if OPIK_METRICS_AVAILABLE else object):
    """
    Measures how accurately the agent scores urgency.

    Compares predicted urgency_score to expected_urgency.
    A smaller difference is better.
    """

    name = "urgency_accuracy"

    def score(self, output: Dict[str, Any], expected: Dict[str, Any], **kwargs) -> float:
        """
        Calculate urgency accuracy.

        Returns a score from 0 to 1, where 1 is perfect match.
        """
        predicted = output.get("urgency_score", 5)
        actual = expected.get("urgency_score", 5)

        # Score decreases with larger differences
        diff = abs(predicted - actual)
        return max(0, 1 - (diff / 10))


class CategoryAccuracyMetric(BaseMetric if OPIK_METRICS_AVAILABLE else object):
    """
    Measures if the agent correctly categorized the task.
    """

    name = "category_accuracy"

    def score(self, output: Dict[str, Any], expected: Dict[str, Any], **kwargs) -> float:
        """Returns 1.0 if categories match, 0.0 otherwise."""
        predicted = output.get("category", "standard")
        actual = expected.get("category", "standard")
        return 1.0 if predicted == actual else 0.0


class SummaryQualityMetric(BaseMetric if OPIK_METRICS_AVAILABLE else object):
    """
    Measures summary quality using simple heuristics.

    - Length: Should be reasonable (20-200 chars)
    - Not empty
    - Contains key terms from original content
    """

    name = "summary_quality"

    def score(self, output: Dict[str, Any], input: Dict[str, Any], **kwargs) -> float:
        """Calculate summary quality score."""
        summary = output.get("summary", "")
        content = input.get("content", "")

        if not summary:
            return 0.0

        score = 0.0

        # Length check (20-200 chars ideal)
        length = len(summary)
        if 20 <= length <= 200:
            score += 0.4
        elif length > 0:
            score += 0.2

        # Contains key terms
        content_words = set(content.lower().split())
        summary_words = set(summary.lower().split())
        overlap = len(content_words & summary_words)
        if overlap >= 3:
            score += 0.4
        elif overlap >= 1:
            score += 0.2

        # Not just copied content
        if summary.lower() != content.lower()[:len(summary)]:
            score += 0.2

        return min(1.0, score)


class ActionabilityMetric(BaseMetric if OPIK_METRICS_AVAILABLE else object):
    """
    Measures if the suggested action is actionable.
    """

    name = "actionability"

    def score(self, output: Dict[str, Any], **kwargs) -> float:
        """Calculate actionability score."""
        action = output.get("suggested_action", "")

        if not action:
            return 0.0

        score = 0.0

        # Has content
        if len(action) >= 10:
            score += 0.3

        # Contains action verbs
        action_verbs = ["review", "respond", "check", "fix", "update", "contact",
                       "schedule", "approve", "reject", "deploy", "test", "call"]
        if any(verb in action.lower() for verb in action_verbs):
            score += 0.4

        # Reasonable length
        if 20 <= len(action) <= 300:
            score += 0.3

        return min(1.0, score)


# Export metrics
EVALUATION_METRICS = [
    UrgencyAccuracyMetric,
    CategoryAccuracyMetric,
    SummaryQualityMetric,
    ActionabilityMetric,
]
