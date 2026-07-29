"""
Shared Response Envelopes for Veridict Common Infrastructure.
Provides standard SuccessResponse[T] and ErrorResponse models for API consistency.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success API response envelope."""
    success: bool = Field(True, description="Success status flag")
    message: str = Field("Request processed successfully.", description="User-facing status summary")
    data: T = Field(..., description="Response payload body")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional response metadata envelope")


class ErrorResponse(BaseModel):
    """Standard error API response envelope."""
    success: bool = Field(False, description="Success status flag")
    error: str = Field(..., description="Machine-readable error type identifier")
    message: str = Field(..., description="Human-readable error explanation")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional context or validation details")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO UTC timestamp when the error occurred"
    )
