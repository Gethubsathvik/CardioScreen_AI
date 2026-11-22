"""Prediction routes."""

from fastapi import APIRouter, HTTPException

from ...models.schemas import PatientFeatures, Prediction, BatchRequest, BatchResponse

router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=Prediction)
def predict(patient: PatientFeatures, explain: bool = True):
    """Single patient prediction with explanation."""
    from ... import get_model_service
    service = get_model_service()
    try:
        return service.predict(patient, explain=explain)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/predict/batch", response_model=BatchResponse)
def predict_batch(req: BatchRequest):
    """Batch prediction (no explanations for performance)."""
    from ... import get_model_service
    service = get_model_service()
    try:
        return service.predict_batch(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))