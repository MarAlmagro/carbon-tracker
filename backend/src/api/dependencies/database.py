"""Supabase client dependency."""

from supabase import Client

from infrastructure.config.supabase import get_supabase_client


def get_supabase() -> Client:
    """Get Supabase client.

    Dependency for injecting Supabase client into route handlers.

    Returns:
        Client: Supabase client instance

    Example:
        @router.get("/")
        async def handler(client: Client = Depends(get_supabase)):
            result = client.table("items").select("*").execute()
    """
    return get_supabase_client()  # type: ignore[no-any-return]
