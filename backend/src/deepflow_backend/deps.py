"""
API Dependencies

Provides dependency injection for database clients and auth.
"""

from functools import lru_cache
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from .config import get_settings, Settings
from .db import get_redis_client, UserStateManager, TaskQueueManager


class CurrentUser(BaseModel):
    id: str
    email: str
    is_active: bool = True
    is_superuser: bool = False


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


@lru_cache
def get_supabase_client():
    """Get cached Supabase client."""
    settings = get_settings()
    if not settings.is_configured:
        # If not configured, we might be in dev mode without auth,
        # but get_current_user should handle that.
        # This will raise if verify_jwt tries to call it.
        return None
    
    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def get_state_manager() -> UserStateManager:
    """Dependency for user state manager."""
    return UserStateManager(get_redis_client())


def get_queue_manager() -> TaskQueueManager:
    """Dependency for task queue manager."""
    return TaskQueueManager(get_redis_client())


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)]
) -> CurrentUser:
    """
    Validate the Supabase JWT and return the current user.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 1. Dev Auth Bypass (Only in Development)
    if settings.app_env == "development" and token.startswith("dev-user-"):
        # Allow dev token for testing without Supabase
        user_id = token.replace("dev-user-", "")
        return CurrentUser(
            id=user_id,
            email=f"dev{user_id}@deepflow.ai",
            is_active=True,
            is_superuser=False
        )

    # 2. Real Supabase Auth
    try:
        supabase = get_supabase_client()
        if not supabase:
             raise ValueError("Supabase not configured")

        user_response = supabase.auth.get_user(token)
        user = user_response.user
        
        if not user:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return CurrentUser(
            id=user.id,
            email=user.email or "",
            is_active=True,
            is_superuser=False
        )
        
    except Exception as e:
        # print(f"Auth Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Type aliases for dependency injection
UserDep = Annotated[CurrentUser, Depends(get_current_user)]
StateManager = Annotated[UserStateManager, Depends(get_state_manager)]
QueueManager = Annotated[TaskQueueManager, Depends(get_queue_manager)]
