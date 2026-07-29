"""
History Exceptions Module for Veridict.
Extends app.common.exceptions base hierarchy for evaluation history domain errors.
"""
from fastapi import status
from app.common.exceptions.base import BaseAppException
from app.common.exceptions.http import NotFoundException, ForbiddenException
from app.common.exceptions.validation import InvalidFilterException


class HistoryDomainError(BaseAppException):
    """Base domain exception for evaluation history module."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message=message, status_code=status_code, error_code="HISTORY_ERROR")


class HistoryNotFoundError(NotFoundException):
    """Raised when an evaluation record is not found or owned by another user."""
    def __init__(self, message: str = "Evaluation record not found."):
        super().__init__(message=message)


class BatchJobNotFoundError(NotFoundException):
    """Raised when a batch job record is not found or owned by another user."""
    def __init__(self, message: str = "Batch job record not found."):
        super().__init__(message=message)


class HistoryAccessDeniedError(ForbiddenException):
    """Raised when unauthorized access to history resources occurs."""
    def __init__(self, message: str = "Access denied to history resource."):
        super().__init__(message=message)


class InvalidHistoryFilterError(InvalidFilterException):
    """Raised when request query filter or pagination parameters are invalid."""
    def __init__(self, message: str = "Invalid history filter query parameters."):
        super().__init__(message=message)
