import json

import pandas as pd
import pytest
from pydantic import ValidationError

from cardioscreen import config, data
from cardioscreen.predictor import ModelNotFoundError, Predictor, risk_band
from cardioscreen.schemas import PatientFeatures
from cardioscreen.train import train

HEALTHY = dict(age=41, sex=0, cp=1, trestbps=130, chol=204, fbs=0, restecg=0, thalach=172,
               exang=0, oldpeak=1.4, slope=2, ca=0, thal=2)
SICK = dict(age=67, sex=1, cp=0, trestbps=160, chol=286, fbs=0, restecg=0, thalach=108,
            exang=1, oldpeak=1.5, slope=1, ca=3, thal=2)


@pytest.fixture(scope="module")
def trained(tmp_path_factory):
    d = tmp_path_factory.mktemp("out")
    res = train(model_path=d / "m.joblib", reports_dir=d, only=["Logistic Regression", "Random Forest"])
    return res, Predictor.load(d / "m.joblib"), d


# ---- data -----------------------------------------------------------------
def test_duplicates_removed_before_split():
    df, info = data.load_dataset()
    assert info.raw_rows == 1025 and info.unique_rows == 302 and not df.duplicated().any()


def test_no_patient_in_both_train_and_test():
    df, _ = data.load_dataset()
    Xtr, Xte, _, _ = data.split(df)
    assert len(pd.merge(Xtr, Xte, how="inner")) == 0


def test_disease_label_is_inverted_target():
    df, _ = data.load_dataset()
    assert (df["disease"] == 1 - df["target"]).all()
    # sanity: exercise-induced angina must be MORE common among disease cases
    assert df[df.disease == 1].exang.mean() > df[df.disease == 0].exang.mean()


def test_validate_rejects_bad_data():
    df = pd.read_csv(config.DATA_PATH)
    with pytest.raises(data.DataValidationError):
        data.validate(df.drop(columns="chol"))
    bad = df.copy(); bad.loc[0, "cp"] = 9
    with pytest.raises(data.DataValidationError):
        data.validate(bad)


# ---- schema ---------------------------------------------------------------
@pytest.mark.parametrize("field,value", [("age", 200), ("sex", 2), ("cp", 4), ("oldpeak", -1), ("chol", 5)])
def test_schema_rejects_out_of_range(field, value):
    with pytest.raises(ValidationError):
        PatientFeatures(**{**HEALTHY, field: value})


def test_schema_rejects_unknown_and_missing_fields():
    with pytest.raises(ValidationError):
        PatientFeatures(**{**HEALTHY, "foo": 1})
    with pytest.raises(ValidationError):
        PatientFeatures(**{k: v for k, v in HEALTHY.items() if k != "age"})


# ---- training / predictor ---------------------------------------------------
def test_training_beats_chance_and_writes_artifacts(trained):
    res, _, d = trained
    best = res["comparison"][0]
    assert best["test_roc_auc"] > 0.8 and best["cv_roc_auc"] > 0.8
    assert (d / "metrics.json").exists() and (d / "model_comparison.csv").exists()
    assert json.loads((d / "metrics.json").read_text())["dataset"]["unique_patients"] == 302


def test_selection_uses_cv_not_test(trained):
    res, _, _ = trained
    assert res["selected_model"] == max(res["comparison"], key=lambda r: r["cv_roc_auc"])["model"]


def test_sick_patient_scores_higher_than_healthy(trained):
    _, p, _ = trained
    sick, healthy = p.predict(PatientFeatures(**SICK)), p.predict(PatientFeatures(**HEALTHY))
    assert sick.disease_probability > healthy.disease_probability
    assert sick.prediction == 1 and healthy.prediction == 0


def test_prediction_shape_and_explanations(trained):
    _, p, _ = trained
    r = p.predict(PatientFeatures(**SICK))
    assert 0 <= r.disease_probability <= 1 and r.risk_band in {"low", "moderate", "high"}
    assert len(r.contributions) == 5 and r.disclaimer
    assert abs(r.contributions[0].effect) >= abs(r.contributions[-1].effect)


def test_out_of_range_input_is_flagged(trained):
    _, p, _ = trained
    r = p.predict(PatientFeatures(**{**HEALTHY, "chol": 650}))
    assert any("chol" in w for w in r.warnings)


def test_batch_matches_single(trained):
    _, p, _ = trained
    pts = [PatientFeatures(**HEALTHY), PatientFeatures(**SICK)]
    batch = p.predict_many(pts)
    assert [b.disease_probability for b in batch] == [p.predict(x).disease_probability for x in pts]


def test_risk_bands():
    assert (risk_band(0.1), risk_band(0.5), risk_band(0.9), risk_band(1.0)) == ("low", "moderate", "high", "high")


def test_missing_model_gives_clear_error(tmp_path):
    with pytest.raises(ModelNotFoundError):
        Predictor.load(tmp_path / "nope.joblib")
