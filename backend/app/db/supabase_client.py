"""
Supabase client wrapper.

Deliberately fails soft: if SUPABASE_URL / SUPABASE_KEY are not set (e.g. during
early scaffold development before the DB is provisioned - see Phase 9), the app
still boots and API routes fall back to in-memory mock data instead of crashing.
"""
from __future__ import annotations

from typing import Optional

from app.core.config import settings

_client = None


def get_supabase_client():
    """Returns a cached Supabase client, or None if not configured."""
    global _client
    if not settings.supabase_configured:
        return None
    if _client is None:
        from supabase import create_client  # imported lazily so the package
        # is only required once real credentials exist.
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _client


def is_db_connected() -> bool:
    return get_supabase_client() is not None
