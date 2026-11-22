"""Pydantic models for request/response validation and serialization."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class PatientFeatures(BaseModel):
    """The 13 clinical inputs for heart disease prediction."""

    model_config = ConfigDict(extra="forbid")

    age: Annotated[int, Field(ge=1, le=120, description="Age in years")]
    sex: Annotated[Literal[0, 1], Field(description="0 = female, 1 = male")]
    cp: Annotated[Literal[0, 1, 2, 3], Field(
        description="Chest pain: 0 asymptomatic, 1 atypical angina, 2 non-anginal, 3 typical angina"
    )]
    trestbps: Annotated[int, Field(ge=60, le=260, description="Resting systolic blood pressure (mm Hg)")]
    chol: Annotated[int, Field(ge=80, le=700, description="Serum cholesterol (mg/dl)")]
    fbs: Annotated[Literal[0, 1], Field(description="Fasting blood sugar > 120 mg/dl")]
    restecg: Annotated[Literal[0, 1, 2], Field(description="0 LV hypertrophy, 1 normal, 2 ST-T abnormality")]
    thalach: Annotated[int, Field(ge=50, le=250, description="Maximum heart rate achieved (bpm)")]
    exang: Annotated[Literal[0, 1], Field(description="Exercise-induced angina")]
    oldpeak: Annotated[float, Field(ge=0, le=10, description="ST depression induced by exercise")]
    slope: Annotated[Literal[0, 1, 2], Field(description="0 downsloping, 1 flat, 2 upsloping")]
    ca: Annotated[Literal[0, 1, 2, 3, 4], Field(description="Major vessels coloured by fluoroscopy")]
    thal: Annotated[Literal[0, 1, 2, 3], Field(description="0 unknown, 1 fixed, 2 normal, 3 reversible")]


class FeatureContribution(BaseModel):
    """Feature contribution to the prediction (occlusion-based explanation)."""

    feature: str = Field(description="Feature name")
    label: str = Field(description="Human-readable feature label")
    value: float = Field(description="Actual feature value for this patient")
    effect: float = Field(
        description="Change in disease probability versus replacing this feature with a "
        "typical (reference) value. Positive = pushes risk up."
    )


class Prediction(BaseModel):
    """Single prediction response."""

    disease_probability: Annotated[float, Field(ge=0, le=1, description="Probability of heart disease")]
    prediction: Annotated[Literal[0, 1], Field(description="1 = disease predicted at decision threshold")]
    risk_band: Annotated[Literal["low", "moderate", "high"], Field(description="Risk category")]
    message: str = Field(description="Human-readable interpretation")
    model_name: str = Field(description="Name of the model used")
    threshold: Annotated[float, Field(ge=0, le=1, description="Decision threshold")]
    contributions: list[FeatureContribution] = Field(default_factory=list, description="Top feature contributions")
    warnings: list[str] = Field(default_factory=list, description="Out-of-range warnings")
    disclaimer: str = Field(description="Medical disclaimer")


class BatchRequest(BaseModel):
    """Batch prediction request."""

    patients: Annotated[list[PatientFeatures], Field(min_length=1, max_length=1000)]


class BatchResponse(BaseModel):
    """Batch prediction response."""

    count: int = Field(description="Number of predictions")
    predictions: list[Prediction] = Field(description="Individual predictions")


class FeatureSpec(BaseModel):
    """Feature specification for dynamic form generation."""

    name: str
    label: str
    kind: Literal["numeric", "categorical", "binary"]
    description: str
    min: float | None = None
    max: float | None = None
    unit: str = ""
    choices: list[dict[str, str | int]] = []


class ModelInfo(BaseModel):
    """Model metadata response."""

    model_name: str
    threshold: float
    cv_roc_auc: float
    test_roc_auc: float
    test_accuracy: float
    test_recall_sensitivity: float
    test_specificity: float
    sklearn_version: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["ok"]
    model_loaded: bool
    version: str


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    message: str
    details: dict = {}