"""
Notifications API - SSE Stream for Browser Notifications

Provides Server-Sent Events endpoint for real-time browser notifications.
Agent's send_browser_notification tool publishes to Redis,
this endpoint subscribes and streams to the frontend.
"""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from upstash_redis import Redis

from ..config import get_settings

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_redis_client() -> Redis:
    """Get Upstash Redis REST client."""
    settings = get_settings()
    if not settings.upstash_redis_rest_url or not settings.upstash_redis_rest_token:
        raise ValueError(
            "Redis REST API not configured. "
            "Set UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN"
        )
    return Redis(
        url=settings.upstash_redis_rest_url,
        token=settings.upstash_redis_rest_token
    )


async def notification_stream(user_id: str, request: Request) -> AsyncGenerator[str, None]:
    """
    Generate SSE events from Redis notifications.
    
    Polls Redis list for new notifications and yields them as SSE events.
    Note: Upstash REST API doesn't support blocking operations,
    so we poll with a short interval.
    """
    redis = get_redis_client()
    notification_key = f"browser_notifications:{user_id}:pending"
    
    # Send initial connection event
    yield f"event: connected\ndata: {json.dumps({'status': 'connected', 'user_id': user_id})}\n\n"
    
    while True:
        # Check if client disconnected
        if await request.is_disconnected():
            break
        
        try:
            # Pop notification from pending list (LPOP)
            notification = redis.lpop(notification_key)
            
            if notification:
                # Parse and send as SSE event
                try:
                    data = json.loads(notification) if isinstance(notification, str) else notification
                except json.JSONDecodeError:
                    data = {"message": notification}
                
                yield f"event: notification\ndata: {json.dumps(data)}\n\n"
            else:
                # No notification, send keepalive ping
                yield f"event: ping\ndata: {json.dumps({'type': 'ping'})}\n\n"
            
            # Wait before next poll (500ms)
            await asyncio.sleep(0.5)
            
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            await asyncio.sleep(1)


@router.get("/stream/{user_id}")
async def stream_notifications(user_id: str, request: Request):
    """
    SSE endpoint for browser notifications.
    
    Frontend connects to this endpoint to receive real-time notifications
    from the Agent's send_browser_notification tool.
    
    Usage:
        const eventSource = new EventSource('/api/v1/notifications/stream/user-123');
        eventSource.addEventListener('notification', (e) => {
            const data = JSON.parse(e.data);
            new Notification(data.title, { body: data.body });
        });
    """
    return StreamingResponse(
        notification_stream(user_id, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get("/test/{user_id}")
async def test_notification(user_id: str, title: str = "Test", body: str = "This is a test notification"):
    """
    Test endpoint to manually trigger a notification.
    
    Useful for testing the SSE connection without running the Agent.
    """
    redis = get_redis_client()
    
    notification = {
        "type": "browser_notification",
        "title": title,
        "body": body,
        "urgency": "normal",
        "data": {"url": "/dashboard"}
    }
    
    # Push to pending list (same format as Agent tool)
    notification_key = f"browser_notifications:{user_id}:pending"
    redis.rpush(notification_key, json.dumps(notification))
    
    return {"status": "sent", "notification": notification}
