"""
Pagination Utilities for Veridict Common Infrastructure.
Provides standard pagination calculations and metadata builders.
"""
import math
from app.common.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.common.models.pagination import PaginationMetadata
from app.common.exceptions.validation import InvalidPaginationException


def calculate_offset(page: int = DEFAULT_PAGE, page_size: int = DEFAULT_PAGE_SIZE) -> int:
    """Calculates SQL LIMIT/OFFSET offset from 1-based page index."""
    if page < 1:
        raise InvalidPaginationException("Parameter 'page' must be greater than or equal to 1.")
    if page_size < 1 or page_size > MAX_PAGE_SIZE:
        raise InvalidPaginationException(f"Parameter 'page_size' must be between 1 and {MAX_PAGE_SIZE}.")
    return (page - 1) * page_size


def calculate_total_pages(total_items: int, page_size: int) -> int:
    """Calculates total available pages from total matching items count."""
    if total_items <= 0 or page_size <= 0:
        return 0
    return math.ceil(total_items / page_size)


def build_pagination_metadata(page: int, page_size: int, total_items: int) -> PaginationMetadata:
    """Constructs a validated PaginationMetadata object."""
    total_pages = calculate_total_pages(total_items, page_size)
    return PaginationMetadata(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=(page < total_pages),
        has_previous=(page > 1 and total_pages > 0),
    )
