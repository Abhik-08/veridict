"""
History Module Package Initialization.
Evaluation History Foundation for Veridict backend.
"""
from app.history.models import Evaluation, BatchJob
from app.history.schemas import (
    HistoryItemCreate,
    HistoryItemResponse,
    EvaluationDetailResponse,
    BatchJobCreate,
    BatchHistoryResponse,
    BatchDetailResponse,
    DashboardStatistics,
    PaginationMetadata,
    PaginatedResponse,
)
from app.history.constants import (
    EvaluationSource,
    HistoryStatus,
    EvaluationVerdict,
    SortOrder,
    DateRangeFilter,
)
from app.history.events import HistoryEvents
from app.history.exceptions import (
    HistoryDomainError,
    HistoryNotFoundError,
    BatchJobNotFoundError,
    HistoryAccessDeniedError,
    InvalidHistoryFilterError,
)
from app.history.validators import HistoryQueryValidator
from app.history.mapper import HistoryMapper
from app.history.repository import HistoryRepository
from app.history.service import HistoryService
from app.history.router import router

__all__ = [
    "Evaluation",
    "BatchJob",
    "HistoryItemCreate",
    "HistoryItemResponse",
    "EvaluationDetailResponse",
    "BatchJobCreate",
    "BatchHistoryResponse",
    "BatchDetailResponse",
    "DashboardStatistics",
    "PaginationMetadata",
    "PaginatedResponse",
    "EvaluationSource",
    "HistoryStatus",
    "EvaluationVerdict",
    "SortOrder",
    "DateRangeFilter",
    "HistoryEvents",
    "HistoryDomainError",
    "HistoryNotFoundError",
    "BatchJobNotFoundError",
    "HistoryAccessDeniedError",
    "InvalidHistoryFilterError",
    "HistoryQueryValidator",
    "HistoryMapper",
    "HistoryRepository",
    "HistoryService",
    "router",
]
