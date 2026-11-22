"""Enumerations for clinical features."""

from __future__ import annotations

from enum import IntEnum


class Sex(IntEnum):
    """Biological sex."""

    FEMALE = 0
    MALE = 1

    @property
    def label(self) -> str:
        return {Sex.FEMALE: "Female", Sex.MALE: "Male"}[self]


class ChestPainType(IntEnum):
    """Chest pain type."""

    ASYMPTOMATIC = 0
    ATYPICAL_ANGINA = 1
    NON_ANGINAL = 2
    TYPICAL_ANGINA = 3

    @property
    def label(self) -> str:
        return {
            ChestPainType.ASYMPTOMATIC: "Asymptomatic",
            ChestPainType.ATYPICAL_ANGINA: "Atypical angina",
            ChestPainType.NON_ANGINAL: "Non-anginal pain",
            ChestPainType.TYPICAL_ANGINA: "Typical angina",
        }[self]


class RestingECG(IntEnum):
    """Resting ECG result."""

    LV_HYPERTROPHY = 0
    NORMAL = 1
    ST_T_ABNORMALITY = 2

    @property
    def label(self) -> str:
        return {
            RestingECG.LV_HYPERTROPHY: "Left ventricular hypertrophy",
            RestingECG.NORMAL: "Normal",
            RestingECG.ST_T_ABNORMALITY: "ST-T wave abnormality",
        }[self]


class FastingBloodSugar(IntEnum):
    """Fasting blood sugar > 120 mg/dl."""

    NO = 0
    YES = 1

    @property
    def label(self) -> str:
        return {FastingBloodSugar.NO: "No", FastingBloodSugar.YES: "Yes"}[self]


class ExerciseInducedAngina(IntEnum):
    """Exercise-induced angina."""

    NO = 0
    YES = 1

    @property
    def label(self) -> str:
        return {ExerciseInducedAngina.NO: "No", ExerciseInducedAngina.YES: "Yes"}[self]


class ST_Slope(IntEnum):
    """ST segment slope."""

    DOWNSLOPING = 0
    FLAT = 1
    UPSLOPING = 2

    @property
    def label(self) -> str:
        return {
            ST_Slope.DOWNSLOPING: "Downsloping",
            ST_Slope.FLAT: "Flat",
            ST_Slope.UPSLOPING: "Upsloping",
        }[self]


class MajorVessels(IntEnum):
    """Number of major vessels colored by fluoroscopy."""

    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4

    @property
    def label(self) -> str:
        return str(self.value)


class Thalassemia(IntEnum):
    """Thallium stress test result."""

    UNKNOWN = 0
    FIXED_DEFECT = 1
    NORMAL = 2
    REVERSIBLE_DEFECT = 3

    @property
    def label(self) -> str:
        return {
            Thalassemia.UNKNOWN: "Unknown / null",
            Thalassemia.FIXED_DEFECT: "Fixed defect",
            Thalassemia.NORMAL: "Normal",
            Thalassemia.REVERSIBLE_DEFECT: "Reversible defect",
        }[self]


# Feature choice mappings for form generation
FEATURE_CHOICES = {
    "sex": {e.value: e.label for e in Sex},
    "cp": {e.value: e.label for e in ChestPainType},
    "restecg": {e.value: e.label for e in RestingECG},
    "fbs": {e.value: e.label for e in FastingBloodSugar},
    "exang": {e.value: e.label for e in ExerciseInducedAngina},
    "slope": {e.value: e.label for e in ST_Slope},
    "ca": {e.value: e.label for e in MajorVessels},
    "thal": {e.value: e.label for e in Thalassemia},
}