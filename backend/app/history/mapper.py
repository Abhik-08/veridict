"""
History Mapper Module for Veridict.
Pure transformation layer converting evaluation pipeline results into persistence payload objects.
Ensures zero coupling between EvaluationService and database persistence schemas.
"""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from app.history.schemas import HistoryItemCreate, BatchJobCreate
from app.history.constants import EvaluationSource, HistoryStatus, EvaluationVerdict


class HistoryMapper:
    """
    Pure data transformation mapper.
    Transforms raw or structured evaluation pipeline output dictionaries into HistoryItemCreate payloads.
    Contains zero database logic, zero HTTP context, and zero side effects.
    """

    @staticmethod
    def _extract_evidence(evaluation_data: Dict[str, Any]) -> Optional[Union[List[Any], Dict[str, Any]]]:
        """Normalizes retrieved evidence from various input payload keys."""
        evidence_raw = (
            evaluation_data.get("retrieved_evidence")
            or evaluation_data.get("retrieved_chunks")
            or evaluation_data.get("evidence_chunks")
            or evaluation_data.get("evidence_text")
            or evaluation_data.get("context")
        )
        if isinstance(evidence_raw, (list, dict)):
            return evidence_raw
        if isinstance(evidence_raw, str) and evidence_raw.strip():
            return [{"text": evidence_raw}]
        return None

    @staticmethod
    def _extract_scores_and_verdict(evaluation_data: Dict[str, Any]) -> tuple[float, Optional[float], str]:
        """Extracts numerical overall score, confidence, and verdict string."""
        verdict_obj = evaluation_data.get("verdict_evaluation") or {}
        default_verdict = EvaluationVerdict.NEEDS_IMPROVEMENT.value

        if isinstance(verdict_obj, dict) and verdict_obj:
            score_val = evaluation_data.get("overall_score")
            score_raw = score_val if score_val is not None else verdict_obj.get("overall_score", evaluation_data.get("score", 0.0))

            conf_val = evaluation_data.get("confidence")
            confidence_raw = conf_val if conf_val is not None else verdict_obj.get("confidence")

            verdict_raw = evaluation_data.get("verdict") or verdict_obj.get("verdict") or default_verdict
        else:
            score_raw = evaluation_data.get("overall_score", evaluation_data.get("score", 0.0))
            confidence_raw = evaluation_data.get("confidence")
            verdict_raw = evaluation_data.get("verdict", default_verdict)

        overall_score = float(score_raw)
        confidence = float(confidence_raw) if confidence_raw is not None else None
        verdict = str(verdict_raw).upper()
        return overall_score, confidence, verdict

    @staticmethod
    def to_history_item_create(
        evaluation_data: Dict[str, Any],
        source_type: Union[EvaluationSource, str] = EvaluationSource.SINGLE,
        batch_job_id: Optional[UUID] = None,
    ) -> HistoryItemCreate:
        """
        Transforms raw evaluation output dictionary into a validated HistoryItemCreate payload.

        Handles key normalization across single and batch evaluation payloads.
        """
        source_str = source_type.value if isinstance(source_type, EvaluationSource) else str(source_type)
        question = evaluation_data.get("question", "")
        ai_response = evaluation_data.get("ai_response") or evaluation_data.get("answer") or ""
        reference_answer = evaluation_data.get("reference_answer") or evaluation_data.get("reference")

        retrieved_evidence = HistoryMapper._extract_evidence(evaluation_data)
        eval_result = evaluation_data.get("evaluation_result") or evaluation_data.get("verdict_evaluation") or evaluation_data
        overall_score, confidence, verdict = HistoryMapper._extract_scores_and_verdict(evaluation_data)

        return HistoryItemCreate(
            question=question,
            ai_response=ai_response,
            reference_answer=reference_answer,
            retrieved_evidence=retrieved_evidence,
            evaluation_result=eval_result,
            overall_score=overall_score,
            confidence=confidence,
            verdict=verdict,
            source_type=source_str,
            batch_job_id=batch_job_id,
        )

    @staticmethod
    def to_batch_job_create(
        filename: str,
        total_items: int = 0,
        status: Union[HistoryStatus, str] = HistoryStatus.PROCESSING,
    ) -> BatchJobCreate:
        """Transforms batch job creation parameters into a BatchJobCreate payload."""
        status_str = status.value if isinstance(status, HistoryStatus) else str(status)
        return BatchJobCreate(
            filename=filename,
            total_items=total_items,
            status=status_str,
        )
