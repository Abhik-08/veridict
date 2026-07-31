"""
Common Package Initialization for Veridict Shared Infrastructure.
Exposes constants, types, models, exceptions, and utilities.
"""
from app.common.constants import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    DEFAULT_SORT_FIELD,
    DEFAULT_SORT_ORDER,
    DATE_FORMAT,
    TIMESTAMP_FORMAT,
)
from app.common.types import (
    UUIDType,
    SortOrderEnum,
    PageNumber,
    PageSize,
    DateRange,
    ScoreRange,
)
from app.common.models import (
    RequestMetadata,
    ResponseMetadata,
    PaginationMetadata,
    PaginatedResponse,
    SuccessResponse,
    ErrorResponse,
)
from app.common.exceptions import (
    BaseAppException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
    ValidationException,
    InvalidPaginationException,
    InvalidDateRangeException,
    InvalidSortFieldException,
    InvalidFilterException,
    BusinessRuleException,
)

__all__ = [
    "DEFAULT_PAGE",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "DEFAULT_SORT_FIELD",
    "DEFAULT_SORT_ORDER",
    "DATE_FORMAT",
    "TIMESTAMP_FORMAT",
    "UUIDType",
    "SortOrderEnum",
    "PageNumber",
    "PageSize",
    "DateRange",
    "ScoreRange",
    "RequestMetadata",
    "ResponseMetadata",
    "PaginationMetadata",
    "PaginatedResponse",
    "SuccessResponse",
    "ErrorResponse",
    "BaseAppException",
    "NotFoundException",
    "UnauthorizedException",
    "ForbiddenException",
    "ConflictException",
    "ValidationException",
    "InvalidPaginationException",
    "InvalidDateRangeException",
    "InvalidSortFieldException",
    "InvalidFilterException",
    "BusinessRuleException",
]
