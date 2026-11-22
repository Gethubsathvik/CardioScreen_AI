"""Pydantic models: validated input and output of the prediction service."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PatientFeatures(BaseModel):
    """The 13 clinical inputs. Ranges are deliberately wider than the training data
    (to reject typos, not unusual patients); out-of-distribution values are flagged
    separately by the predictor."""

    model_config = ConfigDict(extra="forbid")

    age: int = Field(ge=1, le=120, description="Age in years")
    sex: Literal[0, 1] = Field(description="0 = female, 1 = male")
    cp: Literal[0, 1, 2, 3] = Field(
        description="Chest pain: 0 asymptomatic, 1 atypical angina, 2 non-anginal, 3 typical angina"
    )
    trestbps: int = Field(ge=60, le=260, description="Resting systolic blood pressure (mm Hg)")
    chol: int = Field(ge=80, le=700, description="Serum cholesterol (mg/dl)")
    fbs: Literal[0, 1] = Field(description="Fasting blood sugar > 120 mg/dl")
    restecg: Literal[0, 1, 2] = Field(description="0 LV hypertrophy, 1 normal, 2 ST-T abnormality")
    thalach: int = Field(ge=50, le=250, description="Maximum heart rate achieved (bpm)")
    exang: Literal[0, 1] = Field(description="Exercise-induced angina")
    oldpeak: float = Field(ge=0, le=10, description="ST depression induced by exercise")
    slope: Literal[0, 1, 2] = Field(description="0 downsloping, 1 flat, 2 upsloping")
    ca: Literal[0, 1, 2, 3, 4] = Field(description="Major vessels coloured by fluoroscopy")
    thal: Literal[0, 1, 2, 3] = Field(description="0 unknown, 1 fixed, 2 normal, 3 reversible")


class FeatureContribution(BaseModel):
    feature: str
    label: str
    value: float
    effect: float = Field(
        description="Change in disease probability versus replacing this feature with a "
        "typical (reference) value. Positive = pushes risk up."
    )


class Prediction(BaseModel):
    disease_probability: float = Field(ge=0, le=1)
    prediction: Literal[0, 1] = Field(description="1 = disease predicted at the decision threshold")
    risk_band: Literal["low", "moderate", "high"]
    message: str
    model_name: str
    threshold: float
    contributions: list[FeatureContribution] = []
    warnings: list[str] = []
    disclaimer: str


class BatchRequest(BaseModel):
    patients: list[PatientFeatures] = Field(min_length=1, max_length=1000)


class BatchResponse(BaseModel):
    count: int
    predictions: list[Prediction]
