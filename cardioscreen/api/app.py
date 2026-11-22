"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .routes import health_router, model_info_router, features_router, predict_router
from .middleware import ValidationMiddleware
from ..core.config import settings
from ..core.logging import setup_logging
from ..services.model_service import ModelService


# Global model service instance
_model_service: ModelService | None = None


def get_model_service() -> ModelService:
    """Get the global model service instance."""
    global _model_service
    if _model_service is None:
        _model_service = ModelService().load()
    return _model_service


def set_model_service(service: ModelService) -> None:
    """Set the global model service instance (for testing)."""
    global _model_service
    _model_service = service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    setup_logging()
    try:
        get_model_service()
    except FileNotFoundError:
        # Model not found - will be loaded on first request or via training
        pass
    yield
    # Shutdown
    global _model_service
    _model_service = None


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.disclaimer,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware
    app.add_middleware(ValidationMiddleware)

    # Routes
    app.include_router(health_router)
    app.include_router(model_info_router)
    app.include_router(features_router)
    app.include_router(predict_router)

    # Static files - serve web UI
    static_dir = settings.static_dir

    @app.get("/", include_in_schema=False)
    async def index():
        """Serve the web UI."""
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"message": "Web UI not found. Run `python -m cardioscreen serve` after building."}

    return app


# Create the app instance for uvicorn
app = create_app()