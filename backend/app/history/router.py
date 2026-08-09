"""
FastAPI Router for Evaluation History Foundation (Milestone 6 Phase 3).
Provides production-grade REST API endpoints for evaluation history, search, pagination, filtering, statistics, and batch operations.
"""
from typing import Annotated, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.auth.schemas import AuthenticatedUser
from app.history.schemas import (
    HistoryItemCreate,
    HistoryItemResponse,
    EvaluationDetailResponse,
    BatchJobCreate,
    BatchHistoryResponse,
    BatchDetailResponse,
    DashboardStatistics,
    PaginatedResponse,
    HistoryFilterParams,
    AnalyticsFilterParams,
    AnalyticsStatistics,
)
from app.common.models.responses import SuccessResponse
from app.history.service import HistoryService
from app.common.exceptions.base import BaseAppException
from app.history.exceptions import HistoryDomainError

router = APIRouter(prefix="/history", tags=["History"])

DbSession = Annotated[Session, Depends(get_db)]
AuthUser = Annotated[AuthenticatedUser, Depends(get_current_user)]


# ---------------------------------------------------------
# Evaluation History Endpoints
# ---------------------------------------------------------

@router.get("", response_model=PaginatedResponse[HistoryItemResponse])
def get_history_paginated(
    db: DbSession,
    current_user: AuthUser,
    params: Annotated[HistoryFilterParams, Query()],
):
    """
    Retrieves filtered, sorted, and paginated evaluation history records for the authenticated user.
    """
    try:
        return HistoryService.get_history_paginated(db=db, user_id=current_user.id, params=params)
    except (HistoryDomainError, BaseAppException) as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)


@router.get("/recent", response_model=List[HistoryItemResponse])
def get_recent_history(
    db: DbSession,
    current_user: AuthUser,
    limit: Annotated[int, Query(ge=1, le=50, description="Number of recent evaluations to fetch")] = 10,
):
    """Retrieves the latest evaluations for the user dashboard overview."""
    return HistoryService.get_recent_evaluations(db, current_user.id, limit=limit)


@router.get("/stats", response_model=DashboardStatistics)
def get_history_stats(
    db: DbSession,
    current_user: AuthUser,
):
    """Calculates comprehensive aggregate statistics for the user dashboard."""
    return HistoryService.get_dashboard_statistics(db, current_user.id)


@router.get("/dashboard/statistics", response_model=DashboardStatistics, include_in_schema=False)
def get_dashboard_statistics_legacy(
    db: DbSession,
    current_user: AuthUser,
):
    """Legacy route alias for dashboard statistics."""
    return HistoryService.get_dashboard_statistics(db, current_user.id)


@router.get("/analytics", response_model=AnalyticsStatistics)
def get_history_analytics(
    db: DbSession,
    current_user: AuthUser,
    params: Annotated[AnalyticsFilterParams, Query()],
):
    """
    Calculates detailed evaluation scoring analytics, dimension averages, hallucination frequency,
    and quality trends over time for the authenticated user's dashboard.
    """
    try:
        return HistoryService.get_analytics(db=db, user_id=current_user.id, params=params)
    except (HistoryDomainError, BaseAppException) as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)


# ---------------------------------------------------------
# Batch Job Endpoints
# ---------------------------------------------------------

@router.get("/batches", response_model=List[BatchHistoryResponse])
def list_batches(
    db: DbSession,
    current_user: AuthUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """Lists batch evaluation tasks owned by the authenticated user."""
    return HistoryService.list_user_batches(db, current_user.id, skip=skip, limit=limit)


@router.get("/batches/{batch_id}", response_model=BatchDetailResponse)
def get_batch_detail(
    batch_id: UUID,
    db: DbSession,
    current_user: AuthUser,
):
    """Retrieves detailed batch task metadata, linked evaluations, and verdict distribution."""
    try:
        return HistoryService.get_batch_detail(db, batch_id, current_user.id)
    except (HistoryDomainError, BaseAppException) as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)


@router.delete("/batches/{batch_id}", response_model=SuccessResponse[dict])
def delete_batch(
    batch_id: UUID,
    db: DbSession,
    current_user: AuthUser,
):
    """Cascade deletes a batch evaluation task and all associated evaluations."""
    try:
        HistoryService.delete_batch_job(db, batch_id, current_user.id)
        return SuccessResponse[dict](data={"batch_id": str(batch_id)}, message="Batch job deleted successfully.")
    except (HistoryDomainError, BaseAppException) as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)


@router.get("/batch/{batch_id}", response_model=BatchHistoryResponse, include_in_schema=False)
def get_batch_job_legacy(
    batch_id: UUID,
    db: DbSession,
    current_user: AuthUser,
):
    """Legacy route alias for batch task status."""
    try:
        return HistoryService.get_batch_job(db, batch_id, current_user.id)
    except (HistoryDomainError, BaseAppException) as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)


# ---------------------------------------------------------
# Single Item Detail & Mutation Endpoints
# ---------------------------------------------------------

@router.post("/batch", response_model=BatchHistoryResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
@router.post("/batches", response_model=BatchHistoryResponse, status_code=status.HTTP_201_CREATED)
def record_batch_job(
    data: BatchJobCreate,
    db: DbSession,
    current_user: AuthUser,
):
    """Registers a new batch evaluation task for the authenticated user."""
    return HistoryService.create_batch_job(db, current_user.id, data)


@router.post("/evaluations", response_model=EvaluationDetailResponse, status_code=status.HTTP_201_CREATED)
def record_evaluation(
    data: HistoryItemCreate,
    db: DbSession,
    current_user: AuthUser,
):
    """Records a new evaluation history item for the authenticated user."""
    return HistoryService.create_evaluation(db, current_user.id, data)


@router.get("/evaluations", response_model=List[HistoryItemResponse], include_in_schema=False)
def list_evaluations_legacy(
    db: DbSession,
    current_user: AuthUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    verdict: Annotated[Optional[str], Query()] = None,
    source_type: Annotated[Optional[str], Query()] = None,
):
    """Legacy route alias for unpaginated evaluations list."""
    return HistoryService.list_user_history(db, current_user.id, skip=skip, limit=limit, verdict=verdict, source_type=source_type)


@router.get("/evaluations/{evaluation_id}", response_model=EvaluationDetailResponse, include_in_schema=False)
@router.get("/{evaluation_id}", response_model=EvaluationDetailResponse)
def get_evaluation(
    evaluation_id: UUID,
    db: DbSession,
    current_user: AuthUser,
):
    """Retrieves full evaluation details including evidence and raw judge JSON payload."""
    try:
        return HistoryService.get_evaluation_detail(db, evaluation_id, current_user.id)
    except (HistoryDomainError, BaseAppException) as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)


@router.delete("/evaluations/{evaluation_id}", response_model=SuccessResponse[dict], include_in_schema=False)
@router.delete("/{evaluation_id}", response_model=SuccessResponse[dict])
def delete_evaluation(
    evaluation_id: UUID,
    db: DbSession,
    current_user: AuthUser,
):
    """Deletes a specific evaluation record owned by the authenticated user."""
    try:
        HistoryService.delete_evaluation_item(db, evaluation_id, current_user.id)
        return SuccessResponse[dict](data={"evaluation_id": str(evaluation_id)}, message="Evaluation deleted successfully.")
    except (HistoryDomainError, BaseAppException) as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
