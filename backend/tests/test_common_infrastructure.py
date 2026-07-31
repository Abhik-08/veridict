"""
Unit tests for Veridict Common Infrastructure (app.common).
Verifies models, responses, pagination, sorting, filters, exceptions, and utility functions.
"""
import pytest
from app.common import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    PaginationMetadata,
    PaginatedResponse,
    SuccessResponse,
    ErrorResponse,
    BaseAppException,
    NotFoundException,
    InvalidPaginationException,
    InvalidSortFieldException,
    InvalidDateRangeException,
    InvalidFilterException,
)
from app.common.utils import (
    calculate_offset,
    calculate_total_pages,
    build_pagination_metadata,
    validate_and_normalize_sort,
    validate_score_range,
    validate_date_range,
    utcnow,
    format_iso_timestamp,
)


def test_common_constants():
    """Verifies default values in common constants."""
    assert DEFAULT_PAGE == 1
    assert DEFAULT_PAGE_SIZE == 20
    assert MAX_PAGE_SIZE == 100


def test_pagination_utilities_and_models():
    """Verifies pagination offset calculation, total pages, and metadata builder."""
    assert calculate_offset(1, 20) == 0
    assert calculate_offset(2, 20) == 20
    assert calculate_total_pages(45, 20) == 3

    meta = build_pagination_metadata(page=2, page_size=20, total_items=45)
    assert meta.page == 2
    assert meta.total_pages == 3
    assert meta.has_next is True
    assert meta.has_previous is True

    response = PaginatedResponse[str](items=["item1", "item2"], pagination=meta)
    assert len(response.items) == 2
    assert response.pagination.total_items == 45


def test_response_envelopes():
    """Verifies SuccessResponse and ErrorResponse models."""
    succ = SuccessResponse[dict](data={"result": "ok"})
    assert succ.success is True
    assert succ.data["result"] == "ok"

    err = ErrorResponse(error="NOT_FOUND", message="Item missing")
    assert err.success is False
    assert err.error == "NOT_FOUND"
    assert err.timestamp is not None


def test_sorting_and_filtering_utilities():
    """Verifies sort field normalization and filter boundary validation."""
    field, order = validate_and_normalize_sort("created_at", "asc", {"created_at", "score"})
    assert field == "created_at"
    assert order == "ASC"

    with pytest.raises(InvalidSortFieldException):
        validate_and_normalize_sort("unknown_col", "ASC", {"created_at"})

    validate_score_range(1.0, 4.5)
    with pytest.raises(InvalidFilterException):
        validate_score_range(4.5, 1.0)


def test_exception_hierarchy():
    """Verifies BaseAppException status codes and details."""
    exc = NotFoundException("Resource missing")
    assert exc.status_code == 404
    assert exc.error_code == "NOT_FOUND"

    base_exc = BaseAppException("Generic error", status_code=400)
    assert base_exc.status_code == 400
