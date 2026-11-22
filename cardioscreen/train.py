"""Train all candidate models, pick the best, evaluate once on a held-out test set, save."""

from __future__ import annotations

import json
import warnings
import logging
from pathlib import Path

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

from . import config, data

log = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")


def candidates() -> dict[str, tuple[Pipeline, dict]]:
    """name -> (pipeline, param_grid). Scaling is inside the pipeline (no leakage)."""
    rs = config.RANDOM_STATE
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


def _holdout_metrics(model, X, y, threshold: float = 0.5) -> dict:
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
    data_path: Path | str = config.DATA_PATH,
    model_path: Path | str = config.MODEL_PATH,
    reports_dir: Path | str = config.REPORTS_DIR,
    only: list[str] | None = None,
) -> dict:
    """Run the full comparison and persist the winner. Returns the metrics dict."""
    df, info = data.load_dataset(data_path)
    X_train, X_test, y_train, y_test = data.split(df)
    cv = StratifiedKFold(5, shuffle=True, random_state=config.RANDOM_STATE)

    rows, fitted = [], {}
    for name, (pipe, grid) in candidates().items():
        if only and name not in only:
            continue
        gs = GridSearchCV(pipe, grid, cv=cv, scoring="roc_auc", n_jobs=-1)
        gs.fit(X_train, y_train)
        fitted[name] = gs.best_estimator_
        hold = _holdout_metrics(gs.best_estimator_, X_test, y_test)
        rows.append(
            {
                "model": name,
                "cv_roc_auc": float(gs.best_score_),
                "best_params": {k.split("__")[1]: v for k, v in gs.best_params_.items()},
                **{f"test_{k}": v for k, v in hold.items() if k != "confusion_matrix"},
                "test_confusion_matrix": hold["confusion_matrix"],
            }
        )
        log.info("%-20s cv_auc=%.3f test_auc=%.3f", name, gs.best_score_, hold["roc_auc"])

    # Selection uses cross-validation on the TRAIN split only; the test set is not used to choose.
    best = max(rows, key=lambda r: r["cv_roc_auc"])
    best_model = fitted[best["model"]]

    reference = {
        c: float(X_train[c].median()) if c in config.NUMERIC_FEATURES else int(X_train[c].mode()[0])
        for c in config.FEATURE_NAMES
    }
    ranges = {c: [float(X_train[c].min()), float(X_train[c].max())] for c in config.NUMERIC_FEATURES}
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

    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": best_model,
            "model_name": best["model"],
            "feature_names": config.FEATURE_NAMES,
            "reference": reference,
            "train_ranges": ranges,
            "threshold": 0.5,
            "metrics": best,
            "sklearn_version": sklearn.__version__,
        },
        model_path,
    )
    Path(reports_dir).mkdir(parents=True, exist_ok=True)
    (Path(reports_dir) / "metrics.json").write_text(json.dumps(results, indent=2))
    pd.DataFrame(results["comparison"]).drop(columns=["best_params", "test_confusion_matrix"]).to_csv(
        Path(reports_dir) / "model_comparison.csv", index=False
    )
    return results