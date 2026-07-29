"""
Business Rule Exception Classes for Veridict Common Infrastructure.
"""
from typing import Any, Dict, Optional
from fastapi import status
from app.common.exceptions.base import BaseAppException


class BusinessRuleException(BaseAppException):
    """Raised when a request violates domain business rules."""
    def __init__(self, message: str = "Business rule violation occurred.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="BUSINESS_RULE_VIOLATION",
            details=details,
        )
