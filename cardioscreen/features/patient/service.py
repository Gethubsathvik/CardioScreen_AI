"""Patient feature module - data access and business logic for patient data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from ...core.config import settings
from ...models.domain import PatientData
from ...models.schemas import PatientFeatures
from ...services.data_service import DataService


@dataclass
class PatientRepository:
    """Repository for patient data access."""

    data_service: DataService

    def get_training_data(self) -> pd.DataFrame:
        """Get training dataset."""
        df, _ = self.data_service.load_dataset()
        return df

    def get_feature_names(self) -> list[str]:
        """Get feature names."""
        return self.data_service.get_feature_names()

    def get_reference_values(self) -> dict[str, float | int]:
        """Get reference values for features."""
        df, _ = self.data_service.load_dataset()
        return self.data_service.get_reference_values(df)

    def get_training_ranges(self) -> dict[str, list[float]]:
        """Get training ranges for numeric features."""
        df, _ = self.data_service.load_dataset()
        return self.data_service.get_training_ranges(df)


class PatientService:
    """Service for patient-related business logic."""

    def __init__(self, data_service: DataService | None = None):
        self._data_service = data_service or DataService()
        self._repository = PatientRepository(self._data_service)

    def create_patient(self, features: PatientFeatures) -> PatientData:
        """Create PatientData from validated features."""
        return PatientData.from_dict(features.model_dump())

    def validate_patient(self, data: dict[str, Any]) -> PatientFeatures:
        """Validate and create PatientFeatures from raw data."""
        return PatientFeatures(**data)

    def get_example_patient(self) -> PatientFeatures:
        """Get an example patient for testing/demo."""
        return PatientFeatures(
            age=58,
            sex=1,
            cp=0,
            trestbps=140,
            chol=240,
            fbs=0,
            restecg=1,
            thalach=122,
            exang=1,
            oldpeak=2.0,
            slope=1,
            ca=1,
            thal=3,
        )

    def get_healthy_example(self) -> PatientFeatures:
        """Get a healthy example patient."""
        return PatientFeatures(
            age=41,
            sex=0,
            cp=1,
            trestbps=130,
            chol=204,
            fbs=0,
            restecg=0,
            thalach=172,
            exang=0,
            oldpeak=1.4,
            slope=2,
            ca=0,
            thal=2,
        )

    @property
    def repository(self) -> PatientRepository:
        """Access to data repository."""
        return self._repository

    @property
    def data_service(self) -> DataService:
        """Access to data service."""
        return self._data_service