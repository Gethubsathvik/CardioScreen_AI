"""API routes package."""

from .health import router as health_router
from .model_info import router as model_info_router
from .features import router as features_router
from .predict import router as predict_router

__all__ = [
    "health_router",
    "model_info_router",
    "features_router",
    "predict_router",
]