"""Model info routes."""

from fastapi import APIRouter, HTTPException

from ...models.schemas import ModelInfo

router = APIRouter(tags=["Model"])


@router.get("/api/model", response_model=ModelInfo)
def model_info():
    """Get model metadata."""
    from ... import get_model_service
    service = get_model_service()
    try:
        return service.info()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))