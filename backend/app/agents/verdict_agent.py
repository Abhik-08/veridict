"""Verdict Agent. Calculates deterministic weighted overall scores and synthesizes verdict reasoning."""

import logging
from typing import Any, Literal

from app.schemas.judge import (
    JudgeLLMResult,
    VerdictReasoningOutput,
    VerdictOutput,
    RelevanceJudgeOutput,
    AccuracyJudgeOutput,
    HallucinationJudgeOutput,
    CompletenessJudgeOutput
)
from app.services.judge_llm_service import JudgeLLMService

logger = logging.getLogger(__name__)

# Default string for non-evaluated dimensions
NOT_EVALUATED = "Not Evaluated"

# Default weights assigned to judge dimensions
DEFAULT_WEIGHTS: dict[str, float] = {
    "accuracy": 0.35,
    "completeness": 0.30,
    "relevance": 0.20,
    "hallucination": 0.15,
}

# Prompt template for verdict reasoning synthesis
VERDICT_AGENT_PROMPT_TEMPLATE = """You are a meticulous, objective Verdict Reasoning Synthesizer. Your sole task is to generate a concise, natural-language explanation summarizing an AI response evaluation verdict based on provided judge scores.

### CRITICAL RULES:
- DO NOT calculate or modify scores. The overall score and verdict have ALREADY been calculated deterministically in Python.
- DO NOT change the verdict category.
- DO NOT change the overall score.
- Generate ONLY a concise, professional reasoning summary explaining why the AI response earned this overall score and verdict.
- Highlight key strengths (high scoring dimensions) and weaknesses or omissions (low scoring dimensions).

### EVALUATION METRICS SUMMARY:
[START OF QUESTION]
{question}
[END OF QUESTION]

[START OF AI RESPONSE]
{ai_response}
[END OF AI RESPONSE]

JUDGE SCORES:
- Accuracy: {accuracy_info}
- Completeness: {completeness_info}
- Relevance: {relevance_info}
- Hallucination / Groundedness: {hallucination_info}

CALCULATED OVERALL SCORE: {overall_score:.2f} / 5.00
FINAL VERDICT: {verdict}
"""


