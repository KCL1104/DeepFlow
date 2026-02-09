"""Shared API error mapping utilities."""

from fastapi import HTTPException, status


def raise_db_http_exception(exc: Exception, operation: str) -> None:
    """Convert internal DB/config exceptions into stable HTTP responses."""
    message = str(exc)

    if "SUPABASE_SERVICE_ROLE_KEY is not configured" in message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backend configuration error: SUPABASE_SERVICE_ROLE_KEY is not configured.",
        ) from exc

    if "SUPABASE_URL is not configured" in message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backend configuration error: SUPABASE_URL is not configured.",
        ) from exc

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Database operation failed while {operation}.",
    ) from exc
