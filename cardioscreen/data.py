"""Data loading, validation, de-duplication and splitting.

The raw ``heart.csv`` has 1,025 rows but only 302 unique patients (the Cleveland data
repeated ~3.4x). Splitting *before* removing duplicates puts copies of the same patient
in both train and test, which inflates every metric (Random Forest reaches 100% on the
raw split). ``load_dataset`` therefore de-duplicates first.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from . import config

log = logging.getLogger(__name__)

TARGET_DISEASE = "disease"


class DataValidationError(ValueError):
    """Raised when the dataset does not match the expected schema."""


@dataclass(frozen=True)
class DatasetInfo:
    raw_rows: int
    duplicate_rows: int
    unique_rows: int
    disease_prevalence: float


def validate(df: pd.DataFrame) -> None:
    missing = [c for c in [*config.FEATURE_NAMES, config.TARGET_COL] if c not in df.columns]
    if missing:
        raise DataValidationError(f"Missing columns: {missing}")
    if df[config.FEATURE_NAMES + [config.TARGET_COL]].isna().any().any():
        raise DataValidationError("Dataset contains missing values")
    if not set(df[config.TARGET_COL].unique()) <= {0, 1}:
        raise DataValidationError("target must be binary 0/1")
    for f in config.FEATURES:
        col = df[f.name]
        if f.kind != "numeric":
            bad = set(col.unique()) - set(f.choices)
            if bad:
                raise DataValidationError(f"{f.name}: unexpected categories {sorted(bad)}")
        elif col.min() < f.min or col.max() > f.max:
            raise DataValidationError(f"{f.name}: values outside [{f.min}, {f.max}]")


def load_dataset(path: Path | str = config.DATA_PATH) -> tuple[pd.DataFrame, DatasetInfo]:
    """Load, validate, de-duplicate and add the explicit ``disease`` label."""
    raw = pd.read_csv(path)
    validate(raw)
    dup = int(raw.duplicated().sum())
    df = raw.drop_duplicates().reset_index(drop=True)
    if dup:
        log.warning("Dropped %d exact duplicate rows (%d -> %d)", dup, len(raw), len(df))
    df[TARGET_DISEASE] = (
        1 - df[config.TARGET_COL] if config.TARGET_ONE_MEANS_HEALTHY else df[config.TARGET_COL]
    )
    info = DatasetInfo(len(raw), dup, len(df), float(df[TARGET_DISEASE].mean()))
    return df, info


def split(df: pd.DataFrame, test_size: float = config.TEST_SIZE, seed: int = config.RANDOM_STATE):
    """Stratified train/test split. Returns X_train, X_test, y_train, y_test."""
    X = df[config.FEATURE_NAMES]
    y = df[TARGET_DISEASE]
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=seed)