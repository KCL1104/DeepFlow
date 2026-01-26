"""
Conversation Memory Module

Provides Redis-based conversation memory for the DeepFlow Agent.
Stores recent messages and allows the agent to maintain context.
"""

import json
import logging
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def get_redis_client():
    """Get Upstash Redis client."""
    from upstash_redis import Redis
    return Redis(
        url=os.getenv("UPSTASH_REDIS_REST_URL"),
        token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
    )


class ConversationMemory:
    """
    Simple Redis-based conversation memory.
    
    Stores the last N messages for each user, allowing the agent
    to have context about recent interactions.
    """
    
    def __init__(self, max_messages: int = 10):
        """
        Initialize conversation memory.
        
        Args:
            max_messages: Maximum number of messages to retain per user
        """
        self.redis = get_redis_client()
        self.max_messages = max_messages
    
    def _get_key(self, user_id: str) -> str:
        """Get Redis key for user's conversation history."""
        return f"user:{user_id}:conversation_history"
    
    def add_message(
        self,
        user_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None
    ):
        """
        Add a message to the conversation history.
        
        Args:
            user_id: User's unique identifier
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata (source, urgency, etc.)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        key = self._get_key(user_id)
        self.redis.rpush(key, json.dumps(message))
        
        # Trim to max messages
        self.redis.ltrim(key, -self.max_messages, -1)
        
        logger.debug(f"Added message to {user_id}'s history: {role}")
    
    def get_history(self, user_id: str, limit: Optional[int] = None) -> list:
        """
        Get conversation history for a user.
        
        Args:
            user_id: User's unique identifier
            limit: Optional limit on number of messages to return
        
        Returns:
            List of message dictionaries
        """
        key = self._get_key(user_id)
        limit = limit or self.max_messages
        
        raw_messages = self.redis.lrange(key, -limit, -1)
        
        messages = []
        for raw in raw_messages:
            try:
                messages.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        
        return messages
    
    def get_formatted_history(self, user_id: str, limit: int = 5) -> str:
        """
        Get formatted conversation history as a string.
        
        Suitable for including in agent prompts.
        
        Args:
            user_id: User's unique identifier
            limit: Number of recent messages to include
        
        Returns:
            Formatted string of recent messages
        """
        history = self.get_history(user_id, limit)
        
        if not history:
            return "No recent conversation history."
        
        formatted = []
        for msg in history:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")[:200]  # Truncate long messages
            formatted.append(f"[{role}] {content}")
        
        return "\n".join(formatted)
    
    def clear_history(self, user_id: str):
        """Clear conversation history for a user."""
        key = self._get_key(user_id)
        self.redis.delete(key)
        logger.info(f"Cleared conversation history for {user_id}")
    
    def get_last_message(self, user_id: str) -> Optional[dict]:
        """Get the last message in the conversation."""
        key = self._get_key(user_id)
        raw = self.redis.lindex(key, -1)
        
        if raw:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return None
        return None
    
    def get_context_summary(self, user_id: str) -> dict:
        """
        Get a summary of the conversation context.
        
        Returns:
            Dict with context information
        """
        history = self.get_history(user_id)
        
        if not history:
            return {
                "message_count": 0,
                "has_context": False,
                "last_interaction": None
            }
        
        # Count messages by role
        role_counts = {}
        for msg in history:
            role = msg.get("role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # Get last interaction time
        last_msg = history[-1]
        last_time = last_msg.get("timestamp")
        
        return {
            "message_count": len(history),
            "has_context": True,
            "last_interaction": last_time,
            "role_distribution": role_counts
        }


# Singleton instance for easy access
_memory_instance: Optional[ConversationMemory] = None


def get_conversation_memory() -> ConversationMemory:
    """Get the singleton conversation memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = ConversationMemory()
    return _memory_instance
