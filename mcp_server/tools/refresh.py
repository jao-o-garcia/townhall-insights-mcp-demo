"""MCP tool: refresh_insights — triggers on-demand recalculation (Insights API /refresh)."""
import os
import httpx


def get_insights_base_url() -> str:
    return os.environ.get("INSIGHTS_API_URL", "http://localhost:8001").rstrip("/")


def refresh_insights() -> str:
    """
    Trigger an on-demand refresh of cached insights. Call when the user wants to ensure
    the latest data is reflected in subsequent insight queries.
    """
    url = f"{get_insights_base_url()}/refresh"
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(url)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        return f"Error calling Insights API: {e}"
    return data.get("message", str(data))
