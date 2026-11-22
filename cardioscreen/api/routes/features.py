"""Feature specification routes."""

from fastapi import APIRouter

from ...models.schemas import FeatureSpec

router = APIRouter(tags=["Features"])


@router.get("/api/features", response_model=list[FeatureSpec])
def features():
    """Get feature specifications for dynamic form generation."""
    from ... import get_model_service
    service = get_model_service()
    return service.get_feature_spec()