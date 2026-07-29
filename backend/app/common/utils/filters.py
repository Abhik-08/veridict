"""
Filter Utilities for Veridict Common Infrastructure.
Validates range boundaries and date filters.
"""
from datetime import datetime
from typing import Optional
from app.common.exceptions.validation import InvalidDateRangeException, InvalidFilterException


def validate_score_range(score_min: Optional[float] = None, score_max: Optional[float] = None) -> None:
    """Validates 0-5 numerical evaluation score range limits."""
    if score_min is not None and (score_min < 0.0 or score_min > 5.0):
        raise InvalidFilterException("Parameter 'score_min' must be between 0.0 and 5.0.")
    if score_max is not None and (score_max < 0.0 or score_max > 5.0):
        raise InvalidFilterException("Parameter 'score_max' must be between 0.0 and 5.0.")
    if score_min is not None and score_max is not None and score_min > score_max:
        raise InvalidFilterException("'score_min' cannot be greater than 'score_max'.")


def validate_confidence_range(confidence_min: Optional[float] = None, confidence_max: Optional[float] = None) -> None:
    """Validates 0-1 numerical confidence score range limits."""
    if confidence_min is not None and (confidence_min < 0.0 or confidence_min > 1.0):
        raise InvalidFilterException("Parameter 'confidence_min' must be between 0.0 and 1.0.")
    if confidence_max is not None and (confidence_max < 0.0 or confidence_max > 1.0):
        raise InvalidFilterException("Parameter 'confidence_max' must be between 0.0 and 1.0.")
    if confidence_min is not None and confidence_max is not None and confidence_min > confidence_max:
        raise InvalidFilterException("'confidence_min' cannot be greater than 'confidence_max'.")


def validate_date_range(date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> None:
    """Validates date range start and end boundaries."""
    if date_from is not None and date_to is not None and date_from > date_to:
        raise InvalidDateRangeException("'date_from' cannot be after 'date_to'.")
