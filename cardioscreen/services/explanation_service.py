"""Explanation service for model predictions (occlusion-based local explanations)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from ..core.config import settings
from ..models.domain import FeatureMetadata
from ..models.schemas import FeatureContribution


@dataclass
class ExplanationResult:
    """Result of explanation computation."""

    contributions: list[FeatureContribution]
    base_probability: float


class ExplanationService:
    """Service for generating local explanations using occlusion method."""

    def __init__(self, model_pipeline: Any, reference_values: dict[str, float | int], feature_metadata: dict[str, FeatureMetadata]):
        self.pipeline = model_pipeline
        self.reference_values = reference_values
        self.feature_metadata = feature_metadata
        self.feature_names = settings.FEATURE_NAMES

    def explain(
        self,
        patient_data: dict[str, float | int],
        base_probability: float,
        top_k: int = 5,
    ) -> ExplanationResult:
        """
        Generate local explanation using occlusion method.

        For each feature, replace it with its reference value and measure
        the change in predicted probability.
        """
        row = patient_data.copy()
        variants = []

        for name in self.feature_names:
            variant = row.copy()
            variant[name] = self.reference_values[name]
            variants.append(variant)

        # Predict probabilities for all variants
        variant_df = pd.DataFrame(variants)[self.feature_names]
        probs = self.pipeline.predict_proba(variant_df)[:, 1]

        # Compute contributions
        contributions = []
        for name, prob in zip(self.feature_names, probs):
            metadata = self.feature_metadata.get(name)
            effect = round(float(base_probability - prob), 4)
            contributions.append(
                FeatureContribution(
                    feature=name,
                    label=metadata.label if metadata else name,
                    value=float(row[name]),
                    effect=effect,
                )
            )

        # Sort by absolute effect (descending) and take top k
        contributions.sort(key=lambda c: -abs(c.effect))
        top_contributions = contributions[:top_k]

        return ExplanationResult(
            contributions=top_contributions,
            base_probability=base_probability,
        )

    def explain_batch(
        self,
        patients: list[dict[str, float | int]],
        base_probabilities: list[float],
        top_k: int = 5,
    ) -> list[ExplanationResult]:
        """Generate explanations for multiple patients."""
        return [
            self.explain(patient_data, prob, top_k)
            for patient_data, prob in zip(patients, base_probabilities)
        ]