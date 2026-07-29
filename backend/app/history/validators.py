"""
History Query Validators Module for Veridict.
Extends app.common.utils for history query parameter validation.
"""
from datetime import datetime
from typing import Optional

from app.history.exceptions import InvalidHistoryFilterError
from app.common.utils.pagination import calculate_offset
from app.common.utils.sorting import validate_and_normalize_sort
from app.common.utils.filters import validate_score_range, validate_confidence_range, validate_date_range

ALLOWED_SORT_FIELDS = {"created_at", "overall_score", "confidence", "question", "verdict"}


class HistoryQueryValidator:
    """Validator for evaluation history query parameters."""

    @staticmethod
    def validate_pagination(page: int, page_size: int) -> None:
        """Validates page and page_size parameters."""
        try:
            calculate_offset(page, page_size)
        except Exception as err:
            raise InvalidHistoryFilterError(str(err))

    @staticmethod
    def validate_sort_params(sort_by: str, sort_order: str) -> None:
        """Validates sort_by column name and sort_order direction."""
        try:
            validate_and_normalize_sort(sort_by, sort_order, ALLOWED_SORT_FIELDS)
        except Exception as err:
            raise InvalidHistoryFilterError(str(err))

    @staticmethod
    def validate_range_params(
        score_min: Optional[float] = None,
        score_max: Optional[float] = None,
        confidence_min: Optional[float] = None,
        confidence_max: Optional[float] = None,
    ) -> None:
        """Validates score and confidence range boundaries."""
        try:
            validate_score_range(score_min, score_max)
            validate_confidence_range(confidence_min, confidence_max)
        except Exception as err:
            raise InvalidHistoryFilterError(str(err))

    @staticmethod
    def validate_date_range(date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> None:
        """Validates date range bounds."""
        try:
            validate_date_range(date_from, date_to)
        except Exception as err:
            raise InvalidHistoryFilterError(str(err))
