"""MCP tool: get_topic_clusters — calls Insights API /clusters."""
import os
import httpx


def get_insights_base_url() -> str:
    return os.environ.get("INSIGHTS_API_URL", "http://localhost:8001").rstrip("/")


def get_topic_clusters(period: str = "this_month") -> str:
    """
    Get the main topic clusters from resident feedback for a given time period.
    Use this when the user asks about common concerns, main themes, or what residents are talking about.
    """
    url = f"{get_insights_base_url()}/clusters"
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(url, params={"period": period})
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        return f"Error calling Insights API: {e}"
    clusters = data.get("clusters", [])
    total = data.get("total_docs", 0)
    lines = [f"Period: {data.get('period', period)}. Total feedback items: {total}."]
    for i, c in enumerate(clusters[:10], 1):
        topic = c.get("topic", "?")
        count = c.get("count", 0)
        samples = c.get("representative_summaries", [])[:2]
        lines.append(f"{i}. {topic} ({count} items)")
        for s in samples:
            if s:
                lines.append(f"   - {s[:120]}{'...' if len(s) > 120 else ''}")
    return "\n".join(lines)
