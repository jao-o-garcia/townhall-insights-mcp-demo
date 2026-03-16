"""BERTopic / simple topic clustering for feedback."""
from collections import Counter
from typing import Any

# Optional: use BERTopic when enough data; fallback to simple keyword grouping
def get_topic_clusters(texts: list[str], topics: list[str] | None = None, top_k: int = 10) -> list[dict[str, Any]]:
    """
    Build topic clusters from feedback. If topics (short labels) are provided, group by them.
    Otherwise do simple frequency on first words or use a tiny embedding-based grouping.
    """
    if not texts and not topics:
        return []

    if topics and len(topics) == len(texts):
        # Use pre-existing topic labels from feedback.topic
        counter: Counter[str] = Counter()
        by_topic: dict[str, list[str]] = {}
        for t, s in zip(topics, texts):
            label = (t or "Uncategorized").strip() or "Uncategorized"
            counter[label] += 1
            if label not in by_topic:
                by_topic[label] = []
            if s and len(by_topic[label]) < 3:
                by_topic[label].append((s or "")[:200])
        clusters = [
            {
                "topic": topic,
                "count": count,
                "representative_summaries": by_topic.get(topic, [])[:3],
            }
            for topic, count in counter.most_common(top_k)
        ]
        return clusters

    # No topic labels: simple word-based grouping (first significant word)
    counter: Counter[str] = Counter()
    by_key: dict[str, list[str]] = {}
    for s in texts:
        if not s:
            continue
        words = [w for w in s.split() if len(w) > 2][:3]
        key = " ".join(words[:1]) if words else "Other"
        counter[key] += 1
        if key not in by_key:
            by_key[key] = []
        if len(by_key[key]) < 3:
            by_key[key].append(s[:200])
    return [
        {
            "topic": k,
            "count": c,
            "representative_summaries": by_key.get(k, [])[:3],
        }
        for k, c in counter.most_common(top_k)
    ]
