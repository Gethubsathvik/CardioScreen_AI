"""Domain models and schemas."""

from .schemas import (
    PatientFeatures,
    FeatureContribution,
    Prediction,
    BatchRequest,
    BatchResponse,
    FeatureSpec,
    ModelInfo,
    HealthResponse,
    ErrorResponse,
)
from .domain import (
    RiskBand,
    FeatureType,
    FeatureMetadata,
    PatientData,
    ModelMetrics,
    TrainingResult,
)
from .enums import (
    Sex,
    ChestPainType,
    RestingECG,
    FastingBloodSugar,
    ExerciseInducedAngina,
    ST_Slope,
    MajorVessels,
    Thalassemia,
    FEATURE_CHOICES,
)

__all__ = [
    # Schemas
    "PatientFeatures",
    "FeatureContribution",
    "Prediction",
    "BatchRequest",
    "BatchResponse",
    "FeatureSpec",
    "ModelInfo",
    "HealthResponse",
    "ErrorResponse",
    # Domain
    "RiskBand",
    "FeatureType",
    "FeatureMetadata",
    "PatientData",
    "ModelMetrics",
    "TrainingResult",
    # Enums
    "Sex",
    "ChestPainType",
    "RestingECG",
    "FastingBloodSugar",
    "ExerciseInducedAngina",
    "ST_Slope",
    "MajorVessels",
    "Thalassemia",
    "FEATURE_CHOICES",
]