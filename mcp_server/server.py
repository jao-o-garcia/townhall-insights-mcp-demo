"""Insights MCP Server (FastMCP + HTTP). Exposes Insights API as MCP tools."""
import os
from dotenv import load_dotenv
load_dotenv()

from fastmcp import FastMCP

from tools.topic_clusters import get_topic_clusters
from tools.sentiment_trends import get_sentiment_trends
from tools.anomalies import get_anomalies
from tools.conversation_summary import get_conversation_summary
from tools.refresh import refresh_insights

mcp = FastMCP("Town Hall Insights", description="Insights from civic feedback and conversations via the Insights API")


@mcp.tool(name="get_topic_clusters")
def get_topic_clusters_tool(period: str = "this_month") -> str:
    """
    Get the main topic clusters from resident feedback for a given time period.
    Use when the user asks about common concerns, main themes, or what residents are talking about.
    period: one of this_week, this_month, this_quarter.
    """
    return get_topic_clusters(period=period)


@mcp.tool(name="get_sentiment_trends")
def get_sentiment_trends_tool(period: str = "this_week") -> str:
    """
    Get sentiment distribution (positive / negative / neutral) of feedback for a time period.
    Use when the user asks about overall tone, mood, or sentiment of resident feedback.
    period: one of this_week, this_month, this_quarter.
    """
    return get_sentiment_trends(period=period)


@mcp.tool(name="get_anomalies")
def get_anomalies_tool(source: str = "chatkit_thread_items", period: str = "this_week") -> str:
    """
    Check for anomalies in conversation or feedback volume (e.g. unusual spikes).
    source: 'feedback' for feedback table, 'chatkit_thread_items' for conversation thread volume.
    period: one of this_week, this_month, this_quarter.
    """
    return get_anomalies(source=source, period=period)


@mcp.tool(name="get_conversation_summary")
def get_conversation_summary_tool(period: str = "this_week") -> str:
    """
    Get a summary of conversation volume: threads, messages, average messages per thread.
    Use when the user asks about engagement or conversation volume.
    period: one of this_week, this_month, this_quarter.
    """
    return get_conversation_summary(period=period)


@mcp.tool(name="refresh_insights")
def refresh_insights_tool() -> str:
    """
    Trigger an on-demand refresh of cached insights so subsequent queries use the latest data.
    """
    return refresh_insights()


if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT", 8002))
    mcp.run(transport="http", host="127.0.0.1", port=port)
