"""
Town Hall Agent — connects to Insights MCP server and uses run_demo_loop for interactive chat.
Based on the digital-town-hall agent scaffold (OpenAI Agents SDK).
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from agents import Agent, run_demo_loop

# MCP server URL (Streamable HTTP); must be running when agent starts
MCP_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8002/mcp")

AGENT_INSTRUCTIONS_WITH_MCP = (
    "You are a Town Hall assistant for civic engagement. You help residents and staff "
    "understand feedback and community insights. Use the Insights MCP tools when the user asks about:\n"
    "- Common concerns or topics (get_topic_clusters)\n"
    "- Sentiment or tone of feedback (get_sentiment_trends)\n"
    "- Unusual activity or spikes (get_anomalies)\n"
    "- Conversation volume or engagement (get_conversation_summary)\n"
    "Answer in a clear, concise way and cite the data you get from the tools."
)

AGENT_INSTRUCTIONS_FALLBACK = (
    "You are a Town Hall assistant for civic engagement. "
    "You help answer questions about resident feedback and community insights. "
    "The Insights MCP tools are currently unavailable (server is offline). "
    "Let the user know you cannot fetch live data, and describe what you would have queried."
)


async def run_fallback_agent(reason: str) -> None:
    print(f"[Warning] {reason} — running without MCP tools.\n")
    agent = Agent(
        name="Town Hall Assistant",
        instructions=AGENT_INSTRUCTIONS_FALLBACK,
    )
    await run_demo_loop(agent)


async def main() -> None:
    try:
        from agents.mcp import MCPServerStreamableHttp
    except ImportError as e:
        await run_fallback_agent(f"MCP SDK not available: {e}")
        return

    try:
        async with MCPServerStreamableHttp(
            name="Insights MCP",
            params={"url": MCP_URL, "timeout": 15},
            cache_tools_list=True,
        ) as server:
            agent = Agent(
                name="Town Hall Assistant",
                instructions=AGENT_INSTRUCTIONS_WITH_MCP,
                mcp_servers=[server],
            )
            await run_demo_loop(agent)
    except Exception as e:
        await run_fallback_agent(f"Could not connect to MCP server at {MCP_URL}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
