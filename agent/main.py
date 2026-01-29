"""
DeepFlow Agent - Sentinel Worker (Unified Architecture)

Main entry point for the background agent process.
Polls Redis for incoming signals and processes them using the ReAct Agent.
This allows the agent to take actions (like notification) based on urgency.
"""

import asyncio
import json
import logging
from typing import Optional

from upstash_redis import Redis

from deepflow_agent.config import get_settings
from deepflow_agent.agents import process_message, process_message_sync
from deepflow_agent.models import TaskSource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("deepflow-agent")

async def process_signal(redis: Redis, signal_data: str):
    """
    Process a single signal from the queue using ReAct Agent.
    """
    try:
        if isinstance(signal_data, str):
            try:
                data = json.loads(signal_data)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode signal JSON: {signal_data[:100]}...")
                return
        else:
            data = signal_data

        source_id = data.get("source_id", "unknown")
        source_str = data.get("source", "manual")
        content = data.get("content", "")
        sender = data.get("sender", "Unknown")
        metadata = data.get("metadata", {})
        
        logger.info(f"⚡ Processing signal from {source_str}: {source_id}")

        # 1. Determine Target User
        # For MVP, we look for 'user_id' in metadata, or use a default if single-user mode.
        # Ideally, we should have a mapping (e.g., email -> user_id).
        # Here we default to "default_user" if not provided, assuming the user will link this ID.
        user_id = metadata.get("user_id", "default_user")
        
        # 2. Get User State
        # We need to know if the user is in FLOW to make the right decision.
        state_key = f"user:{user_id}:state"
        user_state = redis.get(state_key) or "IDLE"

        logger.info(f"   Context: User={user_id}, State={user_state}")

        # 3. Construct Input for Agent
        # We frame the signal as a message to the agent.
        # "System Alert: [Source] Sender says: Content"
        agent_input = (
            f"INCOMING SIGNAL detected from {source_str.upper()}.\n"
            f"Sender: {sender}\n"
            f"Content: {content}\n\n"
            f"Determine urgency and take action (notify or queue)."
        )

        # 4. Invoke ReAct Agent
        # This will auto-execute tools (add_to_queue, send_telegram_notification)
        result = await process_message(
            user_id=user_id,
            user_state=user_state,
            message_content=agent_input,
            sender="System_Signal_Ingestion",
            source=source_str,
            source_id=str(source_id),
            verbose=True # Helpful for debugging logs
        )
        
        logger.info(f"🤖 Agent Action Complete.")
        if result.get("tool_calls"):
            logger.info(f"   Tools used: {len(result['tool_calls'])}")
        
    except Exception as e:
        logger.error(f"Error processing signal: {e}", exc_info=True)

async def worker_loop():
    """
    Main worker loop.
    """
    settings = get_settings()
    
    # Check Config
    if not settings.is_redis_configured:
        logger.error("❌ Redis is not configured. Set UPSTASH_REDIS_REST_URL/TOKEN.")
        return
    if not settings.is_llm_configured:
        logger.error("❌ LLM is not configured. Set OPENAI_API_KEY.")
        return

    logger.info("🛡️  DeepFlow Sentinel Agent (Unified Brain) Starting...")
    
    try:
        redis = Redis(
            url=settings.upstash_redis_rest_url,
            token=settings.upstash_redis_rest_token
        )
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return

    queue_key = "deepflow:signals:pending"
    logger.info(f"👀 Watching queue: {queue_key}")
    
    while True:
        try:
            # Poll Redis (LPOP)
            item = redis.lpop(queue_key)
            
            if item:
                await process_signal(redis, item)
            else:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Worker loop encountered error: {e}")
            await asyncio.sleep(5)

def main():
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("👋 Agent shutting down...")

if __name__ == "__main__":
    main()
