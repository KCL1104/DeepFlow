"""
Send Browser Notification Tool

Sends a browser push notification for urgent items.
Uses Redis pub/sub to communicate with the frontend via SSE.
"""

import json
from datetime import datetime
from typing import Literal

from langchain.tools import tool

from .base import get_redis_client, tool_with_tracing


@tool
def send_browser_notification(
    user_id: str,
    title: str,
    body: str,
    urgency: Literal["normal", "urgent", "critical"] = "normal",
    action_url: str = "/dashboard"
) -> dict:
    """
    Send a browser push notification for urgent items.
    
    Use this tool when:
    - An urgent or critical task enters the queue
    - User needs immediate attention on something
    - Important alerts that should bypass the queue view
    
    The notification will appear in the user's browser if they have
    notifications enabled.
    
    Args:
        user_id: The user's unique identifier
        title: Notification title (short, attention-grabbing)
        body: Notification body (brief description)
        urgency: Urgency level affects visual styling
        action_url: URL to open when notification is clicked
    
    Returns:
        Dict with notification status
    """
    return _send_browser_notification_impl(
        user_id=user_id,
        title=title,
        body=body,
        urgency=urgency,
        action_url=action_url
    )


@tool_with_tracing("send_browser_notification")
def _send_browser_notification_impl(
    user_id: str,
    title: str,
    body: str,
    urgency: str,
    action_url: str
) -> dict:
    """Internal implementation with Opik tracing."""
    redis = get_redis_client()
    
    import uuid
    notification_id = str(uuid.uuid4())
    
    # Create browser notification payload
    # This follows the Web Notification API structure
    browser_notification = {
        "id": notification_id,
        "type": "browser_notification",
        "title": title,
        "body": body,
        "urgency": urgency,
        "data": {
            "url": action_url,
            "notification_id": notification_id
        },
        "created_at": datetime.utcnow().isoformat(),
        # Browser notification options
        "options": {
            "tag": f"deepflow-{urgency}",  # Group similar notifications
            "requireInteraction": urgency in ["urgent", "critical"],
            "silent": urgency == "normal",
            "icon": "/icons/deepflow-icon.png",
            "badge": "/icons/deepflow-badge.png",
        }
    }
    
    # Add urgency-specific styling hints
    if urgency == "critical":
        browser_notification["options"]["vibrate"] = [200, 100, 200]
        browser_notification["options"]["renotify"] = True
    elif urgency == "urgent":
        browser_notification["options"]["vibrate"] = [100, 50, 100]
    
    # Push to pending list for SSE polling
    # (Upstash REST API doesn't support pub/sub, so we use a list)
    pending_key = f"browser_notifications:{user_id}:pending"
    redis.rpush(pending_key, json.dumps(browser_notification))
    
    # Also store for history/debugging
    history_key = f"user:{user_id}:browser_notification_history"
    redis.lpush(history_key, json.dumps(browser_notification))
    redis.ltrim(history_key, 0, 49)  # Keep last 50
    
    return {
        "status": "sent",
        "notification_id": notification_id,
        "urgency": urgency,
        "message": f"Browser notification '{title}' pushed to user"
    }
