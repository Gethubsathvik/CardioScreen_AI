"""Model serialization utilities."""

from __future__ import annotations

import joblib
from pathlib import Path
from typing import Any


def save_model(artifact: dict[str, Any], path: Path | str) -> Path:
    """Save model artifact to disk."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, path)
    return path


def load_model(path: Path | str) -> dict[str, Any]:
    """Load model artifact from disk."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Model not found: {path}")
    return joblib.load(path)


def get_model_info(artifact: dict[str, Any]) -> dict[str, Any]:
    """Extract human-readable model info from artifact."""
    metrics = artifact.get("metrics", {})
    return {
        "model_name": artifact.get("model_name"),
        "threshold": artifact.get("threshold"),
        "cv_roc_auc": metrics.get("cv_roc_auc"),
        "test_roc_auc": metrics.get("test_roc_auc"),
        "test_accuracy": metrics.get("test_accuracy"),
        "test_recall_sensitivity": metrics.get("test_recall_sensitivity"),
        "test_specificity": metrics.get("test_specificity"),
        "sklearn_version": artifact.get("sklearn_version"),
        "feature_count": len(artifact.get("feature_names", [])),
    }