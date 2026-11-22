"""FastAPI app: JSON API + single-page web UI."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from . import __version__, config
from .predictor import ModelNotFoundError, Predictor
from .schemas import BatchRequest, BatchResponse, PatientFeatures, Prediction

STATIC = Path(__file__).resolve().parent.parent / "static"
state: dict[str, Predictor] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        state["p"] = Predictor.load()
    except ModelNotFoundError:
        # First run convenience: train once (takes ~15 s) instead of failing.
        from .train import train

        train()
        state["p"] = Predictor.load()
    yield
    state.clear()


app = FastAPI(
    title="CardioScreen AI",
    version=__version__,
    description=config.DISCLAIMER,
    lifespan=lifespan,
)


def _model() -> Predictor:
    if "p" not in state:
        raise HTTPException(503, "Model not loaded")
    return state["p"]


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": "p" in state, "version": __version__}


@app.get("/api/features")
def features():
    """Field metadata used by the web form."""
    return config.feature_spec()


@app.get("/api/model")
def model_info():
    return _model().info()


@app.post("/predict", response_model=Prediction)
def predict(patient: PatientFeatures, explain: bool = True):
    return _model().predict(patient, explain=explain)


@app.post("/predict/batch", response_model=BatchResponse)
def predict_batch(req: BatchRequest):
    preds = _model().predict_many(req.patients)
    return BatchResponse(count=len(preds), predictions=preds)
