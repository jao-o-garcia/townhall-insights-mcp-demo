"""Sentiment trends endpoint."""
from fastapi import APIRouter, Query
from db import fetch_feedback
from ml import aggregate_sentiment
from models import SentimentTrendsResponse, SentimentBucket

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


def _days_for_period(period: str) -> int | None:
    if period in ("this_week", "this week"):
        return 7
    if period in ("this_month", "this month"):
        return 30
    if period in ("this_quarter", "this quarter"):
        return 90
    return None


@router.get("/trends", response_model=SentimentTrendsResponse)
def get_sentiment_trends(period: str = Query("this_week", description="this_week | this_month | this_quarter")):
    """Return sentiment distribution from feedback (uses pre-classified sentiment)."""
    since_days = _days_for_period(period.strip().lower())
    r = fetch_feedback(limit=5000, since_days=since_days)
    rows = r.data or []
    labels = [x.get("sentiment") or "neutral" for x in rows]
    buckets = aggregate_sentiment(labels)
    total = len(rows)
    return SentimentTrendsResponse(
        period=period,
        buckets=[SentimentBucket(**b) for b in buckets],
        total=total,
    )
