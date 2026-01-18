"""
Send Auto Reply Tool

Automatically sends a reply to a message on behalf of the user.
Currently supports Slack integration.
"""

import os
from typing import Literal, Optional

from langchain.tools import tool

from .base import tool_with_tracing


# Slack client placeholder - will be initialized on first use
_slack_client = None


def get_slack_client():
    """Get or create Slack client."""
    global _slack_client
    if _slack_client is None:
        try:
            from slack_sdk import WebClient
            token = os.getenv("SLACK_BOT_TOKEN")
            if not token:
                raise ValueError("SLACK_BOT_TOKEN not configured")
            _slack_client = WebClient(token=token)
        except ImportError:
            raise ImportError("slack_sdk not installed. Run: pip install slack_sdk")
    return _slack_client


@tool
def send_auto_reply(
    channel: Literal["slack", "email", "telegram"],
    recipient: str,
    message: str,
    original_msg_id: str = "",
    thread_ts: Optional[str] = None
) -> dict:
    """
    Send an automatic reply on behalf of the user when they are in focus mode.
    
    Use this tool when:
    - User is in FLOW state and the message is not urgent enough to interrupt
    - A polite acknowledgment or deferral is needed
    
    Args:
        channel: The communication channel (slack/email/telegram)
        recipient: Channel ID (Slack) or email address
        message: The reply message to send
        original_msg_id: ID of the original message being replied to
        thread_ts: Slack thread timestamp (for threaded replies)
    
    Returns:
        Dict with status and message ID if successful
    """
    return _send_auto_reply_impl(
        channel=channel,
        recipient=recipient,
        message=message,
        original_msg_id=original_msg_id,
        thread_ts=thread_ts
    )


@tool_with_tracing("send_auto_reply")
def _send_auto_reply_impl(
    channel: str,
    recipient: str,
    message: str,
    original_msg_id: str,
    thread_ts: Optional[str]
) -> dict:
    """Internal implementation with Opik tracing."""
    
    if channel == "slack":
        return _send_slack_reply(recipient, message, thread_ts)
    elif channel == "email":
        # Email integration placeholder
        return {
            "status": "not_implemented",
            "message": "Email auto-reply not yet implemented"
        }
    elif channel == "telegram":
        # Telegram integration placeholder
        return {
            "status": "not_implemented", 
            "message": "Telegram auto-reply not yet implemented"
        }
    else:
        return {
            "status": "error",
            "message": f"Unknown channel: {channel}"
        }


def _send_slack_reply(channel_id: str, message: str, thread_ts: Optional[str]) -> dict:
    """Send a Slack message."""
    try:
        client = get_slack_client()
        
        # Build message payload
        kwargs = {
            "channel": channel_id,
            "text": message,
        }
        
        # Add thread_ts for threaded replies
        if thread_ts:
            kwargs["thread_ts"] = thread_ts
        
        # Send message
        response = client.chat_postMessage(**kwargs)
        
        return {
            "status": "sent",
            "channel": channel_id,
            "message_ts": response["ts"],
            "message": "Auto-reply sent successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send Slack message: {str(e)}"
        }
