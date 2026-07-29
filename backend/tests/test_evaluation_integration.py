"""
Integration tests for the AI response evaluation backend flow.

Verifies `/evaluate` API route and `EvaluationService` integration,
testing all 10 QA validation scenarios using direct dependency overrides.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.judge import (
    JudgeLLMResult,
    RelevanceJudgeOutput,
    AccuracyJudgeOutput,
    HallucinationJudgeOutput,
    CompletenessJudgeOutput,
    VerdictOutput
)
from app.core.exceptions import JudgeLLMUnavailableError, JudgeLLMConfigurationError


from app.auth.dependencies import get_current_user
from app.auth.schemas import AuthenticatedUser


@pytest.fixture
def client():
    """Create a TestClient for FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_mocks():
    """Directly override dependencies on the pre-instantiated evaluation_service in the router."""
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        id="00000000-0000-0000-0000-000000000000",
        email="test@veridict.ai",
        provider="email",
    )
    from app.api.evaluation import evaluation_service

    # Save original attributes
    orig_retrieval = evaluation_service.retrieval_service
    orig_relevance = evaluation_service.relevance_judge
    orig_accuracy = getattr(evaluation_service, "accuracy_judge", None)
    orig_hallucination = getattr(evaluation_service, "hallucination_judge", None)
    orig_completeness = getattr(evaluation_service, "completeness_judge", None)
    orig_verdict = getattr(evaluation_service, "verdict_agent", None)

    mock_retrieval = MagicMock()
    mock_retrieval.retrieve.return_value = [
        {
            "id": "chunk_1",
            "score": 0.95,
            "source": "truthfulqa",
            "document_id": "doc_1",
            "chunk_index": 0,
            "question": "What is photosynthesis?",
            "answer": "Process using light.",
            "text": "Photosynthesis turns light into energy.",
        }
    ]

    mock_relevance = MagicMock()
    mock_relevance.evaluate_relevance.return_value = JudgeLLMResult[RelevanceJudgeOutput](
        result=RelevanceJudgeOutput(relevance_score=5, reasoning="Directly answers the query."),
        model_used="gemini-2.5-flash"
    )

    mock_accuracy = MagicMock()
    mock_accuracy.evaluate_accuracy.return_value = JudgeLLMResult[AccuracyJudgeOutput](
        result=AccuracyJudgeOutput(accuracy_score=5, reasoning="Factually accurate."),
        model_used="gemini-2.5-flash"
    )

    mock_hallucination = MagicMock()
    mock_hallucination.evaluate_hallucination.return_value = JudgeLLMResult[HallucinationJudgeOutput](
        result=HallucinationJudgeOutput(status="SUCCESS", hallucination_score=5, reasoning="Factually grounded."),
        model_used="gemini-2.5-flash"
    )

    mock_completeness = MagicMock()
    mock_completeness.evaluate_completeness.return_value = JudgeLLMResult[CompletenessJudgeOutput](
        result=CompletenessJudgeOutput(
            completeness_score=5,
            reasoning="All aspects covered.",
            covered_aspects=["Photosynthesis definition"],
            missing_aspects=[]
        ),
        model_used="gemini-2.5-flash"
    )

    mock_verdict = MagicMock()
    mock_verdict.generate_verdict.return_value = VerdictOutput(
        overall_score=5.00,
        verdict="PASS",
        reasoning="Exemplary performance across all evaluated dimensions.",
        weights_used={"accuracy": 0.35, "completeness": 0.30, "relevance": 0.20, "hallucination": 0.15},
        model_used="gemini-2.5-flash"
    )

    evaluation_service.retrieval_service = mock_retrieval
    evaluation_service.relevance_judge = mock_relevance
    evaluation_service.accuracy_judge = mock_accuracy
    evaluation_service.hallucination_judge = mock_hallucination
    evaluation_service.completeness_judge = mock_completeness
    evaluation_service.verdict_agent = mock_verdict

    yield mock_retrieval, mock_relevance, mock_accuracy, mock_hallucination, mock_completeness, mock_verdict

    # Restore original attributes
    evaluation_service.retrieval_service = orig_retrieval
    evaluation_service.relevance_judge = orig_relevance
    evaluation_service.accuracy_judge = orig_accuracy
    evaluation_service.hallucination_judge = orig_hallucination
    evaluation_service.completeness_judge = orig_completeness
    evaluation_service.verdict_agent = orig_verdict
    app.dependency_overrides.pop(get_current_user, None)


