"""
Priority Engine Service

Calculates dynamic priority scores for tasks based on multiple factors:
- AI-assessed urgency
- Time until deadline
- Wait time in queue (prevent starvation)
- Context bonus (matching current project)
"""

from datetime import datetime
from typing import Optional


class PriorityEngine:
    """
    Dynamic priority calculator.
    
    Formula:
    Score = (W1 × Urgency) + (W2 × 1/DueTime) + (W3 × WaitTime) + ContextBonus
    """

    # Default weights
    W_URGENCY = 0.4
    W_DEADLINE = 0.3
    W_WAIT_TIME = 0.2
    W_CONTEXT = 0.1

    def __init__(
        self,
        w_urgency: float = 0.4,
        w_deadline: float = 0.3,
        w_wait_time: float = 0.2,
        w_context: float = 0.1,
    ):
        self.w_urgency = w_urgency
        self.w_deadline = w_deadline
        self.w_wait_time = w_wait_time
        self.w_context = w_context

    def calculate_score(
        self,
        urgency: int,
        deadline: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        context_tags: Optional[list[str]] = None,
        current_context: Optional[str] = None,
    ) -> float:
        """
        Calculate priority score for a task.
        
        Args:
            urgency: AI-assessed urgency (0-10)
            deadline: Task deadline (optional)
            created_at: When task was created (for wait time)
            context_tags: Task context tags
            current_context: User's current project context
            
        Returns:
            Priority score (higher = more urgent)
        """
        now = datetime.utcnow()
        score = 0.0

        # Urgency component (0-100)
        urgency_score = urgency * 10
        score += self.w_urgency * urgency_score

        # Deadline component
        if deadline:
            hours_until = (deadline - now).total_seconds() / 3600
            if hours_until > 0:
                # Closer deadline = higher score, capped at 100
                deadline_score = min(100, 100 / max(1, hours_until))
                score += self.w_deadline * deadline_score
            else:
                # Past deadline = maximum urgency
                score += self.w_deadline * 100

        # Wait time component (prevent starvation)
        if created_at:
            hours_waiting = (now - created_at).total_seconds() / 3600
            # Cap at 48 hours for scoring
            wait_score = min(100, hours_waiting * 2)
            score += self.w_wait_time * wait_score

        # Context bonus
        if context_tags and current_context:
            if current_context.lower() in [tag.lower() for tag in context_tags]:
                score += self.w_context * 50  # Bonus for matching context

        return round(score, 2)

    def recalculate_all(
        self,
        tasks: list[dict],
        current_context: Optional[str] = None,
    ) -> dict[str, float]:
        """
        Recalculate priority scores for all tasks.
        
        Args:
            tasks: List of task dictionaries with urgency, deadline, created_at, context_tags
            current_context: User's current project context
            
        Returns:
            Dict mapping task_id to new priority score
        """
        scores = {}
        for task in tasks:
            score = self.calculate_score(
                urgency=task.get("urgency", 5),
                deadline=task.get("deadline"),
                created_at=task.get("created_at"),
                context_tags=task.get("context_tags", []),
                current_context=current_context,
            )
            scores[task["id"]] = score
        return scores


# Global instance with default weights
priority_engine = PriorityEngine()
