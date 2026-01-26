"""
Send Telegram Notification Tool

Sends a Telegram push notification for urgent/critical items.
Uses the Telegram Bot API to directly message users who have linked their accounts.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Literal

from langchain.tools import tool
from telegram import Bot
from dotenv import load_dotenv

from .base import get_redis_client, tool_with_tracing

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def get_telegram_bot() -> Bot:
    """Get Telegram Bot instance."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")
    return Bot(token=token)


def get_telegram_id_for_user(user_id: str) -> str | None:
    """Get Telegram ID for a DeepFlow user."""
    redis = get_redis_client()
    key = f"deepflow_binding:{user_id}"
    return redis.get(key)


@tool
def send_telegram_notification(
    user_id: str,
    title: str,
    body: str,
    urgency: Literal["normal", "urgent", "critical"] = "normal",
    action_url: str = "/dashboard"
) -> dict:
    """
    Send a Telegram push notification for urgent items.
    
    Use this tool when:
    - An urgent or critical task enters the queue
    - User needs immediate attention on something
    - Important alerts that should interrupt the user
    
    The notification will be sent to the user's Telegram if they have
    linked their account.
    
    Args:
        user_id: The user's unique identifier
        title: Notification title (short, attention-grabbing)
        body: Notification body (brief description)
        urgency: Urgency level affects styling
        action_url: URL reference (not clickable in TG)
    
    Returns:
        Dict with notification status
    """
    return _send_telegram_notification_impl(
        user_id=user_id,
        title=title,
        body=body,
        urgency=urgency,
        action_url=action_url
    )


@tool_with_tracing("send_telegram_notification")
def _send_telegram_notification_impl(
    user_id: str,
    title: str,
    body: str,
    urgency: str,
    action_url: str
) -> dict:
    """Implementation with Opik tracing."""
    
    # Get Telegram ID for this user
    telegram_id = get_telegram_id_for_user(user_id)
    
    if not telegram_id:
        logger.warning(f"No Telegram binding for user {user_id}")
        return {
            "success": False,
            "error": "User has not linked Telegram account",
            "user_id": user_id
        }
    
    # Format message based on urgency
    urgency_emoji = {
        "normal": "ℹ️",
        "urgent": "⚠️",
        "critical": "🚨"
    }
    
    urgency_label = {
        "normal": "Info",
        "urgent": "URGENT",
        "critical": "CRITICAL"
    }
    
    message = (
        f"{urgency_emoji.get(urgency, 'ℹ️')} *{urgency_label.get(urgency, 'Info')}*\n\n"
        f"*{title}*\n\n"
        f"{body}"
    )
    
    try:
        # Send message via Telegram Bot API
        bot = get_telegram_bot()
        
        # Run async send in sync context
        async def send():
            await bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode="Markdown"
            )
        
        asyncio.run(send())
        
        logger.info(f"Telegram notification sent to {user_id} ({telegram_id})")
        
        # Log to Redis for history
        redis = get_redis_client()
        notification = {
            "type": "telegram_notification",
            "title": title,
            "body": body,
            "urgency": urgency,
            "sent_at": datetime.now().isoformat(),
            "telegram_id": telegram_id
        }
        
        history_key = f"user:{user_id}:telegram_notification_history"
        redis.lpush(history_key, json.dumps(notification))
        redis.ltrim(history_key, 0, 99)  # Keep last 100
        
        return {
            "success": True,
            "message": "Telegram notification sent",
            "user_id": user_id,
            "telegram_id": telegram_id,
            "urgency": urgency
        }
        
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")
        return {
            "success": False,
            "error": str(e),
            "user_id": user_id
        }


# Convenience function for use outside of Agent context
def notify_user_telegram(user_id: str, title: str, body: str, urgency: str = "normal"):
    """
    Send a Telegram notification (non-tool version for direct calls).
    
    Can be called from anywhere without needing Agent context.
    """
    return _send_telegram_notification_impl(
        user_id=user_id,
        title=title,
        body=body,
        urgency=urgency,
        action_url="/dashboard"
    )
