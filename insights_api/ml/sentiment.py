"""VADER sentiment and trend aggregation."""
from collections import Counter
from typing import Any

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
except Exception:
    _vader = None


def classify_sentiment(text: str) -> str:
    """Classify as positive, negative, or neutral."""
    if _vader is None:
        return "neutral"
    s = _vader.polarity_scores(text)
    compound = s["compound"]
    if compound >= 0.05:
        return "positive"
    if compound <= -0.05:
        return "negative"
    return "neutral"


def aggregate_sentiment(labels: list[str]) -> list[dict[str, Any]]:
    """Aggregate pre-classified sentiment labels into buckets with counts and pct."""
    if not labels:
        return []
    total = len(labels)
    counter: Counter[str] = Counter(labels)
    return [
        {
            "label": label,
            "count": count,
            "pct": round(100.0 * count / total, 1),
        }
        for label, count in counter.most_common()
    ]