# ──────────────────────────────────────────────
# 10 Validation Scenario Tests
# ──────────────────────────────────────────────
class TestAutomatedValidationScenarios:

    def test_scenario_1_question_response_no_reference_no_pdf(self, client, setup_mocks):
        """Scenario 1: Question + AI Response (no reference, no PDF). All judges & verdict execute."""
        mock_retrieval, mock_relevance, mock_accuracy, mock_hallucination, mock_completeness, mock_verdict = setup_mocks

        response = client.post(
            "/evaluate",
            data={
                "question": "What is gravity?",
                "ai_response": "Gravity is a fundamental force attracting mass.",
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["question"] == "What is gravity?"
        assert data["reference_answer"] is None
        assert data["pdf_namespace"] is None
        assert data["relevance_evaluation"] is not None
        assert data["accuracy_evaluation"] is not None
        assert data["hallucination_evaluation"] is not None
        assert data["completeness_evaluation"] is not None
        assert data["verdict_evaluation"] is not None

    def test_scenario_2_question_response_reference_answer(self, client, setup_mocks):
        """Scenario 2: Question + AI Response + Reference Answer. Reference evidence used."""
        mock_retrieval, mock_relevance, mock_accuracy, mock_hallucination, mock_completeness, mock_verdict = setup_mocks

        response = client.post(
            "/evaluate",
            data={
                "question": "What is photosynthesis?",
                "ai_response": "It is light-based energy production.",
                "reference_answer": "Plants producing food using light.",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["reference_answer"] == "Plants producing food using light."
        assert data["verdict_evaluation"]["verdict"] == "PASS"

        # Verify reference_answer passed to accuracy & hallucination judges
        _, kwargs_acc = mock_accuracy.evaluate_accuracy.call_args
        assert kwargs_acc["reference_answer"] == "Plants producing food using light."

        _, kwargs_hal = mock_hallucination.evaluate_hallucination.call_args
        assert kwargs_hal["reference_answer"] == "Plants producing food using light."

    @patch("app.services.pdf_ingestion_service.PDFIngestionService.ingest_pdf_async")
    @patch("app.services.pdf_cache_service.PDFCacheService.get_cached_namespace")
    def test_scenario_3_question_response_uploaded_pdf(
        self, mock_cache, mock_ingest, client, setup_mocks
    ):
        """Scenario 3: Question + AI Response + Uploaded PDF. PDF retrieval & full pipeline execute."""
        mock_retrieval, mock_relevance, mock_accuracy, mock_hallucination, mock_completeness, mock_verdict = setup_mocks
        mock_cache.return_value = None

        dummy_pdf = b"%PDF-1.4 ... dummy content"
        response = client.post(
            "/evaluate",
            data={
                "question": "Explain quantum computing.",
                "ai_response": "Quantum computing uses qubits.",
            },
            files={"pdf_file": ("physics.pdf", dummy_pdf, "application/pdf")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pdf_namespace"] is not None
        assert data["pdf_status"] == "Processing"
        assert data["completeness_evaluation"] is not None
        assert data["verdict_evaluation"] is not None

    @patch("app.services.pdf_ingestion_service.PDFIngestionService.ingest_pdf_async")
    @patch("app.services.pdf_cache_service.PDFCacheService.get_cached_namespace")
    def test_scenario_4_question_response_reference_and_pdf(
        self, mock_cache, mock_ingest, client, setup_mocks
    ):
        """Scenario 4: Reference Answer + Uploaded PDF. Both evidence sources handled cleanly."""
        mock_retrieval, mock_relevance, mock_accuracy, mock_hallucination, mock_completeness, mock_verdict = setup_mocks
        mock_cache.return_value = None

        dummy_pdf = b"%PDF-1.4 ... dummy content"
        response = client.post(
            "/evaluate",
            data={
                "question": "What is photosynthesis?",
                "ai_response": "Light into chemical energy.",
                "reference_answer": "Plants convert light to sugar.",
            },
            files={"pdf_file": ("botany.pdf", dummy_pdf, "application/pdf")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["reference_answer"] == "Plants convert light to sugar."
        assert data["pdf_namespace"] is not None
        assert data["verdict_evaluation"] is not None

    def test_scenario_5_hallucination_insufficient_evidence_weight_normalization(self, client, setup_mocks):
        """Scenario 5: Hallucination returns INSUFFICIENT_EVIDENCE -> excluded and weights normalized."""
        mock_retrieval, mock_relevance, mock_accuracy, mock_hallucination, mock_completeness, mock_verdict = setup_mocks

        insufficient_result = JudgeLLMResult[HallucinationJudgeOutput](
            result=HallucinationJudgeOutput(
                status="INSUFFICIENT_EVIDENCE",
                hallucination_score=None,
                reasoning="No evidence available."
            ),
            model_used="gemini-2.5-flash"
        )
        mock_hallucination.evaluate_hallucination.return_value = insufficient_result

        # Override verdict mock to return output without hallucination in weights_used
        mock_verdict.generate_verdict.return_value = VerdictOutput(
            overall_score=5.00,
            verdict="PASS",
            reasoning="Normalized verdict summary.",
            weights_used={"accuracy": 0.4118, "completeness": 0.3529, "relevance": 0.2353},
            model_used="gemini-2.5-flash"
        )

        response = client.post(
            "/evaluate",
            data={
                "question": "What is dark matter?",
                "ai_response": "Dark matter is non-baryonic matter.",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["hallucination_evaluation"]["status"] == "INSUFFICIENT_EVIDENCE"
        assert data["verdict_evaluation"] is not None
        assert "hallucination" not in data["verdict_evaluation"]["weights_used"]
        assert data["verdict_evaluation"]["verdict"] == "PASS"

    def test_scenario_6_highly_incomplete_answer(self, client, setup_mocks):
        """Scenario 6: Highly incomplete answer -> Completeness score is low and verdict reflects reduced score."""
        mock_retrieval, mock_relevance, mock_accuracy, mock_hallucination, mock_completeness, mock_verdict = setup_mocks

        incomplete_comp = JudgeLLMResult[CompletenessJudgeOutput](
            result=CompletenessJudgeOutput(
                completeness_score=1,
                reasoning="Missed 4 out of 5 requested aspects.",
                covered_aspects=["Aspect 1"],
                missing_aspects=["Aspect 2", "Aspect 3", "Aspect 4", "Aspect 5"]
            ),
            model_used="gemini-2.5-flash"
        )
        mock_completeness.evaluate_completeness.return_value = incomplete_comp

        # Acc=5 (1.75), Comp=1 (0.30), Rel=5 (1.00), Hal=5 (0.75) -> Total = 3.80 -> NEEDS_IMPROVEMENT
        mock_verdict.generate_verdict.return_value = VerdictOutput(
            overall_score=3.80,
            verdict="NEEDS_IMPROVEMENT",
            reasoning="Severe completeness omissions reduce the verdict score.",
            weights_used={"accuracy": 0.35, "completeness": 0.30, "relevance": 0.20, "hallucination": 0.15},
            model_used="gemini-2.5-flash"
        )

        response = client.post(
            "/evaluate",
            data={
                "question": "Explain photosynthesis and list all 5 light reaction stages.",
                "ai_response": "Plants make food.",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completeness_evaluation"]["completeness_score"] == 1
        assert data["verdict_evaluation"]["verdict"] == "NEEDS_IMPROVEMENT"
        assert data["verdict_evaluation"]["overall_score"] == 3.80

    def test_scenario_7_excellent_answer_pass_verdict(self, client, setup_mocks):
        """Scenario 7: Excellent answer -> PASS verdict (5.00)."""
        mock_retrieval, mock_relevance, mock_accuracy, mock_hallucination, mock_completeness, mock_verdict = setup_mocks

        response = client.post(
            "/evaluate",
            data={
                "question": "What is Python?",
                "ai_response": "Python is a high-level programming language.",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["verdict_evaluation"]["verdict"] == "PASS"
        assert data["verdict_evaluation"]["overall_score"] == 5.00

    def test_scenario_8_unrelated_answer_fail_verdict(self, client, setup_mocks):
        """Scenario 8: Completely unrelated answer -> FAIL verdict."""
        mock_retrieval, mock_relevance, mock_accuracy, mock_hallucination, mock_completeness, mock_verdict = setup_mocks

        # Set low scores for unrelated answer
        mock_relevance.evaluate_relevance.return_value = JudgeLLMResult[RelevanceJudgeOutput](
            result=RelevanceJudgeOutput(relevance_score=1, reasoning="Unrelated topic."),
            model_used="gemini-2.5-flash"
        )
        mock_completeness.evaluate_completeness.return_value = JudgeLLMResult[CompletenessJudgeOutput](
            result=CompletenessJudgeOutput(completeness_score=1, reasoning="Unrelated.", covered_aspects=[], missing_aspects=["Topic"]),
            model_used="gemini-2.5-flash"
        )
        mock_verdict.generate_verdict.return_value = VerdictOutput(
            overall_score=1.45,
            verdict="FAIL",
            reasoning="Completely off-topic response.",
            weights_used={"accuracy": 0.35, "completeness": 0.30, "relevance": 0.20, "hallucination": 0.15},
            model_used="gemini-2.5-flash"
        )

        response = client.post(
            "/evaluate",
            data={
                "question": "What is the capital of France?",
                "ai_response": "I enjoy playing basketball.",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["relevance_evaluation"]["relevance_score"] == 1
        assert data["verdict_evaluation"]["verdict"] == "FAIL"

    def test_scenario_9_empty_reference_answer_graceful(self, client, setup_mocks):
        """Scenario 9: Empty reference answer handled gracefully."""
        mock_retrieval, mock_relevance, mock_accuracy, mock_hallucination, mock_completeness, mock_verdict = setup_mocks

        response = client.post(
            "/evaluate",
            data={
                "question": "What is speed of light?",
                "ai_response": "299,792,458 m/s.",
                "reference_answer": "   ",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["verdict_evaluation"] is not None

    def test_scenario_10_retrieval_returns_no_chunks_no_crash(self, client, setup_mocks):
        """Scenario 10: Retrieval returns no chunks -> No crashes, hallucination handles evidence, verdict generated."""
        mock_retrieval, mock_relevance, mock_accuracy, mock_hallucination, mock_completeness, mock_verdict = setup_mocks
        mock_retrieval.retrieve.return_value = []

        response = client.post(
            "/evaluate",
            data={
                "question": "Unusual question?",
                "ai_response": "Response answer.",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["retrieved_chunks"]) == 0
        assert data["verdict_evaluation"] is not None
