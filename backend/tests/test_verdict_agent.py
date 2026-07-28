"""
Unit tests for the VerdictAgent.

All tests mock the JudgeLLMService to prevent real Gemini API calls.
"""

from unittest.mock import MagicMock
import pytest

from app.agents.verdict_agent import VerdictAgent, DEFAULT_WEIGHTS, VERDICT_AGENT_PROMPT_TEMPLATE
from app.core.exceptions import JudgeLLMUnavailableError
from app.schemas.judge import JudgeLLMResult, VerdictReasoningOutput, VerdictOutput


@pytest.fixture
def mock_judge_service():
    """Create a mock JudgeLLMService."""
    return MagicMock()


@pytest.fixture
def verdict_agent(mock_judge_service):
    """Create a VerdictAgent instance with a mocked JudgeLLMService."""
    return VerdictAgent(judge_llm_service=mock_judge_service)


# ──────────────────────────────────────────────
# Weighted Score & Rounding Calculation Tests
# ──────────────────────────────────────────────
class TestWeightedScoreCalculation:
    def test_perfect_scores_yield_pass_5_00(self, verdict_agent, mock_judge_service):
        """All 5s yield 5.00 score and PASS verdict."""
        mock_judge_service.evaluate.return_value = JudgeLLMResult[VerdictReasoningOutput](
            result=VerdictReasoningOutput(reasoning="Outstanding response across all metrics."),
            model_used="gemini-2.5-flash"
        )

        output = verdict_agent.generate_verdict(
            question="What is Python?",
            ai_response="Python is a high-level programming language.",
            accuracy_eval={"accuracy_score": 5},
            completeness_eval={"completeness_score": 5},
            relevance_eval={"relevance_score": 5},
            hallucination_eval={"hallucination_score": 5, "status": "SUCCESS"}
        )

        assert output.overall_score == 5.00
        assert output.verdict == "PASS"
        assert output.weights_used == DEFAULT_WEIGHTS
        assert output.reasoning == "Outstanding response across all metrics."

    def test_weighted_score_and_rounding(self, verdict_agent):
        """Verify exact weighted sum formula and 2 decimal place rounding."""
        # Acc: 4*0.35=1.4, Comp: 3*0.30=0.9, Rel: 5*0.20=1.0, Hal: 2*0.15=0.3 -> Total = 3.60
        score, verdict, weights = verdict_agent.calculate_weighted_score(
            accuracy_eval={"accuracy_score": 4},
            completeness_eval={"completeness_score": 3},
            relevance_eval={"relevance_score": 5},
            hallucination_eval={"hallucination_score": 2, "status": "SUCCESS"}
        )

        assert score == 3.60
        assert verdict == "NEEDS_IMPROVEMENT"
        assert weights == DEFAULT_WEIGHTS


# ──────────────────────────────────────────────
# Weight Normalization & Insufficient Evidence Tests
# ──────────────────────────────────────────────
class TestWeightNormalization:
    def test_insufficient_evidence_hallucination_excluded(self, verdict_agent):
        """Hallucination excluded when status is INSUFFICIENT_EVIDENCE, weights auto-normalized."""
        # Remaining weights sum: 0.35 + 0.30 + 0.20 = 0.85
        # Acc=4 (4*0.35/0.85 = 1.64705), Comp=4 (4*0.30/0.85 = 1.41176), Rel=4 (4*0.20/0.85 = 0.94117) -> Total = 4.00
        score, verdict, weights = verdict_agent.calculate_weighted_score(
            accuracy_eval={"accuracy_score": 4},
            completeness_eval={"completeness_score": 4},
            relevance_eval={"relevance_score": 4},
            hallucination_eval={"hallucination_score": None, "status": "INSUFFICIENT_EVIDENCE"}
        )

        assert score == 4.00
        assert verdict == "PASS"
        assert "hallucination" not in weights
        assert weights["accuracy"] == round(0.35 / 0.85, 4)
        assert weights["completeness"] == round(0.30 / 0.85, 4)
        assert weights["relevance"] == round(0.20 / 0.85, 4)

    def test_missing_judge_scores_excluded_and_normalized(self, verdict_agent):
        """Missing or None judge scores are excluded and remaining weights normalized."""
        # Only Accuracy (0.35) and Completeness (0.30) available -> sum = 0.65
        score, verdict, weights = verdict_agent.calculate_weighted_score(
            accuracy_eval={"accuracy_score": 5},
            completeness_eval={"completeness_score": 3},
            relevance_eval=None,
            hallucination_eval=None
        )

        expected_score = round((5 * (0.35 / 0.65)) + (3 * (0.30 / 0.65)), 2)
        assert score == expected_score
        assert set(weights.keys()) == {"accuracy", "completeness"}


