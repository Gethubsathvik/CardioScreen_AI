"""Training service for model comparison, selection, and persistence."""

from __future__ import annotations

import json
import logging
import warnings
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from ..core.config import settings
from ..core.exceptions import TrainingError
from ..models.domain import ModelMetrics, TrainingResult
from .data_service import DataService

log = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")


class TrainingService:
    """Service for training and comparing models."""

    def __init__(self):
        self._data_service = DataService()

    def _candidates(self) -> dict[str, tuple[Pipeline, dict]]:
        """Define candidate models with pipelines and parameter grids."""
        rs = settings.random_state
        scale = lambda: StandardScaler()  # noqa: E731

        return {
            "Logistic Regression": (
                Pipeline([("s", scale()), ("m", LogisticRegression(max_iter=2000, random_state=rs))]),
                {"m__C": [0.01, 0.1, 1, 10]},
            ),
            "SVM (RBF)": (
                Pipeline([("s", scale()), ("m", SVC(probability=True, random_state=rs))]),
                {"m__C": [0.1, 1, 10], "m__gamma": ["scale", 0.01, 0.1]},
            ),
            "Random Forest": (
                Pipeline([("m", RandomForestClassifier(random_state=rs))]),
                {"m__n_estimators": [200, 400], "m__max_depth": [3, 5, None], "m__min_samples_leaf": [1, 3]},
            ),
            "Gradient Boosting": (
                Pipeline([("m", GradientBoostingClassifier(random_state=rs))]),
                {"m__n_estimators": [50, 100], "m__max_depth": [1, 2, 3], "m__learning_rate": [0.05, 0.1]},
            ),
            "KNN": (
                Pipeline([("s", scale()), ("m", KNeighborsClassifier())]),
                {"m__n_neighbors": [5, 9, 15, 21], "m__weights": ["uniform", "distance"]},
            ),
            "Decision Tree": (
                Pipeline([("m", DecisionTreeClassifier(random_state=rs))]),
                {"m__max_depth": [2, 3, 4, 5], "m__min_samples_leaf": [1, 5, 10]},
            ),
        }

    def _holdout_metrics(self, model: Any, X: pd.DataFrame, y: pd.Series, threshold: float = 0.5) -> dict:
        """Compute holdout metrics."""
        proba = model.predict_proba(X)[:, 1]
        pred = (proba >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()

        return {
            "roc_auc": float(roc_auc_score(y, proba)),
            "accuracy": float(accuracy_score(y, pred)),
            "precision": float(precision_score(y, pred, zero_division=0)),
            "recall_sensitivity": float(recall_score(y, pred)),
            "specificity": float(tn / (tn + fp)),
            "f1": float(f1_score(y, pred)),
            "brier": float(brier_score_loss(y, proba)),
            "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
        }

    def train(
        self,
        data_path: Path | str | None = None,
        model_path: Path | str | None = None,
        reports_dir: Path | str | None = None,
        only: list[str] | None = None,
    ) -> TrainingResult:
        """
        Run full model comparison and persist the best model.

        Returns:
            TrainingResult with selected model and comparison metrics.
        """
        # Load and split data
        df, info = self._data_service.load_dataset(data_path)
        X_train, X_test, y_train, y_test = self._data_service.split(df)

        cv = StratifiedKFold(5, shuffle=True, random_state=settings.random_state)

        rows = []
        fitted = {}

        for name, (pipe, grid) in self._candidates().items():
            if only and name not in only:
                continue

            gs = GridSearchCV(pipe, grid, cv=cv, scoring="roc_auc", n_jobs=-1)
            gs.fit(X_train, y_train)
            fitted[name] = gs.best_estimator_

            hold = self._holdout_metrics(gs.best_estimator_, X_test, y_test)

            row = {
                "model": name,
                "cv_roc_auc": float(gs.best_score_),
                "best_params": {k.split("__")[1]: v for k, v in gs.best_params_.items()},
                **{f"test_{k}": v for k, v in hold.items() if k != "confusion_matrix"},
                "test_confusion_matrix": hold["confusion_matrix"],
            }
            rows.append(row)

            log.info("%-20s cv_auc=%.3f test_auc=%.3f", name, gs.best_score_, hold["roc_auc"])

        # Select best model based on CV AUC (test set never influences choice)
        best = max(rows, key=lambda r: r["cv_roc_auc"])
        best_model = fitted[best["model"]]

        # Prepare reference values and ranges from training data
        reference = {
            c: float(X_train[c].median()) if c in settings.NUMERIC_FEATURES else int(X_train[c].mode()[0])
            for c in settings.FEATURE_NAMES
        }
        ranges = {
            c: [float(X_train[c].min()), float(X_train[c].max())]
            for c in settings.NUMERIC_FEATURES
        }

        # Build results
        results = {
            "dataset": {
                "raw_rows": info.raw_rows,
                "duplicates_removed": info.duplicate_rows,
                "unique_patients": info.unique_rows,
                "disease_prevalence": info.disease_prevalence,
                "train_rows": len(X_train),
                "test_rows": len(X_test),
            },
            "selected_model": best["model"],
            "selection_criterion": "5-fold CV ROC-AUC on training split",
            "comparison": sorted(rows, key=lambda r: -r["cv_roc_auc"]),
            "sklearn_version": sklearn.__version__,
        }

        # Save model artifact
        model_path = Path(model_path) if model_path else settings.model_path
        model_path.parent.mkdir(parents=True, exist_ok=True)

        artifact = {
            "pipeline": best_model,
            "model_name": best["model"],
            "feature_names": settings.FEATURE_NAMES,
            "reference": reference,
            "train_ranges": ranges,
            "threshold": settings.model_threshold,
            "metrics": best,
            "sklearn_version": sklearn.__version__,
        }
        joblib.dump(artifact, model_path)

        # Save reports
        reports_dir = Path(reports_dir) if reports_dir else settings.reports_dir
        reports_dir.mkdir(parents=True, exist_ok=True)

        (reports_dir / "metrics.json").write_text(json.dumps(results, indent=2))

        comparison_df = pd.DataFrame(results["comparison"]).drop(
            columns=["best_params", "test_confusion_matrix"]
        )
        comparison_df.to_csv(reports_dir / "model_comparison.csv", index=False)

        log.info("Selected model: %s (saved to %s)", best["model"], model_path)

        # Convert to TrainingResult
        best_metrics = ModelMetrics(
            cv_roc_auc=best["cv_roc_auc"],
            test_roc_auc=best["test_roc_auc"],
            test_accuracy=best["test_accuracy"],
            test_precision=best["test_precision"],
            test_recall_sensitivity=best["test_recall_sensitivity"],
            test_specificity=best["test_specificity"],
            test_f1=best["test_f1"],
            test_brier=best["test_brier"],
            confusion_matrix=best["test_confusion_matrix"],
        )

        return TrainingResult(
            selected_model=best["model"],
            selection_criterion=results["selection_criterion"],
            comparison=results["comparison"],
            dataset_info=results["dataset"],
            sklearn_version=sklearn.__version__,
            best_params=best["best_params"],
            metrics=best_metrics,
        )

    def evaluate_model(self, model_path: Path | str, data_path: Path | str | None = None) -> dict:
        """Evaluate a saved model on test data."""
        from .model_service import ModelService

        model_service = ModelService(model_path)
        model_service.load()

        df, _ = self._data_service.load_dataset(data_path)
        _, X_test, _, y_test = self._data_service.split(df)

        return self._holdout_metrics(model_service._pipeline, X_test, y_test)