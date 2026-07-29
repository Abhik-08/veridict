"""
HTTP Status Exception Classes for Veridict Common Infrastructure.
"""
from typing import Any, Dict, Optional
from fastapi import status
from app.common.exceptions.base import BaseAppException


class NotFoundException(BaseAppException):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str = "Requested resource not found.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details,
        )


class UnauthorizedException(BaseAppException):
    """Raised when authentication fails or Bearer token is missing."""
    def __init__(self, message: str = "Authentication required.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            details=details,
        )


class ForbiddenException(BaseAppException):
    """Raised when access control permissions block an authenticated user."""
    def __init__(self, message: str = "Access forbidden.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            details=details,
        )


class ConflictException(BaseAppException):
    """Raised when request conflicts with existing database state."""
    def __init__(self, message: str = "Resource conflict occurred.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            details=details,
        )
