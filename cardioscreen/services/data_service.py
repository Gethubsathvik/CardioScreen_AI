"""Data loading, validation, and preprocessing service."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from ..core.config import settings
from ..core.exceptions import DataError, ValidationError
from ..models.domain import DatasetInfo

log = logging.getLogger(__name__)

TARGET_DISEASE = "disease"


class DataValidationError(ValidationError):
    """Raised when dataset validation fails."""

    pass


@dataclass(frozen=True)
class DatasetInfo:
    """Dataset metadata."""

    raw_rows: int
    duplicate_rows: int
    unique_rows: int
    disease_prevalence: float


class DataService:
    """Service for data loading, validation, and splitting."""

    def __init__(self, data_path: Path | str | None = None):
        self.data_path = Path(data_path) if data_path else settings.data_path
        self._cache: pd.DataFrame | None = None
        self._info: DatasetInfo | None = None

    def load_dataset(self, force_reload: bool = False) -> tuple[pd.DataFrame, DatasetInfo]:
        """Load, validate, de-duplicate, and add explicit disease label."""
        if self._cache is not None and not force_reload:
            return self._cache, self._info

        try:
            raw = pd.read_csv(self.data_path)
        except FileNotFoundError:
            raise DataError(f"Dataset not found at {self.data_path}")
        except Exception as e:
            raise DataError(f"Failed to load dataset: {e}")

        self._validate(raw)

        dup = int(raw.duplicated().sum())
        df = raw.drop_duplicates().reset_index(drop=True)

        if dup:
            log.warning("Dropped %d exact duplicate rows (%d -> %d)", dup, len(raw), len(df))

        # Derive explicit disease label (1 = disease present)
        df[TARGET_DISEASE] = (
            1 - df[settings.target_col] if settings.target_one_means_healthy else df[settings.target_col]
        )

        self._info = DatasetInfo(
            raw_rows=len(raw),
            duplicate_rows=dup,
            unique_rows=len(df),
            disease_prevalence=float(df[TARGET_DISEASE].mean()),
        )
        self._cache = df
        return df, self._info

    def _validate(self, df: pd.DataFrame) -> None:
        """Validate dataset schema and values."""
        from ..models.enums import FEATURE_CHOICES
        from ..core.config import settings as config

        # Check required columns
        required_cols = [*config.FEATURE_NAMES, config.target_col]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise DataValidationError(f"Missing columns: {missing}")

        # Check for missing values
        if df[required_cols].isna().any().any():
            raise DataValidationError("Dataset contains missing values")

        # Check target is binary
        if not set(df[config.target_col].unique()) <= {0, 1}:
            raise DataValidationError("target must be binary 0/1")

        # Validate each feature
        for feature_name in config.FEATURE_NAMES:
            col = df[feature_name]
            feature_config = config.FEATURE_BY_NAME.get(feature_name)
            if not feature_config:
                continue

            if feature_config.kind != "numeric":
                # Categorical/binary: check allowed values
                allowed = set(feature_config.choices.keys())
                bad = set(col.unique()) - allowed
                if bad:
                    raise DataValidationError(f"{feature_name}: unexpected categories {sorted(bad)}")
            else:
                # Numeric: check range
                if col.min() < feature_config.min or col.max() > feature_config.max:
                    raise DataValidationError(
                        f"{feature_name}: values outside [{feature_config.min}, {feature_config.max}]"
                    )

    def split(
        self,
        df: pd.DataFrame | None = None,
        test_size: float | None = None,
        seed: int | None = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Stratified train/test split."""
        if df is None:
            df, _ = self.load_dataset()

        X = df[settings.FEATURE_NAMES]
        y = df[TARGET_DISEASE]

        return train_test_split(
            X, y,
            test_size=test_size or settings.test_size,
            stratify=y,
            random_state=seed or settings.random_state,
        )

    def get_feature_names(self) -> list[str]:
        """Get list of feature names in order."""
        return settings.FEATURE_NAMES

    def get_numeric_features(self) -> list[str]:
        """Get list of numeric feature names."""
        return settings.NUMERIC_FEATURES

    def get_categorical_features(self) -> list[str]:
        """Get list of categorical feature names."""
        return settings.CATEGORICAL_FEATURES

    def get_binary_features(self) -> list[str]:
        """Get list of binary feature names."""
        return settings.BINARY_FEATURES

    def get_reference_values(self, df: pd.DataFrame | None = None) -> dict[str, float | int]:
        """Get reference (median/mode) values for each feature."""
        if df is None:
            df, _ = self.load_dataset()

        reference = {}
        for col in settings.FEATURE_NAMES:
            if col in settings.NUMERIC_FEATURES:
                reference[col] = float(df[col].median())
            else:
                reference[col] = int(df[col].mode()[0])
        return reference

    def get_training_ranges(self, df: pd.DataFrame | None = None) -> dict[str, list[float]]:
        """Get min/max ranges for numeric features from training data."""
        if df is None:
            df, _ = self.load_dataset()

        return {
            col: [float(df[col].min()), float(df[col].max())]
            for col in settings.NUMERIC_FEATURES
        }

    def get_feature_spec(self) -> list[dict]:
        """Get JSON-serializable feature specification for UI."""
        from ..core.config import settings as config

        spec = []
        for feature in config.FEATURES:
            spec.append({
                "name": feature.name,
                "label": feature.label,
                "kind": feature.kind,
                "description": feature.description,
                "min": feature.min,
                "max": feature.max,
                "unit": feature.unit,
                "choices": [{"value": k, "label": v} for k, v in feature.choices.items()],
            })
        return spec