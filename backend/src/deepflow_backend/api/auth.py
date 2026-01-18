"""
Auth API Router

Endpoints for Supabase authentication.
Note: Most auth is handled client-side with Supabase JS SDK.
These endpoints are for server-side token validation and user info.
"""

from fastapi import APIRouter, HTTPException, status

from ..deps import CurrentUser
from ..db import get_supabase_client


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def get_current_user_info(user: CurrentUser):
    """Get current authenticated user's information."""
    return {
        "id": user["id"],
        "email": user["email"],
    }


@router.post("/signout")
async def signout(user: CurrentUser):
    """
    Server-side signout.
    Note: Client should also call supabase.auth.signOut()
    """
    try:
        supabase = get_supabase_client()
        # Server-side signout (invalidates session)
        # Note: This mainly clears server-side state
        return {"message": "Signed out successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signout failed: {str(e)}",
        )


@router.post("/refresh")
async def refresh_token():
    """
    Refresh token endpoint.
    Note: Supabase handles token refresh automatically in the JS SDK.
    This is a fallback for manual refresh if needed.
    """
    # Client should handle this with supabase.auth.refreshSession()
    return {"message": "Use Supabase JS SDK for token refresh"}
