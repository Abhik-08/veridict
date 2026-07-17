"""
Integration tests for the AI response evaluation backend flow.

Verifies `/evaluate` API route and `EvaluationService` integration,
using direct dependency overrides on the pre-instantiated evaluation_service.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.judge import JudgeLLMResult, RelevanceJudgeOutput, AccuracyJudgeOutput
from app.core.exceptions import JudgeLLMUnavailableError, JudgeLLMConfigurationError


@pytest.fixture
def client():
    """Create a TestClient for FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_mocks():
    """Directly override dependencies on the pre-instantiated evaluation_service in the router."""
    from app.api.evaluation import evaluation_service

    # Save original attributes
    orig_retrieval = evaluation_service.retrieval_service
    orig_relevance = evaluation_service.relevance_judge
    orig_accuracy = getattr(evaluation_service, "accuracy_judge", None)

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
    expected_output = RelevanceJudgeOutput(
        relevance_score=5,
        reasoning="Directly answers the query."
    )
    mock_result = JudgeLLMResult[RelevanceJudgeOutput](
        result=expected_output,
        model_used="gemini-2.5-flash"
    )
    mock_relevance.evaluate_relevance.return_value = mock_result

    mock_accuracy = MagicMock()
    expected_acc_output = AccuracyJudgeOutput(
        accuracy_score=5,
        reasoning="Factually accurate."
    )
    mock_acc_result = JudgeLLMResult[AccuracyJudgeOutput](
        result=expected_acc_output,
        model_used="gemini-2.5-flash"
    )
    mock_accuracy.evaluate_accuracy.return_value = mock_acc_result

    evaluation_service.retrieval_service = mock_retrieval
    evaluation_service.relevance_judge = mock_relevance
    evaluation_service.accuracy_judge = mock_accuracy

    yield mock_retrieval, mock_relevance, mock_accuracy

    # Restore original attributes
    evaluation_service.retrieval_service = orig_retrieval
    evaluation_service.relevance_judge = orig_relevance
    evaluation_service.accuracy_judge = orig_accuracy


# ──────────────────────────────────────────────
# Integration Tests
# ──────────────────────────────────────────────
class TestEvaluationIntegration:
    def test_evaluate_integration_success(self, client, setup_mocks):
        """Verify successful relevance & accuracy evaluation and preserved M1 retrieval behavior."""
        mock_retrieval, mock_relevance, mock_accuracy = setup_mocks

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

        # Input fields check
        assert data["question"] == "What is photosynthesis?"
        assert data["ai_response"] == "It is light-based energy production."
        assert data["reference_answer"] == "Plants producing food using light."

        # M1 Retrieval integrity check
        assert len(data["retrieved_chunks"]) == 1
        assert data["retrieved_chunks"][0]["id"] == "chunk_1"

        # Relevance evaluation result check
        assert data["relevance_evaluation"] is not None
        assert data["relevance_evaluation"]["relevance_score"] == 5
        assert data["relevance_evaluation"]["reasoning"] == "Directly answers the query."
        assert data["relevance_evaluation"]["model_used"] == "gemini-2.5-flash"

        # Accuracy evaluation result check
        assert data["accuracy_evaluation"] is not None
        assert data["accuracy_evaluation"]["accuracy_score"] == 5
        assert data["accuracy_evaluation"]["reasoning"] == "Factually accurate."
        assert data["accuracy_evaluation"]["model_used"] == "gemini-2.5-flash"

        # Verifies inputs passed correctly
        mock_relevance.evaluate_relevance.assert_called_once_with(
            question="What is photosynthesis?",
            ai_response="It is light-based energy production."
        )

        mock_accuracy.evaluate_accuracy.assert_called_once_with(
            question="What is photosynthesis?",
            ai_response="It is light-based energy production.",
            reference_answer="Plants producing food using light.",
            retrieved_evidence="Photosynthesis turns light into energy."
        )

    def test_evaluate_integration_without_reference_and_evidence(self, client, setup_mocks):
        """Verify evaluation works when reference answer and retrieved evidence are omitted."""
        mock_retrieval, mock_relevance, mock_accuracy = setup_mocks
        mock_retrieval.retrieve.return_value = []  # No evidence retrieved

        response = client.post(
            "/evaluate",
            data={
                "question": "What is the capital of France?",
                "ai_response": "Paris.",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["reference_answer"] is None
        assert len(data["retrieved_chunks"]) == 0
        assert data["relevance_evaluation"]["relevance_score"] == 5
        assert data["accuracy_evaluation"]["accuracy_score"] == 5

        # Verify None values passed down
        mock_accuracy.evaluate_accuracy.assert_called_once_with(
            question="What is the capital of France?",
            ai_response="Paris.",
            reference_answer=None,
            retrieved_evidence=None
        )

    def test_evaluate_accuracy_judge_unavailability_graceful(self, client, setup_mocks):
        """Verify Accuracy Judge unavailability returns accuracy_evaluation=null while relevance remains."""
        mock_retrieval, mock_relevance, mock_accuracy = setup_mocks
        mock_accuracy.evaluate_accuracy.side_effect = JudgeLLMUnavailableError("Temporary limit.")

        response = client.post(
            "/evaluate",
            data={
                "question": "Question?",
                "ai_response": "Response.",
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Relevance still succeeded
        assert data["relevance_evaluation"] is not None
        assert data["relevance_evaluation"]["relevance_score"] == 5

        # Accuracy failed gracefully
        assert data["accuracy_evaluation"] is None

    def test_evaluate_accuracy_judge_config_error_propagates(self, client, setup_mocks):
        """Verify Judge configuration errors propagate and cause 500 status code."""
        mock_retrieval, mock_relevance, mock_accuracy = setup_mocks
        mock_accuracy.evaluate_accuracy.side_effect = JudgeLLMConfigurationError("Bad credentials.")

        response = client.post(
            "/evaluate",
            data={
                "question": "Question?",
                "ai_response": "Response.",
            }
        )

        # Config error is not swallowed
        assert response.status_code == 500
        assert "Bad credentials" in response.json()["detail"]


# ──────────────────────────────────────────────
# PDF Flow Ingestion Tests
# ──────────────────────────────────────────────
class TestPDFIngestionFlow:
    @patch("app.services.pdf_ingestion_service.PDFIngestionService.ingest_pdf_async")
    @patch("app.services.pdf_cache_service.PDFCacheService.get_cached_namespace")
    def test_pdf_upload_flow_intact(
        self, mock_cache, mock_ingest, client, setup_mocks
    ):
        """Verify PDF ingestion does not break and maps correctly to background task."""
        mock_retrieval, mock_relevance, mock_accuracy = setup_mocks
        mock_cache.return_value = None  # Cache miss

        # Create dummy PDF bytes
        dummy_pdf = b"%PDF-1.4 ... dummy content"

        response = client.post(
            "/evaluate",
            data={
                "question": "What is photosynthesis?",
                "ai_response": "It is light-based energy production.",
            },
            files={"pdf_file": ("test.pdf", dummy_pdf, "application/pdf")}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify namespace generated and job status set to Processing
        assert data["pdf_namespace"] is not None
        assert data["pdf_status"] == "Processing"
        assert data["relevance_evaluation"] is not None
        assert data["accuracy_evaluation"] is not None

        # Verify background ingestion dispatched
        mock_ingest.assert_called_once()
