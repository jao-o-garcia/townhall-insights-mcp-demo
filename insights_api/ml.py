"""ML utilities: topic clustering, anomaly detection, sentiment aggregation."""
from __future__ import annotations

from collections import Counter, defaultdict


def get_topic_clusters(
    summaries: list[str],
    topics: list[str | None] | None = None,
    top_k: int = 10,
) -> list[dict]:
    """
    Group summaries into topic clusters.

    When pre-classified topic labels are provided (from the DB), groups by label.
    Falls back to TF-IDF + KMeans when no labels are available.
    """
    if not summaries:
        return []

    # Fast path: use pre-classified topics from the DB
    if topics and any(t for t in topics):
        by_topic: dict[str, list[str]] = defaultdict(list)
        for summary, topic in zip(summaries, topics):
            label = (topic or "Other").strip()
            by_topic[label].append(summary)

        clusters = []
        for topic_label, sums in sorted(by_topic.items(), key=lambda x: -len(x[1]))[:top_k]:
            clusters.append({
                "topic": topic_label,
                "count": len(sums),
                "representative_summaries": [s for s in sums[:3] if s],
            })
        return clusters

    # Fallback: unsupervised TF-IDF + KMeans
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans

    n_clusters = min(top_k, max(2, len(summaries) // 5))
    vect = TfidfVectorizer(max_features=500, stop_words="english", min_df=1)
    X = vect.fit_transform(summaries)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    terms = vect.get_feature_names_out()
    centers = km.cluster_centers_

    clusters = []
    for cluster_id in range(n_clusters):
        mask = labels == cluster_id
        cluster_summaries = [s for s, m in zip(summaries, mask) if m]
        if not cluster_summaries:
            continue
        top_idx = centers[cluster_id].argsort()[-3:][::-1]
        topic_label = " / ".join(terms[i] for i in top_idx)
        clusters.append({
            "topic": topic_label,
            "count": len(cluster_summaries),
            "representative_summaries": cluster_summaries[:3],
        })

    clusters.sort(key=lambda x: -x["count"])
    return clusters[:top_k]


def detect_anomalies(
    daily_counts: list[int | float],
    metric_name: str = "value",
) -> list[dict]:
    """
    Detect anomalies in a time series using z-score method.
    Returns anomalous entries, or the last entry when nothing stands out.
    """
    import numpy as np

    if len(daily_counts) < 3:
        return []

    arr = np.array(daily_counts, dtype=float)
    mean = float(np.mean(arr))
    std = float(np.std(arr))
    expected = f"{mean:.1f} ± {std:.1f}"

    if std == 0:
        return [{
            "metric": metric_name,
            "value": float(arr[-1]),
            "expected_range": f"{mean:.1f} ± 0",
            "is_anomaly": False,
            "details": {"message": "No variation in data."},
        }]

    z_threshold = 2.0
    results = []
    for i, val in enumerate(arr):
        z = abs((val - mean) / std)
        is_anomaly = z > z_threshold
        results.append({
            "metric": metric_name,
            "value": float(val),
            "expected_range": expected,
            "is_anomaly": is_anomaly,
            "details": {
                "z_score": round(float(z), 2),
                "day_index": i,
                "message": f"{'Spike detected' if is_anomaly else 'Within normal range'} (z={z:.2f}).",
            },
        })

    anomalies = [r for r in results if r["is_anomaly"]]
    return anomalies if anomalies else [results[-1]]


def aggregate_sentiment(labels: list[str]) -> list[dict]:
    """Count sentiment labels and return percentage buckets."""
    if not labels:
        return [{"label": "neutral", "count": 0, "pct": 0.0}]

    counts = Counter(lbl.lower().strip() for lbl in labels)
    total = len(labels)

    buckets: list[dict] = []
    for label in ("positive", "negative", "neutral"):
        count = counts.get(label, 0)
        buckets.append({
            "label": label,
            "count": count,
            "pct": round(100 * count / total, 1) if total else 0.0,
        })

    # Surface any labels beyond the standard three
    for label, count in counts.items():
        if label not in ("positive", "negative", "neutral"):
            buckets.append({
                "label": label,
                "count": count,
                "pct": round(100 * count / total, 1) if total else 0.0,
            })

    return buckets
