"""Pydantic response models for the Insights API."""
from typing import Any
from pydantic import BaseModel


class TopicClusterItem(BaseModel):
    topic: str
    count: int
    representative_summaries: list[str] = []


class ClustersResponse(BaseModel):
    period: str
    clusters: list[TopicClusterItem]
    total_docs: int


class AnomalyItem(BaseModel):
    source: str
    metric: str
    value: float | int
    expected_range: str
    is_anomaly: bool
    details: dict[str, Any] = {}


class AnomaliesResponse(BaseModel):
    period: str
    source: str
    anomalies: list[AnomalyItem]


class SentimentBucket(BaseModel):
    label: str
    count: int
    pct: float


class SentimentTrendsResponse(BaseModel):
    period: str
    buckets: list[SentimentBucket]
    total: int


class ConversationSummaryResponse(BaseModel):
    period: str
    total_threads: int
    total_messages: int
    avg_messages_per_thread: float
    summary: str
