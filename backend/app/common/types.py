"""
Shared Types Module for Veridict Common Infrastructure.
Defines reusable type aliases, tuples, and enums across all backend packages.
"""
from enum import Enum
from typing import Annotated, Optional, Tuple, TypeAlias
from uuid import UUID
from pydantic import Field

UUIDType: TypeAlias = UUID
PageNumber: TypeAlias = Annotated[int, Field(ge=1, description="1-based page number")]
PageSize: TypeAlias = Annotated[int, Field(ge=1, le=100, description="Items per page")]

DateRange: TypeAlias = Tuple[Optional[str], Optional[str]]
ScoreRange: TypeAlias = Tuple[Optional[float], Optional[float]]


class SortOrderEnum(str, Enum):
    """Standard sort order directions."""
    ASC = "ASC"
    DESC = "DESC"
