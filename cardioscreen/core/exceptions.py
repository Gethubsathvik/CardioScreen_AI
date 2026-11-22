"""Custom exceptions for CardioScreen AI."""

from __future__ import annotations


class CardioScreenError(Exception):
    """Base exception for CardioScreen AI."""

    def __init__(self, message: str, code: str | None = None, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }


class ModelNotFoundError(CardioScreenError):
    """Raised when the trained model file is not found."""

    def __init__(self, path: str | None = None):
        message = f"Model not found at {path}" if path else "Model not found. Run training first."
        super().__init__(message, code="MODEL_NOT_FOUND", details={"path": path})


class ValidationError(CardioScreenError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field_errors: dict | None = None):
        super().__init__(message, code="VALIDATION_ERROR", details={"field_errors": field_errors or {}})


class DataError(CardioScreenError):
    """Raised when data loading or processing fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="DATA_ERROR", details=details)


class TrainingError(CardioScreenError):
    """Raised when model training fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="TRAINING_ERROR", details=details)


class PredictionError(CardioScreenError):
    """Raised when prediction fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="PREDICTION_ERROR", details=details)


class ConfigurationError(CardioScreenError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="CONFIGURATION_ERROR", details=details)