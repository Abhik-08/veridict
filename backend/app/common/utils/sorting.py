"""
Sorting Utilities for Veridict Common Infrastructure.
Validates and normalizes sort column names and direction strings.
"""
from typing import Set, Tuple
from app.common.constants import DEFAULT_SORT_FIELD, DEFAULT_SORT_ORDER
from app.common.exceptions.validation import InvalidSortFieldException
from app.common.types import SortOrderEnum


def validate_and_normalize_sort(
    sort_by: str = DEFAULT_SORT_FIELD,
    sort_order: str = DEFAULT_SORT_ORDER,
    allowed_fields: Set[str] = None,
) -> Tuple[str, str]:
    """
    Validates sort_by column name against allowed_fields set and normalizes sort_order to 'ASC' or 'DESC'.
    """
    if allowed_fields and sort_by not in allowed_fields:
        allowed_str = ", ".join(sorted(allowed_fields))
        raise InvalidSortFieldException(
            f"Invalid sort field '{sort_by}'. Allowed fields: {allowed_str}."
        )

    order_upper = sort_order.upper() if sort_order else DEFAULT_SORT_ORDER
    if order_upper not in {SortOrderEnum.ASC.value, SortOrderEnum.DESC.value}:
        raise InvalidSortFieldException("Parameter 'sort_order' must be 'ASC' or 'DESC'.")

    return sort_by, order_upper
