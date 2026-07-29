"""
Shared Constants Module for Veridict Common Infrastructure.
Centralizes default page sizes, sort field names, and standard date formatting strings.
"""
from typing import Final

DEFAULT_PAGE: Final[int] = 1
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100

DEFAULT_SORT_FIELD: Final[str] = "created_at"
DEFAULT_SORT_ORDER: Final[str] = "DESC"

DATE_FORMAT: Final[str] = "%Y-%m-%d"
TIMESTAMP_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%SZ"
