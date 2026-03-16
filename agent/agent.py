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


async def main() -> None:
    try:
        from agents.mcp import MCPServerStreamableHttp
    except ImportError:
        # Fallback: run without MCP if SDK version doesn't expose it
        agent = Agent(
            name="Town Hall Assistant",
            instructions=(
                "You are a Town Hall assistant for civic engagement. "
                "You help answer questions about resident feedback and community insights. "
                "MCP insights tools are not available in this session; describe what you would have queried."
            ),
        )
        await run_demo_loop(agent)
        return

    async with MCPServerStreamableHttp(
        name="Insights MCP",
        params={"url": MCP_URL, "timeout": 15},
        cache_tools_list=True,
    ) as server:
        agent = Agent(
            name="Town Hall Assistant",
            instructions=(
                "You are a Town Hall assistant for civic engagement. You help residents and staff "
                "understand feedback and community insights. Use the Insights MCP tools when the user asks about:\n"
                "- Common concerns or topics (get_topic_clusters)\n"
                "- Sentiment or tone of feedback (get_sentiment_trends)\n"
                "- Unusual activity or spikes (get_anomalies)\n"
                "- Conversation volume or engagement (get_conversation_summary)\n"
                "Answer in a clear, concise way and cite the data you get from the tools."
            ),
            mcp_servers=[server],
        )
        await run_demo_loop(agent)


if __name__ == "__main__":
    asyncio.run(main())
