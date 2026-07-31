"""
Repository module for Evaluation History Foundation.
Handles pure SQLAlchemy database interactions with strict user ownership scoping.
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.history.models import Evaluation, BatchJob
from app.history.schemas import HistoryItemCreate, BatchJobCreate, DashboardStatistics, HistoryFilterParams
from app.history.constants import EvaluationVerdict


class HistoryRepository:
    """
    Data access layer for Evaluation and BatchJob records.
    Every query enforces strict user_id scoping for data isolation and ownership security.
    """

    @staticmethod
    def create_evaluation(db: Session, user_id: UUID, data: HistoryItemCreate) -> Evaluation:
        """Persists a new Evaluation history item for the authenticated user."""
        evaluation = Evaluation(
            user_id=user_id,
            question=data.question,
            ai_response=data.ai_response,
            reference_answer=data.reference_answer,
            retrieved_evidence=data.retrieved_evidence,
            evaluation_result=data.evaluation_result,
            overall_score=data.overall_score,
            verdict=data.verdict,
            source_type=data.source_type,
            batch_job_id=data.batch_job_id,
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return evaluation

    @staticmethod
    def get_evaluation(db: Session, evaluation_id: UUID, user_id: UUID) -> Optional[Evaluation]:
        """Retrieves a specific evaluation item owned by the authenticated user."""
        return (
            db.query(Evaluation)
            .filter(Evaluation.id == evaluation_id, Evaluation.user_id == user_id)
            .first()
        )

    @staticmethod
    def get_history(
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        verdict: Optional[str] = None,
        source_type: Optional[str] = None,
    ) -> List[Evaluation]:
        """Retrieves paginated evaluation history records scoped to user_id."""
        query = db.query(Evaluation).filter(Evaluation.user_id == user_id)

        if verdict and verdict != "ALL":
            query = query.filter(Evaluation.verdict == verdict)
        if source_type:
            query = query.filter(Evaluation.source_type == source_type)

        return query.order_by(Evaluation.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_recent_history(db: Session, user_id: UUID, limit: int = 10) -> List[Evaluation]:
        """Retrieves the latest evaluations for the user dashboard."""
        return (
            db.query(Evaluation)
            .filter(Evaluation.user_id == user_id)
            .order_by(Evaluation.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_history_paginated(
        db: Session,
        user_id: UUID,
        params: HistoryFilterParams,
    ) -> Tuple[List[Evaluation], int]:
        """Retrieves filtered, sorted, and paginated evaluations alongside total count."""
        query = db.query(Evaluation).filter(Evaluation.user_id == user_id)

        # 1. Apply Search Filter across text columns
        if params.search and params.search.strip():
            term = f"%{params.search.strip()}%"
            query = query.filter(
                or_(
                    Evaluation.question.ilike(term),
                    Evaluation.ai_response.ilike(term),
                    Evaluation.reference_answer.ilike(term),
                    Evaluation.verdict.ilike(term),
                )
            )

        # 2. Category & Attribute Filters
        if params.verdict and params.verdict != "ALL":
            query = query.filter(Evaluation.verdict == params.verdict.upper())
        if params.source_type and params.source_type != "ALL":
            query = query.filter(Evaluation.source_type == params.source_type.upper())

        # 3. Numeric & Date Ranges
        if params.score_min is not None:
            query = query.filter(Evaluation.overall_score >= params.score_min)
        if params.score_max is not None:
            query = query.filter(Evaluation.overall_score <= params.score_max)
        if params.date_from is not None:
            query = query.filter(Evaluation.created_at >= params.date_from)
        if params.date_to is not None:
            query = query.filter(Evaluation.created_at <= params.date_to)

        # Total count before pagination
        total_items = query.count()

        # 4. Apply Sorting
        sort_column = getattr(Evaluation, params.sort_by, Evaluation.created_at)
        if params.sort_order.upper() == "ASC":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # 5. Apply Pagination Offset & Limit
        offset = (params.page - 1) * params.page_size
        items = query.offset(offset).limit(params.page_size).all()

        return items, total_items

    @staticmethod
    def delete_evaluation(db: Session, evaluation_id: UUID, user_id: UUID) -> bool:
        """Deletes an evaluation history item owned by the authenticated user."""
        evaluation = HistoryRepository.get_evaluation(db, evaluation_id, user_id)
        if not evaluation:
            return False
        db.delete(evaluation)
        db.commit()
        return True

    @staticmethod
    def create_batch(db: Session, user_id: UUID, data: BatchJobCreate) -> BatchJob:
        """Persists a new BatchJob task for the authenticated user."""
        batch_job = BatchJob(
            user_id=user_id,
            filename=data.filename,
            total_items=data.total_items,
            status=data.status,
        )
        db.add(batch_job)
        db.commit()
        db.refresh(batch_job)
        return batch_job

    @staticmethod
    def get_batch(db: Session, batch_id: UUID, user_id: UUID) -> Optional[BatchJob]:
        """Retrieves a specific BatchJob task owned by the authenticated user."""
        return (
            db.query(BatchJob)
            .filter(BatchJob.id == batch_id, BatchJob.user_id == user_id)
            .first()
        )

    @staticmethod
    def get_batches(db: Session, user_id: UUID, skip: int = 0, limit: int = 50) -> List[BatchJob]:
        """Retrieves paginated BatchJob tasks owned by the authenticated user."""
        return (
            db.query(BatchJob)
            .filter(BatchJob.user_id == user_id)
            .order_by(BatchJob.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def delete_batch(db: Session, batch_id: UUID, user_id: UUID) -> bool:
        """Cascade deletes a BatchJob task and all associated evaluations owned by user_id."""
        batch = HistoryRepository.get_batch(db, batch_id, user_id)
        if not batch:
            return False
        db.delete(batch)
        db.commit()
        return True

    @staticmethod
    def dashboard_statistics(db: Session, user_id: UUID) -> DashboardStatistics:
        """Calculates comprehensive evaluation statistics for user dashboard."""
        evals_query = db.query(Evaluation).filter(Evaluation.user_id == user_id)
        batch_query = db.query(BatchJob).filter(BatchJob.user_id == user_id)

        total_evaluations = evals_query.count()
        total_batch_jobs = batch_query.count()

        if total_evaluations == 0:
            return DashboardStatistics(
                total_evaluations=0,
                total_batch_jobs=total_batch_jobs,
                pass_count=0,
                needs_improvement_count=0,
                fail_count=0,
                pass_percentage=0.0,
                average_score=0.0,
                average_batch_size=0.0,
                recent_activity_count=0,
            )

        pass_count = evals_query.filter(Evaluation.verdict == EvaluationVerdict.PASS.value).count()
        needs_improvement_count = evals_query.filter(Evaluation.verdict == EvaluationVerdict.NEEDS_IMPROVEMENT.value).count()
        fail_count = evals_query.filter(Evaluation.verdict == EvaluationVerdict.FAIL.value).count()

        pass_percentage = round((pass_count / total_evaluations) * 100.0, 2)
        fail_percentage = round((fail_count / total_evaluations) * 100.0, 2)
        needs_improvement_percentage = round((needs_improvement_count / total_evaluations) * 100.0, 2)

        avg_score_res = db.query(func.avg(Evaluation.overall_score)).filter(Evaluation.user_id == user_id).scalar()
        max_score_res = db.query(func.max(Evaluation.overall_score)).filter(Evaluation.user_id == user_id).scalar()
        min_score_res = db.query(func.min(Evaluation.overall_score)).filter(Evaluation.user_id == user_id).scalar()

        average_score = round(float(avg_score_res), 2) if avg_score_res is not None else 0.0
        highest_score = round(float(max_score_res), 2) if max_score_res is not None else 0.0
        lowest_score = round(float(min_score_res), 2) if min_score_res is not None else 0.0

        avg_batch_res = db.query(func.avg(BatchJob.total_items)).filter(BatchJob.user_id == user_id).scalar()
        average_batch_size = round(float(avg_batch_res), 2) if avg_batch_res is not None else 0.0

        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_activity_count = evals_query.filter(Evaluation.created_at >= cutoff).count()

        most_recent_eval = db.query(func.max(Evaluation.created_at)).filter(Evaluation.user_id == user_id).scalar()

        return DashboardStatistics(
            total_evaluations=total_evaluations,
            total_batch_jobs=total_batch_jobs,
            pass_count=pass_count,
            needs_improvement_count=needs_improvement_count,
            fail_count=fail_count,
            pass_percentage=pass_percentage,
            fail_percentage=fail_percentage,
            needs_improvement_percentage=needs_improvement_percentage,
            average_score=average_score,
            highest_score=highest_score,
            lowest_score=lowest_score,
            average_batch_size=average_batch_size,
            recent_activity_count=recent_activity_count,
            most_recent_evaluation=most_recent_eval,
        )
