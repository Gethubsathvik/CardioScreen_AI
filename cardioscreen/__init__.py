"""CardioScreen AI: heart disease risk screening."""

__version__ = "2.0.0"

# Core exports
from .core.config import settings
from .core.exceptions import (
    CardioScreenError,
    ModelNotFoundError,
    ValidationError,
    DataError,
)
from .core.logging import setup_logging, get_logger

# Model exports
from .models.schemas import (
    PatientFeatures,
    FeatureContribution,
    Prediction,
    BatchRequest,
    BatchResponse,
    FeatureSpec,
)
from .models.domain import RiskBand, FeatureType
from .models.enums import Sex, ChestPainType, RestingECG, ST_Slope, Thalassemia

# Service exports
from .services.model_service import ModelService
from .services.training_service import TrainingService
from .services.data_service import DataService
from .services.explanation_service import ExplanationService

# Feature exports
from .features.patient.service import PatientService
from .features.clinical.service import ClinicalService
from .features.risk.calculator import RiskCalculator

# API exports
from .api.app import create_app

__all__ = [
    # Core
    "settings",
    "setup_logging",
    "get_logger",
    "CardioScreenError",
    "ModelNotFoundError",
    "ValidationError",
    "DataError",
    # Models
    "PatientFeatures",
    "FeatureContribution",
    "Prediction",
    "BatchRequest",
    "BatchResponse",
    "FeatureSpec",
    "RiskBand",
    "FeatureType",
    "Sex",
    "ChestPainType",
    "RestingECG",
    "ST_Slope",
    "Thalassemia",
    # Services
    "ModelService",
    "TrainingService",
    "DataService",
    "ExplanationService",
    # Features
    "PatientService",
    "ClinicalService",
    "RiskCalculator",
    # API
    "create_app",
]