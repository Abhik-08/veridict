"""
Validation Exception Classes for Veridict Common Infrastructure.
"""
from typing import Any, Dict, Optional
from fastapi import status
from app.common.exceptions.base import BaseAppException


class ValidationException(BaseAppException):
    """Base exception for input validation errors."""
    def __init__(self, message: str = "Input validation failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class InvalidPaginationException(ValidationException):
    """Raised when page or page_size parameters violate boundaries."""
    def __init__(self, message: str = "Invalid pagination parameters."):
        super().__init__(message=message, details={"type": "pagination"})


class InvalidDateRangeException(ValidationException):
    """Raised when date_from exceeds date_to or format is invalid."""
    def __init__(self, message: str = "Invalid date range parameters."):
        super().__init__(message=message, details={"type": "date_range"})


class InvalidSortFieldException(ValidationException):
    """Raised when sort_by column is not in allowed fields list."""
    def __init__(self, message: str = "Invalid sort field parameter."):
        super().__init__(message=message, details={"type": "sort"})


class InvalidFilterException(ValidationException):
    """Raised when filter query parameter combinations are invalid."""
    def __init__(self, message: str = "Invalid filter query parameters."):
        super().__init__(message=message, details={"type": "filter"})
