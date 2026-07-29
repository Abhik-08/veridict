"""
History Constants and Enums Module for Veridict.
Centralized definitions for evaluation source types, status states, verdicts, date ranges, and sorting choices.
Replaces magic string literals across the codebase for improved maintainability and type safety.
"""
from enum import Enum


class EvaluationSource(str, Enum):
    """Source origin for evaluation records."""
    SINGLE = "SINGLE"
    BATCH = "BATCH"


class HistoryStatus(str, Enum):
    """Processing status for batch jobs and asynchronous evaluation tasks."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EvaluationVerdict(str, Enum):
    """Standardized AI judgment verdicts."""
    PASS = "PASS"
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"
    FAIL = "FAIL"


class SortOrder(str, Enum):
    """Sort direction options for query pagination."""
    ASC = "ASC"
    DESC = "DESC"


class DateRangeFilter(str, Enum):
    """Preset time range filters for evaluation history queries."""
    TODAY = "TODAY"
    LAST_7_DAYS = "LAST_7_DAYS"
    LAST_30_DAYS = "LAST_30_DAYS"
    ALL_TIME = "ALL_TIME"
