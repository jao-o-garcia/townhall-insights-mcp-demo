"""MCP tool: get_conversation_summary — calls Insights API /trends/conversation_summary."""
import os
import httpx


def get_insights_base_url() -> str:
    return os.environ.get("INSIGHTS_API_URL", "http://localhost:8001").rstrip("/")


def get_conversation_summary(period: str = "this_week") -> str:
    """
    Get a summary of conversation volume: number of threads, messages, and average messages per thread.
    Use when the user asks about engagement, conversation volume, or session stats.
    """
    url = f"{get_insights_base_url()}/trends/conversation_summary"
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(url, params={"period": period})
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        return f"Error calling Insights API: {e}"
    return data.get("summary", str(data))