# ──────────────────────────────────────────────
# Verdict Category Threshold Tests
# ──────────────────────────────────────────────
class TestVerdictCategories:
    def test_pass_category_threshold(self, verdict_agent):
        """Scores 4.00 to 5.00 map to PASS."""
        score, verdict, _ = verdict_agent.calculate_weighted_score(
            accuracy_eval=4, completeness_eval=4, relevance_eval=4, hallucination_eval=4
        )
        assert score == 4.00
        assert verdict == "PASS"

    def test_needs_improvement_category_threshold(self, verdict_agent):
        """Scores 2.50 to 3.99 map to NEEDS_IMPROVEMENT."""
        score, verdict, _ = verdict_agent.calculate_weighted_score(
            accuracy_eval=3, completeness_eval=3, relevance_eval=3, hallucination_eval=3
        )
        assert score == 3.00
        assert verdict == "NEEDS_IMPROVEMENT"

    def test_fail_category_threshold(self, verdict_agent):
        """Scores 1.00 to 2.49 map to FAIL."""
        score, verdict, _ = verdict_agent.calculate_weighted_score(
            accuracy_eval=1, completeness_eval=2, relevance_eval=1, hallucination_eval=2
        )
        assert score == 1.45
        assert verdict == "FAIL"


# ──────────────────────────────────────────────
# Input Validation & Exception Propagation Tests
# ──────────────────────────────────────────────
class TestInputValidation:
    def test_empty_question_rejected(self, verdict_agent):
        """ValueError raised for empty question string."""
        with pytest.raises(ValueError) as exc:
            verdict_agent.generate_verdict("", "AI Response", accuracy_eval=5)
        assert "Question cannot be empty" in str(exc.value)

    def test_empty_response_rejected(self, verdict_agent):
        """ValueError raised for empty AI response string."""
        with pytest.raises(ValueError) as exc:
            verdict_agent.generate_verdict("Question?", "", accuracy_eval=5)
        assert "AI response cannot be empty" in str(exc.value)

    def test_no_valid_judge_scores_raises_error(self, verdict_agent):
        """ValueError raised when no valid active judge scores are provided."""
        with pytest.raises(ValueError) as exc:
            verdict_agent.calculate_weighted_score()
        assert "No valid judge scores available" in str(exc.value)

    def test_service_exceptions_propagate(self, verdict_agent, mock_judge_service):
        """JudgeLLMUnavailableError propagates to caller."""
        mock_judge_service.evaluate.side_effect = JudgeLLMUnavailableError("LLM unavailable")

        with pytest.raises(JudgeLLMUnavailableError) as exc:
            verdict_agent.generate_verdict("Q?", "A.", accuracy_eval=5)
        assert "LLM unavailable" in str(exc.value)


# ──────────────────────────────────────────────
# Prompt Safeguards Inspection Tests
# ──────────────────────────────────────────────
class TestPromptSafeguards:
    def test_prompt_contains_mandatory_negative_instructions(self, verdict_agent, mock_judge_service):
        """Verify prompt explicitly instructs Gemini NOT to calculate scores or change verdicts."""
        mock_judge_service.evaluate.return_value = JudgeLLMResult[VerdictReasoningOutput](
            result=VerdictReasoningOutput(reasoning="Summary reasoning."),
            model_used="gemini-2.5-flash"
        )

        verdict_agent.generate_verdict(
            question="What is H2O?",
            ai_response="H2O is water.",
            accuracy_eval=5,
            completeness_eval=5,
            relevance_eval=5,
            hallucination_eval={"status": "INSUFFICIENT_EVIDENCE"}
        )

        called_args, called_kwargs = mock_judge_service.evaluate.call_args
        prompt = called_kwargs.get("prompt") or called_args[0]

        assert "DO NOT calculate or modify scores" in prompt
        assert "DO NOT change the verdict category" in prompt
        assert "DO NOT change the overall score" in prompt
        assert "Insufficient Evidence (Excluded)" in prompt
        assert "[START OF QUESTION]" in prompt
        assert "[END OF QUESTION]" in prompt
