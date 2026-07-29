"""
General Validation Utilities for Veridict Common Infrastructure.
"""
from typing import Any, List, Optional
from app.common.exceptions.validation import ValidationException


def ensure_non_empty_string(val: Optional[str], field_name: str = "field") -> str:
    """Ensures a string argument is not None or whitespace only."""
    if not val or not val.strip():
        raise ValidationException(f"Parameter '{field_name}' must be a non-empty string.")
    return val.strip()


def ensure_positive_integer(val: int, field_name: str = "field") -> int:
    """Ensures an integer argument is positive."""
    if val <= 0:
        raise ValidationException(f"Parameter '{field_name}' must be a positive integer.")
    return val
