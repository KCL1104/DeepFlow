"""
User API Router

Endpoints for user-related operations including Telegram binding status.
"""

import redis
from fastapi import APIRouter, HTTPException

from ..config import get_settings
from ..deps import CurrentUser

router = APIRouter(prefix="/user", tags=["user"])


def get_redis_client() -> redis.Redis:
    """Get Redis client."""
    settings = get_settings()
    return redis.from_url(settings.redis_url, decode_responses=True)


@router.get("/telegram-binding")
async def get_telegram_binding(user: CurrentUser):
    """
    Check if current user has linked their Telegram account.
    
    Returns:
        - is_linked: Whether user has linked Telegram
        - telegram_id: The linked Telegram ID (if any)
    """
    try:
        redis_client = get_redis_client()
        
        # Check reverse mapping: DeepFlow user ID -> Telegram ID
        binding_key = f"deepflow_binding:{user['id']}"
        telegram_id = redis_client.get(binding_key)
        
        if telegram_id:
            return {
                "is_linked": True,
                "telegram_id": int(telegram_id),
            }
        else:
            return {
                "is_linked": False,
                "telegram_id": None,
            }
    except Exception as e:
        # If Redis fails, assume not linked
        return {
            "is_linked": False,
            "telegram_id": None,
            "error": str(e)
        }


@router.delete("/telegram-binding")
async def unlink_telegram(user: CurrentUser):
    """
    Unlink Telegram account from current user.
    """
    try:
        redis_client = get_redis_client()
        
        # Get the telegram ID first
        binding_key = f"deepflow_binding:{user['id']}"
        telegram_id = redis_client.get(binding_key)
        
        if not telegram_id:
            raise HTTPException(status_code=404, detail="No Telegram account linked")
        
        # Delete both mappings
        redis_client.delete(binding_key)
        redis_client.delete(f"telegram_binding:{telegram_id}")
        
        return {"message": "Telegram account unlinked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
