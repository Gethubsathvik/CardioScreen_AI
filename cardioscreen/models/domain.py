"""Core domain entities and value objects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class RiskBand(str, Enum):
    """Risk band categories."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"

    @classmethod
    def from_probability(cls, probability: float) -> "RiskBand":
        """Determine risk band from probability."""
        if probability < 0.33:
            return cls.LOW
        elif probability < 0.66:
            return cls.MODERATE
        return cls.HIGH

    @property
    def color(self) -> str:
        """CSS color variable for this risk band."""
        return {
            RiskBand.LOW: "var(--low)",
            RiskBand.MODERATE: "var(--mod)",
            RiskBand.HIGH: "var(--high)",
        }[self]

    @property
    def label(self) -> str:
        """Human-readable label."""
        return self.value.capitalize()


class FeatureType(str, Enum):
    """Feature data types."""

    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BINARY = "binary"


@dataclass(frozen=True)
class FeatureMetadata:
    """Immutable feature metadata."""

    name: str
    label: str
    kind: FeatureType
    description: str
    min: float | None = None
    max: float | None = None
    unit: str = ""
    choices: dict[int, str] = None

    def __post_init__(self):
        if self.choices is None:
            object.__setattr__(self, "choices", {})

    def to_spec(self) -> dict:
        """Convert to FeatureSpec dict."""
        return {
            "name": self.name,
            "label": self.label,
            "kind": self.kind.value,
            "description": self.description,
            "min": self.min,
            "max": self.max,
            "unit": self.unit,
            "choices": [{"value": k, "label": v} for k, v in self.choices.items()],
        }


@dataclass(frozen=True)
class PatientData:
    """Immutable patient data container."""

    age: int
    sex: int
    cp: int
    trestbps: int
    chol: int
    fbs: int
    restecg: int
    thalach: int
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "age": self.age,
            "sex": self.sex,
            "cp": self.cp,
            "trestbps": self.trestbps,
            "chol": self.chol,
            "fbs": self.fbs,
            "restecg": self.restecg,
            "thalach": self.thalach,
            "exang": self.exang,
            "oldpeak": self.oldpeak,
            "slope": self.slope,
            "ca": self.ca,
            "thal": self.thal,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PatientData":
        """Create from dictionary."""
        return cls(**{k: data[k] for k in [
            "age", "sex", "cp", "trestbps", "chol", "fbs",
            "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"
        ]})


@dataclass(frozen=True)
class ModelMetrics:
    """Model evaluation metrics."""

    cv_roc_auc: float
    test_roc_auc: float
    test_accuracy: float
    test_precision: float
    test_recall_sensitivity: float
    test_specificity: float
    test_f1: float
    test_brier: float
    confusion_matrix: list[list[int]]


@dataclass(frozen=True)
class TrainingResult:
    """Result of model training."""

    selected_model: str
    selection_criterion: str
    comparison: list[dict]
    dataset_info: dict
    sklearn_version: str
    best_params: dict
    metrics: ModelMetrics