"""Health check routes."""

from fastapi import APIRouter

from ...models.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    from ... import get_model_service
    service = get_model_service()
    health = service.health_check()
    return HealthResponse(**health)