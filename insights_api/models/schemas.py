"""Pydantic request/response models for Insights API."""
from pydantic import BaseModel, Field
from typing import Any


# --- Topic clusters ---
class TopicClusterItem(BaseModel):
    topic: str
    count: int
    representative_summaries: list[str] = Field(default_factory=list)


class ClustersResponse(BaseModel):
    period: str
    clusters: list[TopicClusterItem]
    total_docs: int


# --- Sentiment ---
class SentimentBucket(BaseModel):
    label: str  # positive | negative | neutral
    count: int
    pct: float


class SentimentTrendsResponse(BaseModel):
    period: str
    buckets: list[SentimentBucket]
    total: int


# --- Anomalies ---
class AnomalyItem(BaseModel):
    source: str
    metric: str
    value: float
    expected_range: str
    is_anomaly: bool
    details: dict[str, Any] = Field(default_factory=dict)


class AnomaliesResponse(BaseModel):
    period: str
    source: str
    anomalies: list[AnomalyItem]


# --- Conversation summary ---
class ConversationSummaryResponse(BaseModel):
    period: str
    total_threads: int
    total_messages: int
    avg_messages_per_thread: float
    summary: str


# --- Refresh ---
class RefreshResponse(BaseModel):
    ok: bool
    message: str
