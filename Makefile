# Town Hall Insights MCP Demo — local development (no Docker)
# Prerequisites: Python 3.11+, uv (https://docs.astral.sh/uv/)
# Copy .env.example to .env and fill in your keys.

.PHONY: help install install-api install-mcp install-agent run-api run-mcp run-agent run-all env-check

# Load .env into the environment for run targets (optional; apps also use python-dotenv from repo root)
RUN_ENV = set -a && [ -f .env ] && . ./.env && set +a

help:
	@echo "Town Hall Insights MCP Demo — local targets"
	@echo ""
	@echo "  make install       Install dependencies for all services (insights_api, mcp_server, agent)"
	@echo "  make install-api   Install insights_api deps only"
	@echo "  make install-mcp   Install mcp_server deps only"
	@echo "  make install-agent Install agent deps only"
	@echo ""
	@echo "  make run-api       Run Insights API on http://localhost:8001"
	@echo "  make run-mcp       Run MCP server on http://localhost:8002 (requires API running)"
	@echo "  make run-agent     Run agent (requires API + MCP running)"
	@echo "  make run-all       Start API and MCP in background, then run agent in foreground"
	@echo ""
	@echo "  make env-check     Verify .env exists and required vars are set"
	@echo ""
	@echo "Run API and MCP in separate terminals, then run the agent in a third (or use make run-all)."

install: install-api install-mcp install-agent

install-api:
	cd insights_api && uv sync

install-mcp:
	cd mcp_server && uv sync

install-agent:
	cd agent && uv sync

# Insights API — port 8001
run-api: #uv run uvicorn main:app --port 8001
	$(RUN_ENV) && cd insights_api && uv run uvicorn main:app --host 0.0.0.0 --port 8001

# MCP server — port 8002 (INSIGHTS_API_URL should be http://localhost:8001 in .env)
run-mcp:
	$(RUN_ENV) && cd mcp_server && uv run python server.py

# Agent — connects to MCP at MCP_SERVER_URL (http://localhost:8002/mcp in .env)
run-agent:
	$(RUN_ENV) && cd agent && uv run python agent.py

# Start API and MCP in background, then run agent in foreground (one terminal)
run-all:
	bash -c '$(RUN_ENV) && \
		(cd insights_api && uv run uvicorn main:app --host 0.0.0.0 --port 8001) & \
		(cd mcp_server && uv run python server.py) & \
		sleep 3 && (cd agent && uv run python agent.py)'

env-check:
	@[ -f .env ] || (echo "Missing .env — copy .env.example to .env and set OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY" && exit 1)
	@echo ".env found"
