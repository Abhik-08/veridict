"""
Base Exception Hierarchy for Veridict Common Infrastructure.
"""
from typing import Any, Dict, Optional
from fastapi import status


class BaseAppException(Exception):
    """
    Root domain exception class for the entire application codebase.
    Contains HTTP status code, machine-readable error code, message, and optional details dict.
    """
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "BAD_REQUEST",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
