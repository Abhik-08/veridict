"""
Service module for Evaluation History Foundation.
Implements business logic orchestration for evaluation history operations.
"""
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from sqlalchemy.orm import Session

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
    HistoryFilterParams,
    AnalyticsFilterParams,
    AnalyticsStatistics,
)
from app.history.constants import EvaluationSource, HistoryStatus, EvaluationVerdict
from app.history.events import HistoryEvents
from app.history.mapper import HistoryMapper
from app.history.repository import HistoryRepository
from app.history.validators import HistoryQueryValidator
from app.history.exceptions import HistoryNotFoundError, BatchJobNotFoundError


class HistoryService:
    """
    Business service layer managing history persistence, retrieval, and statistics.
    Contains zero direct SQL queries, delegating data access to HistoryRepository.
    Uses HistoryMapper for pure object transformations when raw evaluation payloads are provided.
    Dispatches domain events via HistoryEvents for decoupled lifecycle notifications.
    """

    @staticmethod
    def create_evaluation(
        db: Session,
        user_id: UUID,
        data: Union[HistoryItemCreate, Dict[str, Any]],
        source_type: Union[EvaluationSource, str] = EvaluationSource.SINGLE,
        batch_job_id: Optional[UUID] = None,
    ) -> Evaluation:
        """Records a new evaluation history item, transforming raw dicts via HistoryMapper if needed."""
        source_str = source_type.value if isinstance(source_type, EvaluationSource) else str(source_type)
        if not isinstance(data, HistoryItemCreate):
            data = HistoryMapper.to_history_item_create(data, source_type=source_str, batch_job_id=batch_job_id)

        evaluation = HistoryRepository.create_evaluation(db, user_id, data)

        # Dispatch domain event
        HistoryEvents.evaluation_saved(
            user_id=user_id,
            evaluation_id=evaluation.id,
            overall_score=evaluation.overall_score,
            verdict=evaluation.verdict,
        )
        return evaluation

    @staticmethod
    def get_evaluation_detail(db: Session, evaluation_id: UUID, user_id: UUID) -> Evaluation:
        """Fetches detailed evaluation record for a given user. Raises 404 if not found."""
        evaluation = HistoryRepository.get_evaluation(db, evaluation_id, user_id)
        if not evaluation:
            raise HistoryNotFoundError(f"Evaluation '{evaluation_id}' not found.")
        HistoryEvents.evaluation_viewed(user_id=user_id, evaluation_id=evaluation_id)
        return evaluation

    @staticmethod
    def get_history_paginated(
        db: Session,
        user_id: UUID,
        params: HistoryFilterParams,
    ) -> PaginatedResponse[HistoryItemResponse]:
        """Validates query params and retrieves filtered, sorted, and paginated evaluations."""
        # 1. Validate inputs before query execution
        HistoryQueryValidator.validate_pagination(params.page, params.page_size)
        HistoryQueryValidator.validate_sort_params(params.sort_by, params.sort_order)
        HistoryQueryValidator.validate_range_params(params.score_min, params.score_max)
        HistoryQueryValidator.validate_date_range(params.date_from, params.date_to)

        # 2. Execute repository query
        items, total_items = HistoryRepository.get_history_paginated(
            db=db,
            user_id=user_id,
            params=params,
        )

        # 3. Construct pagination metadata using common utility
        from app.common.utils.pagination import build_pagination_metadata
        pagination = build_pagination_metadata(params.page, params.page_size, total_items)

        # 4. Map ORM models to Pydantic responses
        mapped_items = [HistoryItemResponse.model_validate(item) for item in items]
        return PaginatedResponse[HistoryItemResponse](items=mapped_items, pagination=pagination)

    @staticmethod
    def get_recent_evaluations(db: Session, user_id: UUID, limit: int = 10) -> List[HistoryItemResponse]:
        """Retrieves top N latest evaluations for dashboard overview."""
        items = HistoryRepository.get_recent_history(db, user_id, limit=limit)
        return [HistoryItemResponse.model_validate(item) for item in items]

    @staticmethod
    def list_user_history(
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        verdict: Optional[Union[EvaluationVerdict, str]] = None,
        source_type: Optional[Union[EvaluationSource, str]] = None,
    ) -> List[Evaluation]:
        """Legacy helper for listing user evaluation history records."""
        verdict_str = verdict.value if isinstance(verdict, EvaluationVerdict) else verdict
        source_str = source_type.value if isinstance(source_type, EvaluationSource) else source_type
        return HistoryRepository.get_history(db, user_id, skip=skip, limit=limit, verdict=verdict_str, source_type=source_str)

    @staticmethod
    def delete_evaluation_item(db: Session, evaluation_id: UUID, user_id: UUID) -> bool:
        """Deletes an evaluation history item."""
        success = HistoryRepository.delete_evaluation(db, evaluation_id, user_id)
        if not success:
            raise HistoryNotFoundError(f"Evaluation '{evaluation_id}' not found.")
        HistoryEvents.evaluation_deleted(user_id=user_id, evaluation_id=evaluation_id)
        return True

    @staticmethod
    def create_batch_job(
        db: Session,
        user_id: UUID,
        data: Union[BatchJobCreate, Dict[str, Any]],
    ) -> BatchJob:
        """Registers a new batch evaluation task."""
        if not isinstance(data, BatchJobCreate):
            status_val = data.get("status", HistoryStatus.PROCESSING.value)
            if isinstance(status_val, HistoryStatus):
                status_val = status_val.value
            data = HistoryMapper.to_batch_job_create(
                filename=data.get("filename", "unknown.csv"),
                total_items=int(data.get("total_items", 0)),
                status=status_val,
            )
        batch = HistoryRepository.create_batch(db, user_id, data)

        # Dispatch domain event
        HistoryEvents.batch_created(
            user_id=user_id,
            batch_id=batch.id,
            total_items=batch.total_items,
            filename=batch.filename,
        )
        return batch

    @staticmethod
    def get_batch_job(db: Session, batch_id: UUID, user_id: UUID) -> BatchJob:
        """Fetches a batch job record. Raises 404 if not found."""
        batch = HistoryRepository.get_batch(db, batch_id, user_id)
        if not batch:
            raise BatchJobNotFoundError(f"Batch job '{batch_id}' not found.")
        HistoryEvents.batch_viewed(user_id=user_id, batch_id=batch_id)
        return batch

    @staticmethod
    def get_batch_detail(db: Session, batch_id: UUID, user_id: UUID) -> BatchDetailResponse:
        """Fetches comprehensive batch job details with linked evaluation items and verdict statistics."""
        batch = HistoryService.get_batch_job(db, batch_id, user_id)
        evals = HistoryRepository.get_history(db, user_id=user_id, source_type="BATCH", limit=1000)
        linked_evals = [e for e in evals if e.batch_job_id == batch_id]

        pass_cnt = sum(1 for e in linked_evals if e.verdict == EvaluationVerdict.PASS.value)
        needs_cnt = sum(1 for e in linked_evals if e.verdict == EvaluationVerdict.NEEDS_IMPROVEMENT.value)
        fail_cnt = sum(1 for e in linked_evals if e.verdict == EvaluationVerdict.FAIL.value)

        avg_score = round(sum(e.overall_score for e in linked_evals) / len(linked_evals), 2) if linked_evals else 0.0

        items_mapped = [HistoryItemResponse.model_validate(e) for e in linked_evals]
        return BatchDetailResponse(
            id=batch.id,
            user_id=batch.user_id,
            filename=batch.filename,
            status=batch.status,
            total_items=batch.total_items,
            completed_items=batch.completed_items,
            average_score=avg_score,
            created_at=batch.created_at,
            updated_at=batch.updated_at,
            evaluations=items_mapped,
            verdict_distribution={
                "PASS": pass_cnt,
                "NEEDS_IMPROVEMENT": needs_cnt,
                "FAIL": fail_cnt,
            },
        )

    @staticmethod
    def list_user_batches(
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> List[BatchHistoryResponse]:
        """Lists batch jobs owned by the authenticated user with aggregate score summaries."""
        batches = HistoryRepository.get_batches(db, user_id, skip=skip, limit=limit)
        res = []
        for b in batches:
            res.append(
                BatchHistoryResponse(
                    id=b.id,
                    user_id=b.user_id,
                    filename=b.filename,
                    status=b.status,
                    total_items=b.total_items,
                    completed_items=b.completed_items,
                    created_at=b.created_at,
                    updated_at=b.updated_at,
                )
            )
        return res

    @staticmethod
    def delete_batch_job(db: Session, batch_id: UUID, user_id: UUID) -> bool:
        """Deletes a batch job and all associated evaluations."""
        success = HistoryRepository.delete_batch(db, batch_id, user_id)
        if not success:
            raise BatchJobNotFoundError(f"Batch job '{batch_id}' not found.")
        HistoryEvents.batch_deleted(user_id=user_id, batch_id=batch_id)
        return True

    @staticmethod
    def get_dashboard_statistics(db: Session, user_id: UUID) -> DashboardStatistics:
        """Calculates dashboard statistics for the user."""
        HistoryEvents.statistics_requested(user_id=user_id)
        return HistoryRepository.dashboard_statistics(db, user_id)

    @staticmethod
    def get_analytics(db: Session, user_id: UUID, params: AnalyticsFilterParams) -> AnalyticsStatistics:
        """Calculates detailed analytics and score trends for the user scoring dashboard."""
        HistoryEvents.statistics_requested(user_id=user_id)
        return HistoryRepository.analytics_statistics(db, user_id, params)
