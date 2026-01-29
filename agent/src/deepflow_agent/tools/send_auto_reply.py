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
    message: str = "",
    original_msg_id: str = "",
    thread_ts: Optional[str] = None,
    sender_name: str = "Unknown",
    incoming_content: str = "",
    urgency_score: int = 5,
    user_state: str = "FLOW"
) -> dict:
    """
    Send an automatic reply on behalf of the user.
    
    If 'message' is provided, it sends that exact text.
    If 'message' is empty, it uses the Auto-Negotiator to generate a polite,
    context-aware refusal based on the incoming content and user state.
    
    Args:
        channel: The communication channel (slack/email/telegram)
        recipient: Channel ID (Slack/Telegram) or email address
        message: Specific message to send (optional)
        original_msg_id: ID of the original message being replied to
        thread_ts: Slack thread timestamp
        sender_name: Name of the person who sent the message
        incoming_content: Content of the message being replied to
        urgency_score: Urgency of the incoming message (0-10)
        user_state: Current user state (FLOW/SHALLOW/IDLE)
    
    Returns:
        Dict with status and message ID if successful
    """
    return _send_auto_reply_impl(
        channel=channel,
        recipient=recipient,
        message=message,
        original_msg_id=original_msg_id,
        thread_ts=thread_ts,
        sender_name=sender_name,
        incoming_content=incoming_content,
        urgency_score=urgency_score,
        user_state=user_state
    )



# Helpers needed for Telegram
def get_telegram_bot():
    """Get Telegram Bot instance."""
    from telegram import Bot
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")
    return Bot(token=token)

def get_telegram_id_for_user(user_id: str) -> Optional[str]:
    """Get Telegram ID for a DeepFlow user."""
    from .base import get_redis_client
    redis = get_redis_client()
    key = f"deepflow_binding:{user_id}"
    return redis.get(key)

def _send_telegram_reply(user_id: str, message: str) -> dict:
    """Send a Telegram message (reply)."""
    import asyncio
    try:
        telegram_id = get_telegram_id_for_user(user_id)
        if not telegram_id:
            return {
                "status": "error",
                "message": f"User {user_id} has not linked Telegram account"
            }
        
        bot = get_telegram_bot()
        
        async def send():
            await bot.send_message(
                chat_id=telegram_id,
                text=message
            )
        
        asyncio.run(send())
        
        return {
            "status": "sent",
            "channel": "telegram",
            "recipient": user_id,
            "message": "Telegram reply sent successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send Telegram reply: {str(e)}"
        }

@tool_with_tracing("send_auto_reply")
def _send_auto_reply_impl(
    channel: str,
    recipient: str,
    message: str,
    original_msg_id: str,
    thread_ts: Optional[str],
    sender_name: str = "",
    incoming_content: str = "",
    urgency_score: int = 0,
    user_state: str = "FLOW"
) -> dict:
    """Internal implementation with Opik tracing."""
    
    # Generate message if not provided
    if not message and incoming_content:
        try:
            negotiator = create_auto_negotiator()
            
            # Run sync for tool context
            result = negotiator.generate_reply_sync(
                content=incoming_content,
                sender=sender_name,
                urgency_score=urgency_score,
                summary=incoming_content[:100],
                user_state=user_state
            )
            
            if result.should_reply:
                message = result.reply_message
            else:
                return {
                    "status": "skipped",
                    "reason": "Auto-Negotiator decided not to reply (likely too urgent or unnecessary)",
                    "escalation_hint": result.escalation_hint
                }
                
        except Exception as e:
            # Fallback if generation fails
            message = "I'm currently in a focus session and will get back to you later."
            
    if not message:
         return {
            "status": "skipped",
            "reason": "No message provided and generation failed or was insufficient"
        }

    if channel == "slack":
        return _send_slack_reply(recipient, message, thread_ts)
    elif channel == "email":
        return _send_email_reply(recipient, message, sender_name)
    elif channel == "telegram":
        return _send_telegram_reply(recipient, message)
    else:
        return {
            "status": "error",
            "message": f"Unknown channel: {channel}"
        }


def _send_slack_reply(channel_id: str, message: str, thread_ts: Optional[str]) -> dict:
    """Send a Slack message."""
    # ... existing slack implementation ...
    try:
        client = get_slack_client()
        
        kwargs = {
            "channel": channel_id,
            "text": message,
        }
        
        if thread_ts:
            kwargs["thread_ts"] = thread_ts
        
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

def _send_email_reply(recipient: str, message: str, subject_prefix: str = "Re:") -> dict:
    """Send an email reply via SMTP."""
    import smtplib
    from email.mime.text import MIMEText
    
    smtp_server = os.environ.get("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    username = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASSWORD")
    
    if not username or not password:
         return {
            "status": "error",
            "message": "Email not configured (EMAIL_USER/EMAIL_PASSWORD missing)"
        }
    
    try:
        msg = MIMEText(message)
        msg["Subject"] = f"Auto-Reply: {subject_prefix}"
        msg["From"] = username
        msg["To"] = recipient

        with smtplib.SMTP_SSL(smtp_server, 465) as smtp:
            smtp.login(username, password)
            smtp.send_message(msg)
            
        return {
            "status": "sent",
            "channel": "email",
            "recipient": recipient,
            "message": "Email reply sent successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send email: {str(e)}"
        }

