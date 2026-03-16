# townhall-insights-mcp-demo

A showcase of how to connect an AI agent to a general **Insights API** via an **MCP (Model Context Protocol) server**. Built on top of the [Digital Town Hall](https://github.com/Amigda-Labs/digital-town-hall) project — a civic engagement platform where residents submit feedback and report incidents.

This demo illustrates the full insights pipeline:

> Agent → MCP Client → MCP Server → Insights API → PostgreSQL (Supabase)

---

## What this demonstrates

- How to expose a general Insights API as MCP tools
- How an AI agent (OpenAI Agents SDK) calls those tools naturally in conversation
- How to separate the insights computation layer from the agent layer via a clean API boundary
- Practical ML and analytics techniques applied to civic/community data

---

## Architecture

```
┌─────────────────────────────────────────┐
│              Agent Layer                │
│                                         │
│   Town Hall Agent (OpenAI Agents SDK)   │
│        │                                │
│   [ insights_tool ]  [ other tools ]    │
└────────────┬────────────────────────────┘
             │ MCP tool call
┌────────────▼────────────────────────────┐
│              MCP Layer                  │
│                                         │
│   Insights MCP Server (FastMCP + SSE)   │
│                                         │
│   Tools exposed:                        │
│   • get_topic_clusters                  │
│   • get_sentiment_trends                │
│   • get_anomalies                       │
│   • get_conversation_summary            │
│   • refresh_insights                    │
└────────────┬────────────────────────────┘
             │ HTTP
┌────────────▼────────────────────────────┐
│           Insights API Layer            │
│                                         │
│   FastAPI Insights Service (Python)     │
│   ├── Topic Clustering  (BERTopic)      │
│   ├── Sentiment Analysis (VADER)        │
│   ├── Anomaly Detection  (Isolation     │
│   │                       Forest)       │
│   └── Trend Analysis    (time-series)   │
│                    │                    │
│            Supabase / PostgreSQL        │
│            (Feedback + Incident tables) │
└─────────────────────────────────────────┘
```

---

## Repository structure

```
townhall-insights-mcp-demo/
│
├── agent/                        # Sample Town Hall Agent (demo/testing only)
│   ├── agent.py                  # Agent definition + tool registration
│   ├── tools/
│   │   └── insights_tool.py      # MCP-connected insights tool
│   └── requirements.txt
│
├── mcp_server/                   # Insights MCP Server
│   ├── server.py                 # FastMCP server entrypoint
│   ├── tools/
│   │   ├── topic_clusters.py
│   │   ├── sentiment_trends.py
│   │   ├── anomalies.py
│   │   └── conversation_summary.py
│   └── requirements.txt
│
├── insights_api/                 # General Insights API (FastAPI)
│   ├── main.py                   # FastAPI app entrypoint
│   ├── routers/
│   │   ├── clusters.py
│   │   ├── sentiment.py
│   │   ├── anomalies.py
│   │   └── trends.py
│   ├── models/
│   │   └── schemas.py            # Pydantic request/response models
│   ├── ml/
│   │   ├── topic_model.py        # BERTopic logic
│   │   ├── sentiment.py          # VADER / transformer sentiment
│   │   ├── anomaly.py            # Isolation Forest
│   │   └── trends.py             # Time-series trend analysis
│   ├── db.py                     # Supabase / SQLAlchemy connection
│   └── requirements.txt
│
├── docker-compose.yml            # Run all services together
├── .env.example
└── README.md
```

---

## ML techniques used

| Technique | Library | Applied to |
|---|---|---|
| Topic clustering | BERTopic / LDA | Feedback free-text — surfaces top community concerns |
| Sentiment analysis | VADER / distilbert | Feedback — tracks positive/negative tone over time |
| Anomaly detection | Isolation Forest | Incidents — flags unusual spikes by type or location |
| Trend analysis | statsmodels / LOESS | Both tables — shows how issues evolve week over week |

> Results are **pre-computed and cached** on a schedule. MCP tools query the cache, keeping latency low. A `refresh_insights` tool triggers on-demand recalculation.

---

## Quickstart

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (for install and run when not using Docker)
- Node.js 18+ (optional, for the agent demo UI)
- A Supabase project with `feedback` and `incident` tables
- OpenAI API key

### 1. Clone the repo

```bash
git clone https://github.com/your-username/townhall-insights-mcp-demo.git
cd townhall-insights-mcp-demo
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Fill in: OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY, INSIGHTS_API_URL
```

### 3. Run with Docker Compose

```bash
docker-compose up
```

This starts:
- `insights_api` on `http://localhost:8001`
- `mcp_server` on `http://localhost:8002`
- `agent` demo on `http://localhost:8000`

### 4. Run services individually (with uv)

Use [uv](https://docs.astral.sh/uv/) for dependency management and running. In each service directory, initialize the project and add dependencies from its `requirements.txt`, then run with `uv run`.

**Initialize and install (once per service):**

In each service directory, run `uv init` to create a `pyproject.toml`, then add dependencies with `uv add` (use the packages from that service’s `requirements.txt`). Example for the Insights API:

```bash
# Insights API
cd insights_api
uv init
uv add fastapi "uvicorn[standard]" supabase pydantic httpx python-dotenv scikit-learn vaderSentiment bertopic sentence-transformers statsmodels numpy pandas

# MCP server
cd ../mcp_server
uv init
uv add fastmcp httpx python-dotenv

# Agent
cd ../agent
uv init
uv add openai-agents python-dotenv
```

Alternatively, install from the existing `requirements.txt` with uv’s pip interface, then use `uv run` for execution:

```bash
cd insights_api && uv init && uv pip install -r requirements.txt
cd ../mcp_server && uv init && uv pip install -r requirements.txt
cd ../agent && uv init && uv pip install -r requirements.txt
```

**Run each service** (in separate terminals, from the repo root or the service directory):

```bash
# Insights API
cd insights_api && uv run uvicorn main:app --port 8001 --reload

# MCP server
cd mcp_server && uv run python server.py

# Agent
cd agent && uv run python agent.py
```

---

## Example interaction

```
User: What are the most common concerns raised by residents this month?

Agent → calls get_topic_clusters(period="this_month")
MCP Server → calls Insights API /clusters
Insights API → runs clustering on feedback.topic + feedback.summary

Agent: Based on this month's feedback, the top concerns are:
  1. Station facilities — locker availability, restroom conditions (Ginza Station)
  2. Public cleanliness — street and public space upkeep
  3. Safety and missing persons reports

User: What's the overall sentiment of feedback this week?

Agent → calls get_sentiment_trends(period="this_week")

Agent: This week's feedback skews negative (50%), with some neutral (25%)
  and positive (25%) submissions. The negative feedback is concentrated
  around cleanliness and safety concerns.

User: Is there anything unusual in the conversation volume this week?

Agent → calls get_anomalies(source="chatkit_thread_items", period="this_week")

Agent: Thread volume appears normal. No significant spikes detected.
  Average session length is consistent with prior weeks.
```

---

## Data schema

The Insights API queries the following tables from the Digital Town Hall Supabase instance:

```sql
-- Feedback and incident reports submitted via the Town Hall agent
-- sentiment is pre-classified by the agent at submission time (positive, negative, neutral)
CREATE TABLE feedback (
    id          SERIAL PRIMARY KEY,
    topic       TEXT,
    summary     TEXT,
    sentiment   VARCHAR(20),           -- 'positive' | 'negative' | 'neutral'
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    session_id  VARCHAR(255)
);

-- Full conversation history from the ChatKit-powered Town Hall interface
-- item_type is either 'user_message' or 'assistant_message'
-- item_json holds the full message payload including content array
CREATE TABLE chatkit_thread_items (
    id          TEXT PRIMARY KEY,
    thread_id   VARCHAR(50),
    item_type   VARCHAR(50),           -- 'user_message' | 'assistant_message'
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    item_json   JSONB
);
```

### Notes on the data

- The `feedback` table already has a `sentiment` column populated by the agent — the Insights API can use this directly for trend analysis without re-running sentiment classification.
- The `topic` field is a short human-readable label (e.g. `"Cleanliness of Tokyo Streets"`), while `summary` is the full agent-generated description — both are available for topic clustering.
- The `chatkit_thread_items` table stores the raw conversation turns (user + assistant messages) grouped by `thread_id`. This can be used for deeper conversational analytics such as session volume, response patterns, and unresolved concern detection.
- `session_id` in `feedback` maps to a `thread_id` in `chatkit_thread_items`, allowing joins between a feedback record and its originating conversation.

---

## Related projects

- [Digital Town Hall](https://github.com/Amigda-Labs/digital-town-hall) — the full civic engagement platform this demo is based on
- [mcp-hr-test](https://github.com/jao-o-garcia/mcp-hr-test) — base reference for the MCP server pattern used in this repo
- [FastMCP](https://github.com/jlowin/fastmcp) — the MCP server framework used
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) — agent framework

---

## License

MIT