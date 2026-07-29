"""
Shared Pagination Models for Veridict Common Infrastructure.
Reusable generic pagination wrappers for all API endpoints.
"""
from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMetadata(BaseModel):
    """Reusable pagination metadata model across APIs."""
    page: int = Field(..., description="Current 1-based page index")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total matching items count")
    total_pages: int = Field(..., description="Total available pages")
    has_next: bool = Field(..., description="True if next page exists")
    has_previous: bool = Field(..., description="True if previous page exists")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic reusable paginated response envelope."""
    items: List[T] = Field(default_factory=list)
    pagination: PaginationMetadata
