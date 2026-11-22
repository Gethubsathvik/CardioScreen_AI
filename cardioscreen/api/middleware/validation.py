"""Request validation middleware."""

from __future__ import annotations

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ...core.exceptions import ValidationError
from ...core.logging import get_logger

log = get_logger(__name__)


class ValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for request validation and error handling."""

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
            return response
        except ValidationError as e:
            log.warning("Validation error: %s", e.message)
            return JSONResponse(
                status_code=422,
                content=e.to_dict(),
            )
        except Exception as e:
            log.exception("Unhandled error: %s", e)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {},
                },
            )