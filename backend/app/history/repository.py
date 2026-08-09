"""
Repository module for Evaluation History Foundation.
Handles pure SQLAlchemy database interactions with strict user ownership scoping.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.history.models import Evaluation, BatchJob
from app.history.schemas import (
    HistoryItemCreate,
    BatchJobCreate,
    DashboardStatistics,
    HistoryFilterParams,
    AnalyticsFilterParams,
    AnalyticsStatistics,
    VerdictDistribution,
    AverageDimensionScores,
    HallucinationMetrics,
    QualityTrendPoint,
    AvailableFilterMetadata,
)
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

    @staticmethod
    @staticmethod
    def _extract_available_filters(all_user_evals: List[Evaluation]) -> AvailableFilterMetadata:
        """Extracts unique models, source types, and verdicts across user history."""
        models_set = set()
        for e in all_user_evals:
            result_json = e.evaluation_result or {}
            model_name = (
                result_json.get("relevance_evaluation", {}).get("model_used")
                or result_json.get("model_used")
            )
            if model_name:
                models_set.add(model_name)

        return AvailableFilterMetadata(
            available_models=sorted(models_set),
            available_source_types=sorted({e.source_type for e in all_user_evals if e.source_type}),
            available_verdicts=sorted({e.verdict for e in all_user_evals if e.verdict}),
        )

    @staticmethod
    def _calculate_verdict_distribution(filtered_evals: List[Evaluation], total_evaluations: int) -> VerdictDistribution:
        """Calculates PASS, NEEDS_IMPROVEMENT, FAIL counts and percentages."""
        if total_evaluations == 0:
            return VerdictDistribution()

        pass_count = sum(1 for e in filtered_evals if e.verdict == EvaluationVerdict.PASS.value)
        needs_improvement_count = sum(1 for e in filtered_evals if e.verdict == EvaluationVerdict.NEEDS_IMPROVEMENT.value)
        fail_count = sum(1 for e in filtered_evals if e.verdict == EvaluationVerdict.FAIL.value)

        return VerdictDistribution(
            pass_count=pass_count,
            needs_improvement_count=needs_improvement_count,
            fail_count=fail_count,
            pass_percentage=round((pass_count / total_evaluations) * 100.0, 2),
            needs_improvement_percentage=round((needs_improvement_count / total_evaluations) * 100.0, 2),
            fail_percentage=round((fail_count / total_evaluations) * 100.0, 2),
        )

    @staticmethod
    def _is_numeric(val: Any) -> bool:
        """Returns True if val is a number (int or float) and not a boolean."""
        return isinstance(val, (int, float)) and not isinstance(val, bool)

    @staticmethod
    def _extract_score(result_json: dict, key_name: str) -> Optional[float]:
        """
        Extracts numeric score for a dimension (relevance, accuracy, completeness, hallucination)
        from various evaluation payload JSON structures across single and batch runs.
        """
        if not isinstance(result_json, dict):
            return None

        # 1. Top-level score check (e.g. result_json["relevance_score"] or result_json["relevance"])
        for top_key in (f"{key_name}_score", key_name):
            if HistoryRepository._is_numeric(val := result_json.get(top_key)):
                return float(val)

        # 2. Nested dictionary check (e.g. result_json["relevance_evaluation"] or result_json["relevance"])
        for parent_key in (f"{key_name}_evaluation", key_name):
            parent_dict = result_json.get(parent_key)
            if isinstance(parent_dict, dict):
                for sub_key in (f"{key_name}_score", "score", "value"):
                    if HistoryRepository._is_numeric(val := parent_dict.get(sub_key)):
                        return float(val)

        return None

    @staticmethod
    def _calculate_dimension_averages(filtered_evals: List[Evaluation]) -> AverageDimensionScores:
        """Calculates mean scores for relevance, accuracy, completeness, and overall score."""
        overall_scores = [float(e.overall_score) for e in filtered_evals if e.overall_score is not None]

        results = [e.evaluation_result or {} for e in filtered_evals]
        rel_scores = [s for r in results if (s := HistoryRepository._extract_score(r, "relevance")) is not None]
        acc_scores = [s for r in results if (s := HistoryRepository._extract_score(r, "accuracy")) is not None]
        comp_scores = [s for r in results if (s := HistoryRepository._extract_score(r, "completeness")) is not None]

        return AverageDimensionScores(
            average_relevance=round(sum(rel_scores) / len(rel_scores), 2) if rel_scores else 0.0,
            average_accuracy=round(sum(acc_scores) / len(acc_scores), 2) if acc_scores else 0.0,
            average_completeness=round(sum(comp_scores) / len(comp_scores), 2) if comp_scores else 0.0,
            average_overall_score=round(sum(overall_scores) / len(overall_scores), 2) if overall_scores else 0.0,
        )

    @staticmethod
    def _calculate_hallucination_metrics(filtered_evals: List[Evaluation]) -> HallucinationMetrics:
        """
        Calculates hallucination rate, evaluable vs insufficient evidence counts.
        Note: Items with INSUFFICIENT_EVIDENCE status, missing evidence, or 0.0 score are
        excluded from evaluable hallucination counts and counted under insufficient_evidence_count.
        """
        insufficient_evidence_count = 0
        hal_scores = []

        for e in filtered_evals:
            result_json = e.evaluation_result or {}
            hal_eval = result_json.get("hallucination_evaluation") or {}
            status_str = hal_eval.get("status") if isinstance(hal_eval, dict) else result_json.get("status")
            evidence_source = result_json.get("evidence_source")

            h_score = HistoryRepository._extract_score(result_json, "hallucination")

            if (
                status_str == "INSUFFICIENT_EVIDENCE"
                or evidence_source == "NO_EVIDENCE"
                or h_score is None
                or h_score < 0.01
            ):
                insufficient_evidence_count += 1
            elif 1.0 <= h_score <= 5.0:
                hal_scores.append(h_score)

        evaluable_count = len(hal_scores)
        hallucinated_count = sum(1 for s in hal_scores if s < 4.0)
        grounded_count = evaluable_count - hallucinated_count

        return HallucinationMetrics(
            evaluable_count=evaluable_count,
            insufficient_evidence_count=insufficient_evidence_count,
            hallucinated_count=hallucinated_count,
            grounded_count=grounded_count,
            hallucination_rate_percentage=round((hallucinated_count / evaluable_count) * 100.0, 2) if evaluable_count > 0 else 0.0,
            average_hallucination_score=round(sum(hal_scores) / len(hal_scores), 2) if hal_scores else 0.0,
        )

    @staticmethod
    def _calculate_quality_trends(filtered_evals: List[Evaluation]) -> List[QualityTrendPoint]:
        """Groups evaluations by date YYYY-MM-DD for time-series quality trends."""
        trends_map: dict[str, list[Evaluation]] = {}
        for e in filtered_evals:
            date_key = e.created_at.strftime("%Y-%m-%d") if e.created_at else "Unknown"
            if date_key not in trends_map:
                trends_map[date_key] = []
            trends_map[date_key].append(e)

        quality_trends = []
        for date_key in sorted(trends_map.keys()):
            items = trends_map[date_key]
            d_scores = [item.overall_score for item in items if item.overall_score is not None]
            d_avg = round(sum(d_scores) / len(d_scores), 2) if d_scores else 0.0
            d_pass = sum(1 for item in items if item.verdict == EvaluationVerdict.PASS.value)
            d_needs = sum(1 for item in items if item.verdict == EvaluationVerdict.NEEDS_IMPROVEMENT.value)
            d_fail = sum(1 for item in items if item.verdict == EvaluationVerdict.FAIL.value)

            quality_trends.append(
                QualityTrendPoint(
                    date=date_key,
                    count=len(items),
                    average_score=d_avg,
                    pass_count=d_pass,
                    needs_improvement_count=d_needs,
                    fail_count=d_fail,
                )
            )
        return quality_trends

    @staticmethod
    def analytics_statistics(db: Session, user_id: UUID, params: AnalyticsFilterParams) -> AnalyticsStatistics:
        """
        Calculates comprehensive, filtered evaluation analytics for the user's dashboard.
        Strictly scoped to user_id for multi-tenant security.
        """
        all_user_evals = db.query(Evaluation).filter(Evaluation.user_id == user_id).all()
        available_filters = HistoryRepository._extract_available_filters(all_user_evals)

        query = db.query(Evaluation).filter(Evaluation.user_id == user_id)
        if params.date_from:
            query = query.filter(Evaluation.created_at >= params.date_from)
        if params.date_to:
            query = query.filter(Evaluation.created_at <= params.date_to)
        if params.source_type and params.source_type.upper() != "ALL":
            query = query.filter(Evaluation.source_type == params.source_type.upper())
        if params.verdict and params.verdict.upper() != "ALL":
            query = query.filter(Evaluation.verdict == params.verdict.upper())

        filtered_evals = query.order_by(Evaluation.created_at.asc()).all()

        if params.model and params.model.strip() and params.model.upper() != "ALL":
            target_model = params.model.strip().lower()
            filtered_evals = [
                e for e in filtered_evals
                if (
                    (e.evaluation_result or {}).get("relevance_evaluation", {}).get("model_used", "").lower() == target_model
                    or (e.evaluation_result or {}).get("model_used", "").lower() == target_model
                )
            ]

        total_evaluations = len(filtered_evals)
        if total_evaluations == 0:
            return AnalyticsStatistics(
                total_evaluations=0,
                verdict_distribution=VerdictDistribution(),
                average_scores=AverageDimensionScores(),
                hallucination_metrics=HallucinationMetrics(),
                quality_trends=[],
                available_filters=available_filters,
            )

        return AnalyticsStatistics(
            total_evaluations=total_evaluations,
            verdict_distribution=HistoryRepository._calculate_verdict_distribution(filtered_evals, total_evaluations),
            average_scores=HistoryRepository._calculate_dimension_averages(filtered_evals),
            hallucination_metrics=HistoryRepository._calculate_hallucination_metrics(filtered_evals),
            quality_trends=HistoryRepository._calculate_quality_trends(filtered_evals),
            available_filters=available_filters,
        )
