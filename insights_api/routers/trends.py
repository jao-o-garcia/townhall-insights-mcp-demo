"""Conversation summary and trend endpoints."""
from collections import defaultdict
from fastapi import APIRouter, Query
from db import fetch_chatkit_thread_items
from models import ConversationSummaryResponse

router = APIRouter(prefix="/trends", tags=["trends"])


def _days_for_period(period: str) -> int | None:
    if period in ("this_week", "this week"):
        return 7
    if period in ("this_month", "this month"):
        return 30
    if period in ("this_quarter", "this quarter"):
        return 90
    return None


@router.get("/conversation_summary", response_model=ConversationSummaryResponse)
def get_conversation_summary(period: str = Query("this_week", description="this_week | this_month | this_quarter")):
    """Return conversation volume summary (threads, messages, avg)."""
    since_days = _days_for_period(period.strip().lower())
    r = fetch_chatkit_thread_items(limit=10000, since_days=since_days)
    rows = r.data or []
    by_thread: dict[str, int] = defaultdict(int)
    for row in rows:
        tid = row.get("thread_id") or "unknown"
        by_thread[tid] += 1
    total_threads = len(by_thread)
    total_messages = len(rows)
    avg = total_messages / total_threads if total_threads else 0
    summary = (
        f"In {period}, there were {total_threads} threads and {total_messages} messages, "
        f"averaging {avg:.1f} messages per thread."
    )
    return ConversationSummaryResponse(
        period=period,
        total_threads=total_threads,
        total_messages=total_messages,
        avg_messages_per_thread=round(avg, 2),
        summary=summary,
    )
