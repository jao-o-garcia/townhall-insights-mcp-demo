"""Supabase / PostgreSQL connection for Insights API."""
import os
from supabase import create_client, Client

_supabase: Client | None = None


def get_supabase() -> Client:
    """Return a Supabase client (singleton)."""
    global _supabase
    if _supabase is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        _supabase = create_client(url, key)
    return _supabase


def fetch_feedback(limit: int = 1000, since_days: int | None = None):
    """Fetch feedback rows for insights. Optionally filter by created_at."""
    sb = get_supabase()
    q = sb.table("feedback").select("id,topic,summary,sentiment,created_at,session_id")
    if since_days is not None:
        from datetime import datetime, timedelta, timezone
        since = (datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat()
        q = q.gte("created_at", since)
    q = q.order("created_at", desc=True).limit(limit)
    return q.execute()


def fetch_chatkit_thread_items(limit: int = 5000, since_days: int | None = None):
    """Fetch chatkit_thread_items for conversation analytics."""
    sb = get_supabase()
    q = sb.table("chatkit_thread_items").select("id,thread_id,item_type,created_at,item_json")
    if since_days is not None:
        from datetime import datetime, timedelta, timezone
        since = (datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat()
        q = q.gte("created_at", since)
    q = q.order("created_at", desc=True).limit(limit)
    return q.execute()
