"""Central configuration and feature metadata.

Everything that describes the dataset (feature names, valid ranges, human-readable
category labels) lives here so that validation, the API schema, the web form and the
documentation can never drift apart.

Label conventions below were **verified against the data**, not copied from a
data-card: category counts match the original Cleveland (UCI) dataset exactly, and
the direction of every clinical risk factor was checked (see docs/DATA_NOTES.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "heart.csv"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
MODEL_PATH = MODELS_DIR / "heart_model.joblib"

RANDOM_STATE = 42
TEST_SIZE = 0.2
TARGET_COL = "target"

# In THIS csv, target == 1 means "no heart disease" (healthy) and target == 0 means
# "heart disease". Evidence: exang=1, high oldpeak, ca>0, male sex and higher age are
# all associated with target == 0. We therefore derive an explicit `disease` label
# (1 = disease present) and train/report everything for that positive class.
# If you replace the dataset with one where 1 == disease, set this to False.
TARGET_ONE_MEANS_HEALTHY = True

# Probability thresholds used to turn a probability into a risk band.
RISK_BANDS = ((0.33, "low"), (0.66, "moderate"), (1.01, "high"))

DISCLAIMER = (
    "Educational research project. Not a medical device and not a substitute for "
    "professional medical advice, diagnosis or treatment."
)


@dataclass(frozen=True)
class Feature:
    name: str
    label: str
    kind: str  # "numeric" | "categorical" | "binary"
    description: str
    min: float | None = None
    max: float | None = None
    unit: str = ""
    # value -> human label (categorical / binary only)
    choices: dict[int, str] = field(default_factory=dict)


FEATURES: tuple[Feature, ...] = (
    Feature("age", "Age", "numeric", "Age in years", 1, 120, "years"),
    Feature("sex", "Sex", "binary", "Biological sex", choices={0: "Female", 1: "Male"}),
    Feature(
        "cp",
        "Chest pain type",
        "categorical",
        "Type of chest pain",
        choices={
            0: "Asymptomatic",
            1: "Atypical angina",
            2: "Non-anginal pain",
            3: "Typical angina",
        },
    ),
    Feature("trestbps", "Resting blood pressure", "numeric", "Resting systolic BP", 60, 260, "mm Hg"),
    Feature("chol", "Serum cholesterol", "numeric", "Serum cholesterol", 80, 700, "mg/dl"),
    Feature(
        "fbs",
        "Fasting blood sugar > 120 mg/dl",
        "binary",
        "Fasting blood sugar above 120 mg/dl",
        choices={0: "No", 1: "Yes"},
    ),
    Feature(
        "restecg",
        "Resting ECG",
        "categorical",
        "Resting electrocardiographic result",
        choices={0: "Left ventricular hypertrophy", 1: "Normal", 2: "ST-T wave abnormality"},
    ),
    Feature("thalach", "Max heart rate achieved", "numeric", "Maximum heart rate", 50, 250, "bpm"),
    Feature(
        "exang",
        "Exercise-induced angina",
        "binary",
        "Angina induced by exercise",
        choices={0: "No", 1: "Yes"},
    ),
    Feature("oldpeak", "ST depression (oldpeak)", "numeric", "ST depression induced by exercise", 0, 10),
    Feature(
        "slope",
        "ST slope",
        "categorical",
        "Slope of the peak exercise ST segment",
        choices={0: "Downsloping", 1: "Flat", 2: "Upsloping"},
    ),
    Feature(
        "ca",
        "Major vessels coloured by fluoroscopy",
        "categorical",
        "Number of major vessels (0-4)",
        choices={0: "0", 1: "1", 2: "2", 3: "3", 4: "4"},
    ),
    Feature(
        "thal",
        "Thalassemia (thallium test)",
        "categorical",
        "Thallium stress test result",
        choices={0: "Unknown / null", 1: "Fixed defect", 2: "Normal", 3: "Reversible defect"},
    ),
)

FEATURE_NAMES: list[str] = [f.name for f in FEATURES]
FEATURE_BY_NAME: dict[str, Feature] = {f.name: f for f in FEATURES}
NUMERIC_FEATURES: list[str] = [f.name for f in FEATURES if f.kind == "numeric"]
CATEGORICAL_FEATURES: list[str] = [f.name for f in FEATURES if f.kind == "categorical"]
BINARY_FEATURES: list[str] = [f.name for f in FEATURES if f.kind == "binary"]


def feature_spec() -> list[dict]:
    """JSON-serialisable description of the form fields (used by the web UI)."""
    out = []
    for f in FEATURES:
        out.append(
            {
                "name": f.name,
                "label": f.label,
                "kind": f.kind,
                "description": f.description,
                "min": f.min,
                "max": f.max,
                "unit": f.unit,
                "choices": [{"value": k, "label": v} for k, v in f.choices.items()],
            }
        )
    return out