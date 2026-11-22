"""Model service for loading, prediction, and model management."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import sklearn

from ..core.config import settings
from ..core.exceptions import ModelNotFoundError, PredictionError
from ..models.domain import RiskBand, ModelMetrics, TrainingResult
from ..models.schemas import PatientFeatures, Prediction, FeatureContribution, BatchRequest, BatchResponse, ModelInfo
from .data_service import DataService
from .explanation_service import ExplanationService
from .training_service import TrainingService


class ModelService:
    """Service for model loading, prediction, and management."""

    def __init__(self, model_path: Path | str | None = None):
        self.model_path = Path(model_path) if model_path else settings.model_path
        self._artifact: dict[str, Any] | None = None
        self._pipeline: Any = None
        self._data_service = DataService()
        self._explanation_service: ExplanationService | None = None

    def load(self) -> "ModelService":
        """Load the trained model artifact."""
        if not self.model_path.exists():
            raise ModelNotFoundError(
                f"{self.model_path} not found. Run: python -m cardioscreen train"
            )

        # joblib uses pickle: only load model files you trained yourself
        self._artifact = joblib.load(self.model_path)
        self._pipeline = self._artifact["pipeline"]

        # Check sklearn version compatibility
        if self._artifact.get("sklearn_version") != sklearn.__version__:
            warnings.warn(
                f"Model trained with scikit-learn {self._artifact.get('sklearn_version')}, "
                f"running {sklearn.__version__}. Retrain with `python -m cardioscreen train`."
            )

        # Initialize explanation service
        self._explanation_service = ExplanationService(
            model_pipeline=self._pipeline,
            reference_values=self._artifact["reference"],
            feature_metadata=self._build_feature_metadata(),
        )

        return self

    def _build_feature_metadata(self) -> dict:
        """Build feature metadata dict from config."""
        from ..core.config import settings as config
        from ..models.domain import FeatureMetadata, FeatureType

        metadata = {}
        for feature in config.FEATURES:
            metadata[feature.name] = FeatureMetadata(
                name=feature.name,
                label=feature.label,
                kind=FeatureType(feature.kind),
                description=feature.description,
                min=feature.min,
                max=feature.max,
                unit=feature.unit,
                choices=feature.choices,
            )
        return metadata

    def _ensure_loaded(self) -> None:
        """Ensure model is loaded."""
        if self._pipeline is None:
            self.load()

    def _frame(self, patients: list[PatientFeatures]) -> pd.DataFrame:
        """Convert patient features to DataFrame."""
        return pd.DataFrame([p.model_dump() for p in patients])[settings.FEATURE_NAMES]

    def _warnings(self, patient: PatientFeatures) -> list[str]:
        """Check for out-of-range values."""
        out = []
        train_ranges = self._artifact.get("train_ranges", {})
        for name, (lo, hi) in train_ranges.items():
            v = getattr(patient, name)
            if v < lo or v > hi:
                out.append(
                    f"{name}={v} is outside the training range [{lo:g}, {hi:g}]; treat with caution."
                )
        return out

    def predict_many(
        self,
        patients: list[PatientFeatures],
        explain: bool = False,
    ) -> list[Prediction]:
        """Predict for multiple patients."""
        self._ensure_loaded()

        probs = self._pipeline.predict_proba(self._frame(patients))[:, 1]
        threshold = self._artifact["threshold"]
        model_name = self._artifact["model_name"]

        results = []
        for patient, prob in zip(patients, probs):
            prob = float(prob)
            pred = int(prob >= threshold)
            band = RiskBand.from_probability(prob)

            message = (
                f"Model estimates a {prob:.0%} probability of heart disease ({band.value} risk). "
                + ("Further clinical evaluation is advised." if pred else "No strong indication of disease.")
            )

            contributions = []
            if explain and self._explanation_service:
                explanation = self._explanation_service.explain(
                    patient_data=patient.model_dump(),
                    base_probability=prob,
                    top_k=5,
                )
                contributions = explanation.contributions

            results.append(
                Prediction(
                    disease_probability=round(prob, 4),
                    prediction=pred,
                    risk_band=band.value,
                    message=message,
                    model_name=model_name,
                    threshold=threshold,
                    contributions=contributions,
                    warnings=self._warnings(patient),
                    disclaimer=settings.DISCLAIMER,
                )
            )

        return results

    def predict(self, patient: PatientFeatures, explain: bool = True) -> Prediction:
        """Predict for a single patient."""
        return self.predict_many([patient], explain=explain)[0]

    def predict_batch(self, request: BatchRequest) -> BatchResponse:
        """Predict for a batch of patients."""
        preds = self.predict_many(request.patients, explain=False)
        return BatchResponse(count=len(preds), predictions=preds)

    def info(self) -> ModelInfo:
        """Get model metadata."""
        self._ensure_loaded()
        metrics = self._artifact["metrics"]

        return ModelInfo(
            model_name=self._artifact["model_name"],
            threshold=self._artifact["threshold"],
            cv_roc_auc=metrics["cv_roc_auc"],
            test_roc_auc=metrics["test_roc_auc"],
            test_accuracy=metrics["test_accuracy"],
            test_recall_sensitivity=metrics["test_recall_sensitivity"],
            test_specificity=metrics["test_specificity"],
            sklearn_version=self._artifact["sklearn_version"],
        )

    def health_check(self) -> dict:
        """Health check endpoint."""
        return {
            "status": "ok",
            "model_loaded": self._pipeline is not None,
            "version": settings.app_version,
        }

    def get_feature_spec(self) -> list[dict]:
        """Get feature specification for UI."""
        return self._data_service.get_feature_spec()

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._pipeline is not None

    @property
    def model_name(self) -> str | None:
        """Get model name if loaded."""
        return self._artifact["model_name"] if self._artifact else None

    def retrain(self, data_path: Path | str | None = None) -> TrainingResult:
        """Retrain the model."""
        training_service = TrainingService()
        result = training_service.train(data_path=data_path, model_path=self.model_path)
        # Reload the new model
        self._artifact = None
        self._pipeline = None
        self._explanation_service = None
        self.load()
        return result