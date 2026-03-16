"""MCP tool: get_sentiment_trends — calls Insights API /sentiment/trends."""
import os
import httpx


def get_insights_base_url() -> str:
    return os.environ.get("INSIGHTS_API_URL", "http://localhost:8001").rstrip("/")


def get_sentiment_trends(period: str = "this_week") -> str:
    """
    Get sentiment distribution (positive / negative / neutral) of feedback for a time period.
    Use when the user asks about overall tone, mood, or sentiment of resident feedback.
    """
    url = f"{get_insights_base_url()}/sentiment/trends"
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(url, params={"period": period})
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        return f"Error calling Insights API: {e}"
    buckets = data.get("buckets", [])
    total = data.get("total", 0)
    lines = [f"Period: {data.get('period', period)}. Total feedback: {total}."]
    for b in buckets:
        label = b.get("label", "?")
        count = b.get("count", 0)
        pct = b.get("pct", 0)
        lines.append(f"- {label}: {count} ({pct}%)")
    return "\n".join(lines)
