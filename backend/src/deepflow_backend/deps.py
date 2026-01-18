"""
API Dependencies

Provides dependency injection for database clients and auth.
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Header, status

from .config import get_settings, Settings
from .db import get_redis_client, get_supabase_client, UserStateManager, TaskQueueManager


def get_settings_dep() -> Settings:
    """Dependency for settings."""
    return get_settings()


def get_state_manager() -> UserStateManager:
    """Dependency for user state manager."""
    return UserStateManager(get_redis_client())


def get_queue_manager() -> TaskQueueManager:
    """Dependency for task queue manager."""
    return TaskQueueManager(get_redis_client())


async def get_current_user(
    authorization: Annotated[Optional[str], Header()] = None,
) -> dict:
    """
    Validate Supabase JWT and return user info.
    
    In production, this should properly verify the JWT.
    For now, we extract the user_id from the token.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    token = authorization.replace("Bearer ", "")

    try:
        # Use Supabase to verify the token
        supabase = get_supabase_client()
        user = supabase.auth.get_user(token)
        
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return {
            "id": user.user.id,
            "email": user.user.email,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
        )


# Type aliases for dependency injection
CurrentUser = Annotated[dict, Depends(get_current_user)]
StateManager = Annotated[UserStateManager, Depends(get_state_manager)]
QueueManager = Annotated[TaskQueueManager, Depends(get_queue_manager)]
