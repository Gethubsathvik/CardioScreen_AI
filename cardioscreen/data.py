"""Backward-compatible data module using new DataService."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from . import config
from .services.data_service import DataService, DataValidationError

log = logging.getLogger(__name__)

TARGET_DISEASE = "disease"


@dataclass(frozen=True)
class DatasetInfo:
    raw_rows: int
    duplicate_rows: int
    unique_rows: int
    disease_prevalence: float


# Global data service instance
_data_service = DataService()


def validate(df: pd.DataFrame) -> None:
    """Validate dataset (backward compatible)."""
    _data_service._validate(df)


def load_dataset(path: Path | str = config.DATA_PATH) -> tuple[pd.DataFrame, DatasetInfo]:
    """Load, validate, de-duplicate and add the explicit `disease` label."""
    df, info = _data_service.load_dataset(path)
    return df, DatasetInfo(
        raw_rows=info.raw_rows,
        duplicate_rows=info.duplicate_rows,
        unique_rows=info.unique_rows,
        disease_prevalence=info.disease_prevalence,
    )


def split(df: pd.DataFrame, test_size: float = config.TEST_SIZE, seed: int = config.RANDOM_STATE):
    """Stratified train/test split. Returns X_train, X_test, y_train, y_test."""
    X = df[config.FEATURE_NAMES]
    y = df[TARGET_DISEASE]
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=seed)