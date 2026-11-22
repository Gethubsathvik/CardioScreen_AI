"""API package - FastAPI routes and app factory."""

from .app import create_app, app, get_model_service, set_model_service

__all__ = [
    "create_app",
    "app",
    "get_model_service",
    "set_model_service",
]