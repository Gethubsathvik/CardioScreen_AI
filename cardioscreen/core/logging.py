"""Structured logging configuration."""

from __future__ import annotations

import logging
import sys
from typing import Any

from ..core.config import settings


def setup_logging(level: str | None = None, format_string: str | None = None) -> None:
    """Configure application logging."""
    log_level = level or settings.log_level
    log_format = format_string or settings.log_format

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(log_format))

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given module name."""
    return logging.getLogger(name)


class StructuredLogger:
    """Wrapper for structured logging with context."""

    def __init__(self, logger: logging.Logger, context: dict[str, Any] | None = None):
        self._logger = logger
        self._context = context or {}

    def bind(self, **kwargs: Any) -> "StructuredLogger":
        """Create a new logger with additional context."""
        new_context = {**self._context, **kwargs}
        return StructuredLogger(self._logger, new_context)

    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        extra = {**self._context, **kwargs}
        self._logger.log(level, message, extra=extra)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, message, **kwargs)


def get_structured_logger(name: str, **context: Any) -> StructuredLogger:
    """Get a structured logger with optional context."""
    return StructuredLogger(logging.getLogger(name), context)