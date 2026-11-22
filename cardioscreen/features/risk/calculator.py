"""Risk assessment module - risk calculation, bands, and thresholds."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ...core.config import settings
from ...models.domain import RiskBand


class DecisionThreshold(Enum):
    """Decision thresholds for classification."""

    DEFAULT = 0.5
    HIGH_SENSITIVITY = 0.33  # Lower threshold = catch more disease
    HIGH_SPECIFICITY = 0.66  # Higher threshold = fewer false alarms


@dataclass(frozen=True)
class RiskAssessment:
    """Complete risk assessment result."""

    probability: float
    risk_band: RiskBand
    prediction: int  # 0 or 1
    threshold: float
    message: str

    @property
    def is_high_risk(self) -> bool:
        return self.risk_band == RiskBand.HIGH

    @property
    def is_moderate_risk(self) -> bool:
        return self.risk_band == RiskBand.MODERATE

    @property
    def is_low_risk(self) -> bool:
        return self.risk_band == RiskBand.LOW


class RiskCalculator:
    """Service for calculating risk from probability."""

    def __init__(self, threshold: float = DecisionThreshold.DEFAULT.value):
        self.threshold = threshold
        self.risk_bands = settings.risk_bands  # [(0.33, "low"), (0.66, "moderate"), (1.01, "high")]

    def calculate(self, probability: float) -> RiskAssessment:
        """Calculate risk assessment from probability."""
        # Determine risk band
        risk_band = RiskBand.HIGH
        for upper, name in self.risk_bands:
            if probability < upper:
                risk_band = RiskBand(name)
                break

        # Binary prediction
        prediction = int(probability >= self.threshold)

        # Generate message
        if prediction == 1:
            message = (
                f"Model estimates a {probability:.0%} probability of heart disease "
                f"({risk_band.value} risk). Further clinical evaluation is advised."
            )
        else:
            message = (
                f"Model estimates a {probability:.0%} probability of heart disease "
                f"({risk_band.value} risk). No strong indication of disease."
            )

        return RiskAssessment(
            probability=probability,
            risk_band=risk_band,
            prediction=prediction,
            threshold=self.threshold,
            message=message,
        )

    def calculate_batch(self, probabilities: list[float]) -> list[RiskAssessment]:
        """Calculate risk assessments for multiple probabilities."""
        return [self.calculate(p) for p in probabilities]

    @classmethod
    def from_config(cls) -> "RiskCalculator":
        """Create calculator from settings."""
        return cls(threshold=settings.model_threshold)


# Clinical decision support messages
CLINICAL_MESSAGES = {
    RiskBand.LOW: {
        "summary": "Low probability of heart disease",
        "recommendation": "Routine follow-up. Maintain healthy lifestyle.",
        "urgency": "Routine",
    },
    RiskBand.MODERATE: {
        "summary": "Moderate probability of heart disease",
        "recommendation": "Consider further diagnostic testing (stress test, imaging). Discuss with cardiologist.",
        "urgency": "Soon (1-2 weeks)",
    },
    RiskBand.HIGH: {
        "summary": "High probability of heart disease",
        "recommendation": "Urgent cardiology referral. Consider coronary angiography.",
        "urgency": "Urgent (within days)",
    },
}

# Feature importance descriptions for clinical interpretation
FEATURE_CLINICAL_IMPORTANCE = {
    "exang": "Exercise-induced angina - strongest predictor",
    "ca": "Number of diseased vessels - direct anatomical evidence",
    "thal": "Thallium defect - perfusion abnormality",
    "cp": "Chest pain type - typical angina most specific",
    "oldpeak": "ST depression - ischemia indicator",
    "thalach": "Max heart rate - lower = worse prognosis",
    "slope": "ST slope - downsloping most concerning",
    "restecg": "Resting ECG abnormalities",
    "age": "Age - risk increases with age",
    "sex": "Male sex - higher baseline risk",
    "chol": "Cholesterol - moderate risk factor",
    "trestbps": "Blood pressure - moderate risk factor",
    "fbs": "Diabetes indicator - moderate risk factor",
}