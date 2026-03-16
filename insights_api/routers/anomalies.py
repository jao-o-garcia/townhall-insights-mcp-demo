"""Anomaly detection endpoint."""
from collections import defaultdict
from fastapi import APIRouter, Query
from insights_api.db import fetch_feedback, fetch_chatkit_thread_items
from insights_api.ml import detect_anomalies
from insights_api.models import AnomaliesResponse, AnomalyItem

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


def _days_for_period(period: str) -> int | None:
    if period in ("this_week", "this week"):
        return 7
    if period in ("this_month", "this month"):
        return 30
    if period in ("this_quarter", "this quarter"):
        return 90
    return None


@router.get("", response_model=AnomaliesResponse)
def get_anomalies(
    source: str = Query("feedback", description="feedback | chatkit_thread_items"),
    period: str = Query("this_week", description="this_week | this_month | this_quarter"),
):
    """Return detected anomalies (volume/spike) for the given source."""
    since_days = _days_for_period(period.strip().lower())
    anomalies: list[dict] = []

    if source == "feedback":
        r = fetch_feedback(limit=5000, since_days=since_days)
        rows = r.data or []
        if len(rows) >= 3:
            # Daily counts for anomaly detection
            from datetime import datetime, timezone, timedelta
            by_day: dict[str, int] = defaultdict(int)
            for row in rows:
                raw = row.get("created_at")
                if not raw:
                    continue
                try:
                    dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    key = dt.strftime("%Y-%m-%d")
                    by_day[key] += 1
                except Exception:
                    continue
            daily_counts = [by_day[k] for k in sorted(by_day)]
            if daily_counts:
                detected = detect_anomalies(daily_counts, metric_name="feedback_per_day")
                for d in detected:
                    d["source"] = "feedback"
                    anomalies.append(d)
        if not anomalies:
            anomalies.append({
                "source": "feedback",
                "metric": "volume",
                "value": len(rows),
                "expected_range": "normal",
                "is_anomaly": False,
                "details": {"message": "No significant spikes detected."},
            })

    elif source == "chatkit_thread_items":
        r = fetch_chatkit_thread_items(limit=5000, since_days=since_days)
        rows = r.data or []
        by_day: dict[str, int] = defaultdict(int)
        for row in rows:
            raw = row.get("created_at")
            if not raw:
                continue
            try:
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                key = dt.strftime("%Y-%m-%d")
                by_day[key] += 1
            except Exception:
                continue
        daily_counts = [by_day[k] for k in sorted(by_day)]
        if len(daily_counts) >= 3:
            detected = detect_anomalies(daily_counts, metric_name="messages_per_day")
            for d in detected:
                d["source"] = "chatkit_thread_items"
                anomalies.append(d)
        if not anomalies:
            anomalies.append({
                "source": "chatkit_thread_items",
                "metric": "volume",
                "value": len(rows),
                "expected_range": "normal",
                "is_anomaly": False,
                "details": {"message": "Thread volume appears normal."},
            })

    else:
        anomalies.append({
            "source": source,
            "metric": "unknown",
            "value": 0,
            "expected_range": "N/A",
            "is_anomaly": False,
            "details": {"error": "Unknown source."},
        })

    return AnomaliesResponse(period=period, source=source, anomalies=[AnomalyItem(**a) for a in anomalies])
