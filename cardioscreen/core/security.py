"""Security utilities (API keys, rate limiting - future use)."""

from __future__ import annotations

from functools import wraps
from typing import Callable

from ..core.config import settings
from ..core.exceptions import CardioScreenError


class SecurityError(CardioScreenError):
    """Security-related errors."""

    def __init__(self, message: str, code: str = "SECURITY_ERROR"):
        super().__init__(message, code=code)


def require_api_key(func: Callable) -> Callable:
    """Decorator to require API key (future implementation)."""
    if not settings.api_key_enabled:
        return func

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # TODO: Implement API key validation
        return await func(*args, **kwargs)

    return wrapper


def rate_limit(requests: int | None = None, window: int | None = None) -> Callable:
    """Decorator for rate limiting (future implementation)."""
    if not settings.rate_limit_enabled:
        def decorator(func: Callable) -> Callable:
            return func
        return decorator

    max_requests = requests or settings.rate_limit_requests
    window_seconds = window or settings.rate_limit_window

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # TODO: Implement rate limiting with Redis/in-memory store
            return await func(*args, **kwargs)
        return wrapper

    return decorator


def hash_password(password: str) -> str:
    """Hash a password using bcrypt (future use)."""
    # TODO: Implement with passlib
    raise NotImplementedError("Password hashing not yet implemented")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash (future use)."""
    # TODO: Implement with passlib
    raise NotImplementedError("Password verification not yet implemented")