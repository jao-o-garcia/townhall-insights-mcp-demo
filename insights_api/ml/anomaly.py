"""Isolation Forest / simple anomaly detection for incident and volume metrics."""
import math
from typing import Any

try:
    from sklearn.ensemble import IsolationForest
    import numpy as np
    _HAS_SKLEARN = True
except Exception:
    _HAS_SKLEARN = False


def detect_anomalies(values: list[float], metric_name: str = "value") -> list[dict[str, Any]]:
    """
    Flag anomalies in a series of values. Uses Isolation Forest if available,
    else simple z-score style check (mean ± 2*std).
    """
    if not values or len(values) < 3:
        return []

    arr = [float(v) for v in values]
    if _HAS_SKLEARN:
        X = np.array(arr).reshape(-1, 1)
        clf = IsolationForest(random_state=42, contamination=0.1)
        pred = clf.fit_predict(X)
        # -1 = anomaly
        anomalies = []
        for i, (v, p) in enumerate(zip(arr, pred)):
            if p == -1:
                anomalies.append({
                    "source": "isolation_forest",
                    "metric": metric_name,
                    "value": v,
                    "expected_range": f"based on {len(arr)} samples",
                    "is_anomaly": True,
                    "details": {"index": i},
                })
        return anomalies

    # Fallback: mean ± 2*std
    n = len(arr)
    mean = sum(arr) / n
    variance = sum((x - mean) ** 2 for x in arr) / n
    std = math.sqrt(variance) if variance else 0
    if std == 0:
        return []
    anomalies = []
    for i, v in enumerate(arr):
        z = (v - mean) / std if std else 0
        if abs(z) > 2:
            anomalies.append({
                "source": "z_score",
                "metric": metric_name,
                "value": v,
                "expected_range": f"mean={mean:.2f} std={std:.2f}",
                "is_anomaly": True,
                "details": {"index": i, "z_score": round(z, 2)},
            })
    return anomalies
