"""Custom validators for patient data."""

from __future__ import annotations

from typing import Any

from ..core.config import settings
from ..core.exceptions import ValidationError


def validate_patient_data(data: dict[str, Any]) -> dict[str, list[str]]:
    """Validate patient data against feature constraints. Returns dict of field -> errors."""
    errors = {}

    for feature_name in settings.FEATURE_NAMES:
        feature_config = settings.FEATURE_BY_NAME.get(feature_name)
        if not feature_config:
            continue

        value = data.get(feature_name)
        if value is None:
            errors.setdefault(feature_name, []).append("Field is required")
            continue

        # Type check
        if feature_config.kind == "numeric":
            if not isinstance(value, (int, float)):
                errors.setdefault(feature_name, []).append("Must be a number")
            elif feature_config.min is not None and value < feature_config.min:
                errors.setdefault(feature_name, []).append(f"Must be >= {feature_config.min}")
            elif feature_config.max is not None and value > feature_config.max:
                errors.setdefault(feature_name, []).append(f"Must be <= {feature_config.max}")
        else:
            # Categorical/binary
            allowed = set(feature_config.choices.keys())
            if value not in allowed:
                errors.setdefault(feature_name, []).append(f"Must be one of {sorted(allowed)}")

    return errors


def raise_if_errors(errors: dict[str, list[str]]) -> None:
    """Raise ValidationError if there are any errors."""
    if errors:
        raise ValidationError("Validation failed", field_errors=errors)