"""
Supabase Client Module

Provides async Supabase client for database operations.
"""

from functools import lru_cache

from supabase import create_client, Client

from ..config import get_settings


@lru_cache
def get_supabase_client() -> Client:
    """Get cached Supabase client."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_anon_key)


@lru_cache
def get_supabase_admin_client() -> Client:
    """Get cached Supabase admin client with service role key."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