class VerdictAgent:
    """Agent responsible for deterministic weighted score aggregation and verdict synthesis."""

    def __init__(self, judge_llm_service: JudgeLLMService | None = None) -> None:
        """Initialize the VerdictAgent."""
        self.judge_llm_service = judge_llm_service or JudgeLLMService()

    @staticmethod
    def _coerce_int_score(val: Any) -> int | None:
        """Safely coerce value to integer score between 1 and 5."""
        if val is None:
            return None
        try:
            score = int(val)
            return score if 1 <= score <= 5 else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _extract_score_and_status(eval_input: Any, score_attr: str) -> tuple[int | None, str | None]:
        """Extract numeric score and optional status string from dict, model, or raw numeric input."""
        if eval_input is None:
            return None, None

        if isinstance(eval_input, (int, float)):
            return VerdictAgent._coerce_int_score(eval_input), None

        if isinstance(eval_input, dict):
            status = eval_input.get("status")
            score = eval_input.get(score_attr) or eval_input.get("score")
            return VerdictAgent._coerce_int_score(score), status

        # Handle JudgeLLMResult or Pydantic model objects
        target = getattr(eval_input, "result", eval_input)
        status = getattr(target, "status", None)
        score = getattr(target, score_attr, None) or getattr(target, "score", None)
        return VerdictAgent._coerce_int_score(score), status

    def calculate_weighted_score(
        self,
        accuracy_eval: Any = None,
        completeness_eval: Any = None,
        relevance_eval: Any = None,
        hallucination_eval: Any = None,
        custom_weights: dict[str, float] | None = None,
    ) -> tuple[float, str, dict[str, float]]:
        """
        Calculate deterministic weighted overall score, verdict category, and normalized weights.

        Excludes hallucination judge when status is INSUFFICIENT_EVIDENCE or score is None,
        and automatically normalizes remaining weights.
        """
        weights = dict(custom_weights or DEFAULT_WEIGHTS)

        # Extract individual scores
        acc_score, _ = self._extract_score_and_status(accuracy_eval, "accuracy_score")
        comp_score, _ = self._extract_score_and_status(completeness_eval, "completeness_score")
        rel_score, _ = self._extract_score_and_status(relevance_eval, "relevance_score")
        hal_score, hal_status = self._extract_score_and_status(hallucination_eval, "hallucination_score")

        # Exclude hallucination if status is INSUFFICIENT_EVIDENCE
        if hal_status == "INSUFFICIENT_EVIDENCE":
            hal_score = None

        raw_scores: dict[str, int | None] = {
            "accuracy": acc_score,
            "completeness": comp_score,
            "relevance": rel_score,
            "hallucination": hal_score,
        }

        # Filter active judges with valid 1-5 scores
        active_judges = {
            k: score for k, score in raw_scores.items()
            if score is not None and 1 <= score <= 5
        }

        if not active_judges:
            raise ValueError("No valid judge scores available to calculate overall verdict.")

        # Compute weight normalization
        total_raw_weight = sum(weights[k] for k in active_judges)
        if total_raw_weight <= 0:
            raise ValueError("Sum of active weights must be greater than zero.")

        normalized_weights = {
            k: round(weights[k] / total_raw_weight, 4)
            for k in active_judges
        }

        # Weighted average calculation
        weighted_sum = sum(
            score * (weights[k] / total_raw_weight)
            for k, score in active_judges.items()
        )
        overall_score = round(weighted_sum, 2)

        # Verdict threshold mapping
        if overall_score >= 4.00:
            verdict: Literal["PASS", "NEEDS_IMPROVEMENT", "FAIL"] = "PASS"
        elif overall_score >= 2.50:
            verdict = "NEEDS_IMPROVEMENT"
        else:
            verdict = "FAIL"

        return overall_score, verdict, normalized_weights

    def generate_verdict(
        self,
        question: str,
        ai_response: str,
        accuracy_eval: Any = None,
        completeness_eval: Any = None,
        relevance_eval: Any = None,
        hallucination_eval: Any = None,
        custom_weights: dict[str, float] | None = None,
    ) -> VerdictOutput:
        """
        Generate overall evaluation verdict containing deterministic score and Gemini synthesized reasoning.
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty or whitespace-only.")
        if not ai_response or not ai_response.strip():
            raise ValueError("AI response cannot be empty or whitespace-only.")

        logger.info("Verdict calculation started.")

        try:
            overall_score, verdict, weights_used = self.calculate_weighted_score(
                accuracy_eval=accuracy_eval,
                completeness_eval=completeness_eval,
                relevance_eval=relevance_eval,
                hallucination_eval=hallucination_eval,
                custom_weights=custom_weights,
            )

            # Format judge info strings for prompt
            acc_score, _ = self._extract_score_and_status(accuracy_eval, "accuracy_score")
            comp_score, _ = self._extract_score_and_status(completeness_eval, "completeness_score")
            rel_score, _ = self._extract_score_and_status(relevance_eval, "relevance_score")
            hal_score, hal_status = self._extract_score_and_status(hallucination_eval, "hallucination_score")

            acc_info = f"{acc_score}/5" if acc_score else NOT_EVALUATED
            comp_info = f"{comp_score}/5" if comp_score else NOT_EVALUATED
            rel_info = f"{rel_score}/5" if rel_score else NOT_EVALUATED
            if hal_status == "INSUFFICIENT_EVIDENCE":
                hal_info = "Insufficient Evidence (Excluded)"
            elif hal_score is not None:
                hal_info = f"{hal_score}/5"
            else:
                hal_info = NOT_EVALUATED

            prompt = VERDICT_AGENT_PROMPT_TEMPLATE.format(
                question=question.strip(),
                ai_response=ai_response.strip(),
                accuracy_info=acc_info,
                completeness_info=comp_info,
                relevance_info=rel_info,
                hallucination_info=hal_info,
                overall_score=overall_score,
                verdict=verdict,
            )

            result = self.judge_llm_service.evaluate(
                prompt=prompt,
                output_model=VerdictReasoningOutput
            )

            logger.info(
                "Verdict calculation completed. Score: %.2f, Verdict: %s, Model used: %s",
                overall_score,
                verdict,
                result.model_used
            )

            return VerdictOutput(
                overall_score=overall_score,
                verdict=verdict,
                reasoning=result.result.reasoning,
                weights_used=weights_used,
                model_used=result.model_used
            )

        except Exception:
            logger.exception("Verdict calculation failed.")
            raise
