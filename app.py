"""Compatibility entry point: `uvicorn app:app` still works."""
from cardioscreen.api import app  # noqa: F401
