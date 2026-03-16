"""FastAPI Insights Service entrypoint."""
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from insights_api.routers import clusters, sentiment, anomalies, trends

app = FastAPI(
    title="Town Hall Insights API",
    description="ML-powered insights (topic clustering, sentiment, anomalies) for civic feedback and conversations.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clusters.router)
app.include_router(sentiment.router)
app.include_router(anomalies.router)
app.include_router(trends.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/refresh")
def refresh_insights():
    """On-demand refresh of cached insights (no-op for now; cache can be added later)."""
    return {"ok": True, "message": "Refresh triggered. Results are computed on demand."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8001)))
