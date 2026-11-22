"""Clinical feature module - clinical feature definitions and validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ...core.config import settings
from ...models.domain import FeatureMetadata, FeatureType
from ...models.enums import FEATURE_CHOICES


@dataclass(frozen=True)
class ClinicalFeature:
    """Clinical feature definition with metadata."""

    name: str
    label: str
    type: FeatureType
    description: str
    min_value: float | None = None
    max_value: float | None = None
    unit: str = ""
    choices: dict[int, str] | None = None

    def __post_init__(self):
        if self.choices is None:
            object.__setattr__(self, "choices", FEATURE_CHOICES.get(self.name, {}))

    def to_metadata(self) -> FeatureMetadata:
        """Convert to FeatureMetadata."""
        return FeatureMetadata(
            name=self.name,
            label=self.label,
            kind=self.type,
            description=self.description,
            min=self.min_value,
            max=self.max_value,
            unit=self.unit,
            choices=self.choices or {},
        )

    def validate(self, value: Any) -> bool:
        """Validate a value against this feature's constraints."""
        if self.type == FeatureType.NUMERIC:
            if not isinstance(value, (int, float)):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
            return True
        elif self.type in (FeatureType.CATEGORICAL, FeatureType.BINARY):
            return value in (self.choices or {})
        return True


class ClinicalService:
    """Service for clinical feature definitions and validation."""

    # Clinical feature definitions matching config.FEATURES
    FEATURES = {
        "age": ClinicalFeature(
            name="age",
            label="🎂 Age",
            type=FeatureType.NUMERIC,
            description="Age in years",
            min_value=1,
            max_value=120,
            unit="years",
        ),
        "sex": ClinicalFeature(
            name="sex",
            label="🧬 Sex",
            type=FeatureType.BINARY,
            description="Biological sex",
        ),
        "cp": ClinicalFeature(
            name="cp",
            label="🫁 Chest pain type",
            type=FeatureType.CATEGORICAL,
            description="Type of chest pain",
        ),
        "trestbps": ClinicalFeature(
            name="trestbps",
            label="🩺 Resting blood pressure",
            type=FeatureType.NUMERIC,
            description="Resting systolic BP",
            min_value=60,
            max_value=260,
            unit="mm Hg",
        ),
        "chol": ClinicalFeature(
            name="chol",
            label="🧪 Serum cholesterol",
            type=FeatureType.NUMERIC,
            description="Serum cholesterol",
            min_value=80,
            max_value=700,
            unit="mg/dl",
        ),
        "fbs": ClinicalFeature(
            name="fbs",
            label="🍬 Fasting blood sugar > 120 mg/dl",
            type=FeatureType.BINARY,
            description="Fasting blood sugar above 120 mg/dl",
        ),
        "restecg": ClinicalFeature(
            name="restecg",
            label="📋 Resting ECG",
            type=FeatureType.CATEGORICAL,
            description="Resting electrocardiographic result",
        ),
        "thalach": ClinicalFeature(
            name="thalach",
            label="💓 Max heart rate achieved",
            type=FeatureType.NUMERIC,
            description="Maximum heart rate",
            min_value=50,
            max_value=250,
            unit="bpm",
        ),
        "exang": ClinicalFeature(
            name="exang",
            label="🏃 Exercise-induced angina",
            type=FeatureType.BINARY,
            description="Angina induced by exercise",
        ),
        "oldpeak": ClinicalFeature(
            name="oldpeak",
            label="📉 ST depression (oldpeak)",
            type=FeatureType.NUMERIC,
            description="ST depression induced by exercise",
            min_value=0,
            max_value=10,
        ),
        "slope": ClinicalFeature(
            name="slope",
            label="📈 ST slope",
            type=FeatureType.CATEGORICAL,
            description="Slope of the peak exercise ST segment",
        ),
        "ca": ClinicalFeature(
            name="ca",
            label="🔬 Major vessels coloured by fluoroscopy",
            type=FeatureType.CATEGORICAL,
            description="Number of major vessels (0-4)",
        ),
        "thal": ClinicalFeature(
            name="thal",
            label="🩸 Thalassemia (thallium test)",
            type=FeatureType.CATEGORICAL,
            description="Thallium stress test result",
        ),
    }

    def __init__(self):
        self._features = self.FEATURES
        self._feature_order = settings.FEATURE_NAMES

    def get_feature(self, name: str) -> ClinicalFeature | None:
        """Get feature by name."""
        return self._features.get(name)

    def get_all_features(self) -> list[ClinicalFeature]:
        """Get all features in order."""
        return [self._features[name] for name in self._feature_order]

    def get_feature_metadata(self, name: str) -> FeatureMetadata | None:
        """Get FeatureMetadata for a feature."""
        feature = self.get_feature(name)
        return feature.to_metadata() if feature else None

    def get_all_metadata(self) -> dict[str, FeatureMetadata]:
        """Get all FeatureMetadata."""
        return {name: feat.to_metadata() for name, feat in self._features.items()}

    def validate_value(self, name: str, value: Any) -> bool:
        """Validate a value for a specific feature."""
        feature = self.get_feature(name)
        return feature.validate(value) if feature else False

    def validate_patient(self, data: dict[str, Any]) -> dict[str, list[str]]:
        """Validate all features for a patient. Returns dict of feature -> list of errors."""
        errors = {}
        for name in self._feature_order:
            feature = self._features[name]
            value = data.get(name)
            if value is None:
                errors[name] = [f"Missing required field: {name}"]
            elif not feature.validate(value):
                errors[name] = [f"Invalid value for {name}: {value}"]
        return errors

    def get_feature_spec(self) -> list[dict]:
        """Get JSON-serializable feature specification for UI."""
        spec = []
        for name in self._feature_order:
            feature = self._features[name]
            spec.append({
                "name": feature.name,
                "label": feature.label,
                "kind": feature.type.value,
                "description": feature.description,
                "min": feature.min_value,
                "max": feature.max_value,
                "unit": feature.unit,
                "choices": [{"value": k, "label": v} for k, v in (feature.choices or {}).items()],
            })
        return spec

    def get_risk_factors(self) -> dict[str, str]:
        """Get clinical risk factor descriptions."""
        return {
            "age": "Older age increases risk",
            "sex": "Male sex increases risk",
            "cp": "Typical angina (cp=3) is most concerning; asymptomatic (cp=0) also elevated risk",
            "trestbps": "Elevated resting BP increases risk",
            "chol": "High cholesterol increases risk",
            "fbs": "Fasting blood sugar > 120 mg/dl increases risk",
            "restecg": "Abnormal resting ECG (LVH or ST-T changes) increases risk",
            "thalach": "Lower max heart rate increases risk",
            "exang": "Exercise-induced angina strongly increases risk",
            "oldpeak": "ST depression during exercise increases risk",
            "slope": "Downsloping ST segment (slope=0) increases risk",
            "ca": "More major vessels colored increases risk",
            "thal": "Fixed (1) and reversible (3) defects increase risk vs normal (2)",
        }