"""Time-series trend analysis (e.g. week-over-week)."""
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Any


def week_over_week_counts(rows: list[dict], date_key: str = "created_at") -> list[dict[str, Any]]:
    """Aggregate counts by week for trend view."""
    by_week: dict[str, int] = defaultdict(int)
    for r in rows:
        raw = r.get(date_key)
        if not raw:
            continue
        try:
            if isinstance(raw, str):
                dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            else:
                dt = raw
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            # Week start (Monday)
            start = dt - timedelta(days=dt.weekday())
            key = start.strftime("%Y-%m-%d")
            by_week[key] += 1
        except Exception:
            continue
    return [{"week": k, "count": v} for k, v in sorted(by_week.items())]
