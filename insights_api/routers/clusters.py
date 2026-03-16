"""Topic clustering endpoint."""
from fastapi import APIRouter, Query
from insights_api.db import fetch_feedback
from insights_api.ml import get_topic_clusters
from insights_api.models import ClustersResponse, TopicClusterItem

router = APIRouter(prefix="/clusters", tags=["clusters"])


def _days_for_period(period: str) -> int | None:
    if period in ("this_week", "this week"):
        return 7
    if period in ("this_month", "this month"):
        return 30
    if period in ("this_quarter", "this quarter"):
        return 90
    return None


@router.get("", response_model=ClustersResponse)
def get_clusters(period: str = Query("this_month", description="this_week | this_month | this_quarter")):
    """Return topic clusters from feedback (topic + summary)."""
    since_days = _days_for_period(period.strip().lower())
    r = fetch_feedback(limit=2000, since_days=since_days)
    rows = r.data or []
    topics = [x.get("topic") for x in rows]
    summaries = [x.get("summary") or x.get("topic") or "" for x in rows]
    clusters = get_topic_clusters(summaries, topics=topics, top_k=10)
    return ClustersResponse(
        period=period,
        clusters=[TopicClusterItem(**c) for c in clusters],
        total_docs=len(rows),
    )
