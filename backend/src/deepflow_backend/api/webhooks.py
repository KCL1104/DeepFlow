"""
Webhooks API - Ingestion Endpoint for External Signals

Receives webhooks from external services (Slack, Jira, etc.)
and pushes them to the Redis queue for the Agent to process.
"""

import json
import logging
import time
from typing import Any, Dict, Literal

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from upstash_redis import Redis

from ..config import get_settings

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

class WebhookPayload(BaseModel):
    source: Literal["slack", "email", "jira", "notion", "manual"]
    content: str
    sender: str
    source_id: str | None = None
    metadata: Dict[str, Any] = {}

def get_redis_client() -> Redis:
    """Get Upstash Redis REST client."""
    settings = get_settings()
    if not settings.upstash_redis_rest_url or not settings.upstash_redis_rest_token:
        # For local development without proper env, we might want to warn or fail
        # But failing is better to signal config error
        raise ValueError("Redis configuration missing")
    return Redis(
        url=settings.upstash_redis_rest_url,
        token=settings.upstash_redis_rest_token
    )

def push_to_queue(payload: WebhookPayload):
    """Background task to push signal to Redis."""
    try:
        redis = get_redis_client()
        
        # Structure the signal for the Agent
        signal = {
            "type": "incoming_signal",
            "source": payload.source,
            "content": payload.content,
            "sender": payload.sender,
            "source_id": payload.source_id or f"manual-{int(time.time())}",
            "metadata": payload.metadata,
            "timestamp": time.time()
        }
        
        # Push to the list that Agent monitors
        # Use key: deepflow:signals:pending
        redis.rpush("deepflow:signals:pending", json.dumps(signal))
        logger.info(f"Pushed signal to queue: {signal['source_id']}")
        
    except Exception as e:
        logger.error(f"Failed to push signal to Redis: {e}")
        # In a real app, we might want to retry or store in DLQ

@router.post("/simulate")
async def simulate_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """
    Simulate an incoming webhook (e.g., from Slack).
    
    This endpoint is used for testing and demo purposes to inject
    signals into the system manually.
    """
    # Use background task to avoid blocking the API response
    background_tasks.add_task(push_to_queue, payload)
    
    return {"status": "accepted", "message": "Signal received and queued for processing"}
