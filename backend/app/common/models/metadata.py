"""
Shared Metadata Models for Veridict Common Infrastructure.
"""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class RequestMetadata(BaseModel):
    """Metadata detailing incoming HTTP request context."""
    request_id: Optional[str] = Field(None, description="Correlation UUID for request tracing")
    client_ip: Optional[str] = Field(None, description="Originating client IP address")


class ResponseMetadata(BaseModel):
    """Metadata detailing API execution metrics."""
    execution_time_ms: Optional[float] = Field(None, description="Request execution duration in milliseconds")
    extra: Dict[str, Any] = Field(default_factory=dict, description="Additional contextual metadata")
