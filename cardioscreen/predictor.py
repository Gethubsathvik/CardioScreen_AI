"""Backward-compatible predictor using new ModelService."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import sklearn

from . import config
from .core.exceptions import ModelNotFoundError
from .models.schemas import FeatureContribution, PatientFeatures, Prediction
from .services.model_service import ModelService


def risk_band(p: float) -> str:
    """Get risk band from probability (backward compatible)."""
    for upper, name in config.RISK_BANDS:
        if p < upper:
            return name
    return "high"


class Predictor:
    """Backward-compatible predictor interface."""

    def __init__(self, artifact: dict):
        self.a = artifact
        self.pipeline = artifact["pipeline"]
        self.threshold = artifact["threshold"]
        self.model_name = artifact["model_name"]
        if artifact.get("sklearn_version") != sklearn.__version__:
            warnings.warn(
                f"Model trained with scikit-learn {artifact.get('sklearn_version')}, "
                f"running {sklearn.__version__}. Retrain with `python -m cardioscreen train`."
            )

    @classmethod
    def load(cls, path: Path | str = config.MODEL_PATH) -> "Predictor":
        path = Path(path)
        if not path.exists():
            raise ModelNotFoundError(f"{path} not found. Run: python -m cardioscreen train")
        return cls(joblib.load(path))

    def _frame(self, patients: list[PatientFeatures]) -> pd.DataFrame:
        return pd.DataFrame([p.model_dump() for p in patients])[config.FEATURE_NAMES]

    def _warnings(self, p: PatientFeatures) -> list[str]:
        out = []
        for name, (lo, hi) in self.a["train_ranges"].items():
            v = getattr(p, name)
            if v < lo or v > hi:
                out.append(f"{name}={v} is outside the training range [{lo:g}, {hi:g}]; treat with caution.")
        return out

    def _contributions(self, p: PatientFeatures, base_p: float, top: int) -> list[FeatureContribution]:
        row = p.model_dump()
        variants = []
        for name in config.FEATURE_NAMES:
            v = dict(row)
            v[name] = self.a["reference"][name]
            variants.append(v)
        probs = self.pipeline.predict_proba(pd.DataFrame(variants)[config.FEATURE_NAMES])[:, 1]
        contribs = [
            FeatureContribution(
                feature=n,
                label=config.FEATURE_BY_NAME[n].label,
                value=float(row[n]),
                effect=round(float(base_p - q), 4),
            )
            for n, q in zip(config.FEATURE_NAMES, probs)
        ]
        contribs.sort(key=lambda c: -abs(c.effect))
        return contribs[:top]

    def predict_many(self, patients: list[PatientFeatures], explain: bool = False) -> list[Prediction]:
        probs = self.pipeline.predict_proba(self._frame(patients))[:, 1]
        out = []
        for p, prob in zip(patients, probs):
            prob = float(prob)
            pred = int(prob >= self.threshold)
            band = risk_band(prob)
            out.append(
                Prediction(
                    disease_probability=round(prob, 4),
                    prediction=pred,
                    risk_band=band,
                    message=(
                        f"Model estimates a {prob:.0%} probability of heart disease ({band} risk). "
                        + ("Further clinical evaluation is advised." if pred else "No strong indication of disease.")
                    ),
                    model_name=self.model_name,
                    threshold=self.threshold,
                    contributions=self._contributions(p, prob, 5) if explain else [],
                    warnings=self._warnings(p),
                    disclaimer=config.DISCLAIMER,
                )
            )
        return out

    def predict(self, patient: PatientFeatures, explain: bool = True) -> Prediction:
        return self.predict_many([patient], explain=explain)[0]

    def info(self) -> dict:
        m = self.a["metrics"]
        return {
            "model_name": self.model_name,
            "threshold": self.threshold,
            "cv_roc_auc": m["cv_roc_auc"],
            "test_roc_auc": m["test_roc_auc"],
            "test_accuracy": m["test_accuracy"],
            "test_recall_sensitivity": m["test_recall_sensitivity"],
            "test_specificity": m["test_specificity"],
            "sklearn_version": self.a["sklearn_version"],
        }