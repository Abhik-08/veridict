"""
Veridict Batch Statistics Service.

Computes summary metrics, average dimension scores, verdict counts,
and processing duration for dataset batch evaluation jobs.
"""

from typing import Any
from app.schemas.batch_evaluation import BatchItemEvaluationResult, BatchProgress


class BatchStatisticsService:
    """Computes comprehensive metrics and summary statistics for batch evaluation jobs."""

    @staticmethod
    def calculate_statistics(
        items: list[BatchItemEvaluationResult],
        elapsed_seconds: float = 0.0,
        gemini_calls: int = 0,
    ) -> dict[str, Any]:
        """
        Compute batch metrics dictionary.

        Args:
            items: List of evaluated item results.
            elapsed_seconds: Total processing duration in seconds.
            gemini_calls: Number of Gemini LLM API requests made.

        Returns:
            dict[str, Any]: Dictionary containing aggregate scores and counts.
        """
        total_items = len(items)
        if total_items == 0:
            return {
                "total_items": 0,
                "pass_count": 0,
                "needs_improvement_count": 0,
                "fail_count": 0,
                "pass_rate_percent": 0.0,
                "avg_relevance": 0.0,
                "avg_accuracy": 0.0,
                "avg_hallucination": 0.0,
                "avg_completeness": 0.0,
                "avg_overall_score": 0.0,
                "avg_confidence": 0.0,
                "elapsed_seconds": round(elapsed_seconds, 2),
                "gemini_calls": gemini_calls,
            }

        completed_items = [i for i in items if i.status == "COMPLETED"]
        pass_count = sum(1 for i in items if i.verdict == "PASS")
        imp_count = sum(1 for i in items if i.verdict == "NEEDS_IMPROVEMENT")
        fail_count = sum(1 for i in items if i.verdict == "FAIL" or i.status == "FAILED")

        pass_rate = round((pass_count / total_items) * 100.0, 1)

        rel_scores = [i.relevance_score for i in completed_items if i.relevance_score is not None]
        acc_scores = [i.accuracy_score for i in completed_items if i.accuracy_score is not None]
        hal_scores = [i.hallucination_score for i in completed_items if i.hallucination_score is not None]
        comp_scores = [i.completeness_score for i in completed_items if i.completeness_score is not None]
        overall_scores = [i.overall_score for i in completed_items if i.overall_score is not None]
        conf_scores = [i.confidence for i in completed_items if i.confidence is not None]

        return {
            "total_items": total_items,
            "pass_count": pass_count,
            "needs_improvement_count": imp_count,
            "fail_count": fail_count,
            "pass_rate_percent": pass_rate,
            "avg_relevance": round(sum(rel_scores) / len(rel_scores), 2) if rel_scores else 0.0,
            "avg_accuracy": round(sum(acc_scores) / len(acc_scores), 2) if acc_scores else 0.0,
            "avg_hallucination": round(sum(hal_scores) / len(hal_scores), 2) if hal_scores else 0.0,
            "avg_completeness": round(sum(comp_scores) / len(comp_scores), 2) if comp_scores else 0.0,
            "avg_overall_score": round(sum(overall_scores) / len(overall_scores), 2) if overall_scores else 0.0,
            "avg_confidence": round(sum(conf_scores) / len(conf_scores), 2) if conf_scores else 0.0,
            "elapsed_seconds": round(elapsed_seconds, 2),
            "gemini_calls": gemini_calls,
        }
