"""MCP tool: get_anomalies — calls Insights API /anomalies."""
import os
import httpx


def get_insights_base_url() -> str:
    return os.environ.get("INSIGHTS_API_URL", "http://localhost:8001").rstrip("/")


def get_anomalies(source: str = "chatkit_thread_items", period: str = "this_week") -> str:
    """
    Check for anomalies in conversation or feedback volume (e.g. unusual spikes).
    source: 'feedback' for feedback table, 'chatkit_thread_items' for conversation thread volume.
    Use when the user asks if anything unusual happened, spikes, or outliers.
    """
    url = f"{get_insights_base_url()}/anomalies"
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(url, params={"source": source, "period": period})
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        return f"Error calling Insights API: {e}"
    items = data.get("anomalies", [])
    lines = [f"Period: {data.get('period', period)}. Source: {data.get('source', source)}."]
    for a in items:
        metric = a.get("metric", "?")
        value = a.get("value", "?")
        is_anomaly = a.get("is_anomaly", False)
        details = a.get("details", {})
        msg = details.get("message", details.get("error", str(details)))
        lines.append(f"- {metric}: {value} (anomaly={is_anomaly}). {msg}")
    return "\n".join(lines)
