"""Backward-compatible config module using new settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .core.config import settings

ROOT = settings.root_dir
DATA_PATH = settings.data_path
MODELS_DIR = settings.models_dir
REPORTS_DIR = settings.reports_dir
MODEL_PATH = settings.model_path

RANDOM_STATE = settings.random_state
TEST_SIZE = settings.test_size
TARGET_COL = settings.target_col
TARGET_ONE_MEANS_HEALTHY = settings.target_one_means_healthy
RISK_BANDS = tuple(settings.risk_bands)
DISCLAIMER = settings.disclaimer


@dataclass(frozen=True)
class Feature:
    name: str
    label: str
    kind: str  # "numeric" | "categorical" | "binary"
    description: str
    min: float | None = None
    max: float | None = None
    unit: str = ""
    choices: dict[int, str] = field(default_factory=dict)


# Build FEATURES from settings
FEATURES = tuple(
    Feature(
        name=f.name,
        label=f.label,
        kind=f.kind,
        description=f.description,
        min=f.min,
        max=f.max,
        unit=f.unit,
        choices=f.choices,
    )
    for f in settings.FEATURES
)

FEATURE_NAMES: list[str] = [f.name for f in FEATURES]
FEATURE_BY_NAME: dict[str, Feature] = {f.name: f for f in FEATURES}
NUMERIC_FEATURES: list[str] = [f.name for f in FEATURES if f.kind == "numeric"]
CATEGORICAL_FEATURES: list[str] = [f.name for f in FEATURES if f.kind == "categorical"]
BINARY_FEATURES: list[str] = [f.name for f in FEATURES if f.kind == "binary"]


def feature_spec() -> list[dict]:
    """JSON-serialisable description of the form fields (used by the web UI)."""
    return settings.get_feature_spec() if hasattr(settings, 'get_feature_spec') else [
        {
            "name": f.name,
            "label": f.label,
            "kind": f.kind,
            "description": f.description,
            "min": f.min,
            "max": f.max,
            "unit": f.unit,
            "choices": [{"value": k, "label": v} for k, v in f.choices.items()],
        }
        for f in FEATURES
    ]


# For backward compatibility with old imports
__all__ = [
    "ROOT", "DATA_PATH", "MODELS_DIR", "REPORTS_DIR", "MODEL_PATH",
    "RANDOM_STATE", "TEST_SIZE", "TARGET_COL", "TARGET_ONE_MEANS_HEALTHY",
    "RISK_BANDS", "DISCLAIMER",
    "Feature", "FEATURES", "FEATURE_NAMES", "FEATURE_BY_NAME",
    "NUMERIC_FEATURES", "CATEGORICAL_FEATURES", "BINARY_FEATURES",
    "feature_spec",
]