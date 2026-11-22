"""Evaluation metrics utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass
class ClassificationMetrics:
    """Container for classification metrics."""

    accuracy: float
    precision: float
    recall: float  # sensitivity
    specificity: float
    f1: float
    roc_auc: float
    brier: float
    confusion_matrix: list[list[int]]

    @classmethod
    def from_predictions(cls, y_true: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray) -> "ClassificationMetrics":
        """Compute all metrics from predictions."""
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

        return cls(
            accuracy=float(accuracy_score(y_true, y_pred)),
            precision=float(precision_score(y_true, y_pred, zero_division=0)),
            recall=float(recall_score(y_true, y_pred)),
            specificity=float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0,
            f1=float(f1_score(y_true, y_pred)),
            roc_auc=float(roc_auc_score(y_true, y_proba)),
            brier=float(brier_score_loss(y_true, y_proba)),
            confusion_matrix=[[int(tn), int(fp)], [int(fn), int(tp)]],
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall_sensitivity": self.recall,
            "specificity": self.specificity,
            "f1": self.f1,
            "roc_auc": self.roc_auc,
            "brier": self.brier,
            "confusion_matrix": self.confusion_matrix,
        }


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray) -> dict[str, Any]:
    """Compute all classification metrics."""
    return ClassificationMetrics.from_predictions(y_true, y_pred, y_proba).to_dict()


def sensitivity(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute sensitivity (recall)."""
    return float(recall_score(y_true, y_pred))


def specificity(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute specificity."""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0


def brier_score(y_true: np.ndarray, y_proba: np.ndarray) -> float:
    """Compute Brier score."""
    return float(brier_score_loss(y_true, y_proba))