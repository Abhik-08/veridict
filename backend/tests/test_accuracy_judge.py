"""
Unit tests for the AccuracyJudge agent.

All tests mock the JudgeLLMService to prevent real Gemini API usage.
"""

from unittest.mock import MagicMock
import pytest

from app.agents.accuracy_judge import AccuracyJudge, ACCURACY_JUDGE_PROMPT_TEMPLATE
from app.core.exceptions import JudgeLLMUnavailableError
from app.schemas.judge import JudgeLLMResult, AccuracyJudgeOutput


@pytest.fixture
def mock_judge_service():
    """Create a mock JudgeLLMService."""
    return MagicMock()


@pytest.fixture
def accuracy_judge(mock_judge_service):
    """Create an AccuracyJudge instance with a mocked JudgeLLMService."""
    return AccuracyJudge(judge_llm_service=mock_judge_service)


# ──────────────────────────────────────────────
# Rubric Score Tests (1-5)
# ──────────────────────────────────────────────
class TestAccuracyScoringRubric:
    @pytest.mark.parametrize("score", [1, 2, 3, 4, 5])
    def test_accuracy_scores_propagate(self, accuracy_judge, mock_judge_service, score):
        """Verify that scores from 1 to 5 are parsed, validated, and returned correctly."""
        expected_output = AccuracyJudgeOutput(
            accuracy_score=score,
            reasoning=f"Reasoning for score {score}."
        )
        mock_result = JudgeLLMResult[AccuracyJudgeOutput](
            result=expected_output,
            model_used="gemini-2.0-flash"
        )
        mock_judge_service.evaluate.return_value = mock_result

        result = accuracy_judge.evaluate_accuracy(
            question="What is the capital of France?",
            ai_response="The capital of France is Paris.",
            retrieved_evidence="Paris is the capital of France."
        )

        assert isinstance(result, JudgeLLMResult)
        assert result.result.accuracy_score == score
        assert result.result.reasoning == f"Reasoning for score {score}."
        assert result.model_used == "gemini-2.0-flash"


# ──────────────────────────────────────────────
# Input Validation Tests
# ──────────────────────────────────────────────
class TestInputValidation:
    def test_empty_question_rejected(self, accuracy_judge):
        """ValueError raised for empty question string."""
        with pytest.raises(ValueError) as exc:
            accuracy_judge.evaluate_accuracy("", "Some response")
        assert "Question cannot be empty" in str(exc.value)

    def test_whitespace_question_rejected(self, accuracy_judge):
        """ValueError raised for whitespace-only question."""
        with pytest.raises(ValueError) as exc:
            accuracy_judge.evaluate_accuracy("   ", "Some response")
        assert "Question cannot be empty" in str(exc.value)

    def test_empty_response_rejected(self, accuracy_judge):
        """ValueError raised for empty AI response string."""
        with pytest.raises(ValueError) as exc:
            accuracy_judge.evaluate_accuracy("Some question?", "")
        assert "AI response cannot be empty" in str(exc.value)

    def test_whitespace_response_rejected(self, accuracy_judge):
        """ValueError raised for whitespace-only AI response."""
        with pytest.raises(ValueError) as exc:
            accuracy_judge.evaluate_accuracy("Some question?", "   ")
        assert "AI response cannot be empty" in str(exc.value)


# ──────────────────────────────────────────────
# Exception Propagation Tests
# ──────────────────────────────────────────────
class TestExceptionPropagation:
    def test_service_exceptions_propagate(self, accuracy_judge, mock_judge_service):
        """Verify that JudgeLLMService exceptions are propagated to higher layers."""
        mock_judge_service.evaluate.side_effect = JudgeLLMUnavailableError("Service unavailable")

        with pytest.raises(JudgeLLMUnavailableError) as exc:
            accuracy_judge.evaluate_accuracy("Question?", "Response")
        
        assert "Service unavailable" in str(exc.value)


# ──────────────────────────────────────────────
# Prompt and Evidence Handling Tests
# ──────────────────────────────────────────────
class TestEvidenceHandling:
    def test_missing_evidence(self, accuracy_judge, mock_judge_service):
        """Verify 'None Provided' is substituted when evidence is omitted."""
        expected_output = AccuracyJudgeOutput(accuracy_score=3, reasoning="Test")
        mock_result = JudgeLLMResult[AccuracyJudgeOutput](result=expected_output, model_used="gemini")
        mock_judge_service.evaluate.return_value = mock_result

        accuracy_judge.evaluate_accuracy("Question?", "Response")

        called_prompt = mock_judge_service.evaluate.call_args[1]["prompt"]
        assert "[START OF REFERENCE ANSWER]\nNone Provided.\n[END OF REFERENCE ANSWER]" in called_prompt
        assert "[START OF RETRIEVED EVIDENCE]\nNone Provided.\n[END OF RETRIEVED EVIDENCE]" in called_prompt

    def test_provided_evidence(self, accuracy_judge, mock_judge_service):
        """Verify provided evidence is injected into the prompt."""
        expected_output = AccuracyJudgeOutput(accuracy_score=3, reasoning="Test")
        mock_result = JudgeLLMResult[AccuracyJudgeOutput](result=expected_output, model_used="gemini")
        mock_judge_service.evaluate.return_value = mock_result

        accuracy_judge.evaluate_accuracy(
            "Question?",
            "Response",
            reference_answer="Ref Ans",
            retrieved_evidence="Ret Evid"
        )

        called_prompt = mock_judge_service.evaluate.call_args[1]["prompt"]
        assert "[START OF REFERENCE ANSWER]\nRef Ans\n[END OF REFERENCE ANSWER]" in called_prompt
        assert "[START OF RETRIEVED EVIDENCE]\nRet Evid\n[END OF RETRIEVED EVIDENCE]" in called_prompt

    def test_prompt_contains_safeguards(self):
        """Verify the prompt template contains required injection safeguards and rubric details."""
        assert "Evaluate ONLY factual correctness" in ACCURACY_JUDGE_PROMPT_TEMPLATE
        assert "SAFETY & PROMPT INJECTION RULES" in ACCURACY_JUDGE_PROMPT_TEMPLATE
        assert "CLAIM-LEVEL EVALUATION" in ACCURACY_JUDGE_PROMPT_TEMPLATE
