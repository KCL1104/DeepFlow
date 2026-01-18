"""
Notify User Tool

Sends a system notification to the user.
"""

import json
from datetime import datetime
from typing import Literal

from langchain.tools import tool

from .base import get_redis_client, tool_with_tracing


@tool
def notify_user_tool(
    user_id: str,
    title: str,
    message: str,
    urgency: Literal["info", "warning", "critical"] = "info"
) -> dict:
    """
    Send a system notification to the user.
    
    Use this tool when you need to inform the user about:
    - Important status changes
    - Errors or issues
    - Confirmations of actions taken
    
    Args:
        user_id: The user's unique identifier
        title: Notification title (short)
        message: Notification body
        urgency: Urgency level (info/warning/critical)
    
    Returns:
        Dict with notification ID and status
    """
    return _notify_user_impl(
        user_id=user_id,
        title=title,
        message=message,
        urgency=urgency
    )


@tool_with_tracing("notify_user")
def _notify_user_impl(
    user_id: str,
    title: str,
    message: str,
    urgency: str
) -> dict:
    """Internal implementation with Opik tracing."""
    redis = get_redis_client()
    
    import uuid
    notification_id = str(uuid.uuid4())
    
    notification = {
        "id": notification_id,
        "title": title,
        "message": message,
        "urgency": urgency,
        "read": False,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Store notification
    notification_key = f"notification:{notification_id}"
    redis.set(notification_key, json.dumps(notification))
    
    # Add to user's notification list (for retrieval)
    user_notifications_key = f"user:{user_id}:notifications"
    redis.lpush(user_notifications_key, notification_id)
    
    # Keep only last 100 notifications
    redis.ltrim(user_notifications_key, 0, 99)
    
    # Publish to notification channel (for real-time SSE)
    channel_key = f"notifications:{user_id}"
    redis.publish(channel_key, json.dumps(notification))
    
    return {
        "status": "sent",
        "notification_id": notification_id,
        "message": f"Notification '{title}' sent to user"
    }
