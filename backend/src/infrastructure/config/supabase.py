"""Supabase client configuration."""

from functools import lru_cache

from supabase import Client, create_client

from .settings import get_settings


@lru_cache
def get_supabase_client() -> Client:
    """Get cached Supabase client instance.

    Returns:
        Configured Supabase client
    """
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_publishable_key)
