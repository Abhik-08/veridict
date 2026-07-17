"""
Comprehensive tests for the JudgeLLMService shared foundation.

All tests use mocked Gemini API calls — zero real quota consumed.
"""

import json
from unittest.mock import MagicMock, patch, PropertyMock

import pytest
from pydantic import BaseModel, Field

from app.core.exceptions import (
    JudgeLLMConfigurationError,
    JudgeLLMResponseValidationError,
    JudgeLLMUnavailableError,
)
from app.schemas.judge import JudgeLLMResult


# ──────────────────────────────────────────────
# Test output model (simulates a future Judge schema)
# ──────────────────────────────────────────────
class SampleJudgeOutput(BaseModel):
    """A minimal Judge output schema used for testing."""

    score: int = Field(..., ge=1, le=5, description="Score from 1-5.")
    reasoning: str = Field(..., description="Explanation for the score.")


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def _make_api_error(code: int, status: str = "", message: str = ""):
    """Create a mock google.genai.errors.APIError."""
    from google.genai.errors import APIError, ClientError, ServerError

    response_json = {
        "error": {
            "code": code,
            "status": status,
            "message": message,
        }
    }

    if 400 <= code < 500:
        return ClientError(code, response_json, None)
    elif 500 <= code < 600:
        return ServerError(code, response_json, None)
    else:
        return APIError(code, response_json, None)


def _make_success_response(data: dict) -> MagicMock:
    """Create a mock Gemini generate_content response."""
    mock_response = MagicMock()
    mock_response.text = json.dumps(data)
    return mock_response


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────
@pytest.fixture
def mock_settings():
    """Patch settings for all tests to avoid needing real env vars."""
    with patch("app.services.judge_llm_service.settings") as mock_s:
        mock_s.GOOGLE_API_KEY = "test-api-key"
        mock_s.JUDGE_PRIMARY_MODEL = "gemini-2.0-flash"
        mock_s.JUDGE_FALLBACK_MODELS = "gemini-2.0-flash-lite,gemini-1.5-flash"
        mock_s.JUDGE_MAX_RETRIES = 2
        mock_s.JUDGE_RETRY_BASE_DELAY = 0.01  # Fast retries for tests
        mock_s.JUDGE_REQUEST_TIMEOUT = 60
        mock_s.JUDGE_TEMPERATURE = 0.0
        yield mock_s


@pytest.fixture
def mock_client():
    """Patch the genai.Client so no real API calls are made."""
    with patch("app.services.judge_llm_service.genai.Client") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def service(mock_settings, mock_client):
    """Create a JudgeLLMService with mocked dependencies."""
    from app.services.judge_llm_service import JudgeLLMService

    svc = JudgeLLMService()
    return svc


# ──────────────────────────────────────────────
# 1. Primary model succeeds
# ──────────────────────────────────────────────
class TestPrimaryModelSuccess:
    def test_returns_validated_result(self, service, mock_client):
        """Primary model succeeds on first call — returns correct result."""
        mock_client.models.generate_content.return_value = _make_success_response(
            {"score": 4, "reasoning": "Good answer."}
        )

        result = service.evaluate("Test prompt", SampleJudgeOutput)

        assert isinstance(result, JudgeLLMResult)
        assert result.result.score == 4
        assert result.result.reasoning == "Good answer."
        assert result.model_used == "gemini-2.0-flash"
        assert mock_client.models.generate_content.call_count == 1


# ──────────────────────────────────────────────
# 2. Retryable rate-limit error → succeeds after retry
# ──────────────────────────────────────────────
class TestRetryOnRateLimit:
    def test_retries_on_429_then_succeeds(self, service, mock_client):
        """Primary model gets 429, retries, then succeeds on second attempt."""
        mock_client.models.generate_content.side_effect = [
            _make_api_error(429, "RESOURCE_EXHAUSTED", "Rate limit exceeded"),
            _make_success_response({"score": 3, "reasoning": "Average."}),
        ]

        result = service.evaluate("Test prompt", SampleJudgeOutput)

        assert result.result.score == 3
        assert result.model_used == "gemini-2.0-flash"
        assert mock_client.models.generate_content.call_count == 2


# ──────────────────────────────────────────────
# 3. Primary exhausts retries → fallback succeeds
# ──────────────────────────────────────────────
class TestFallbackAfterExhaustion:
    def test_fallback_model_succeeds(self, service, mock_client):
        """Primary model exhausts all retries, first fallback succeeds."""
        rate_limit_error = _make_api_error(
            429, "RESOURCE_EXHAUSTED", "Rate limit"
        )

        mock_client.models.generate_content.side_effect = [
            # Primary: 2 retries, all fail
            rate_limit_error,
            rate_limit_error,
            # Fallback 1: succeeds
            _make_success_response({"score": 5, "reasoning": "Excellent."}),
        ]

        result = service.evaluate("Test prompt", SampleJudgeOutput)

        assert result.result.score == 5
        assert result.model_used == "gemini-2.0-flash-lite"
        assert mock_client.models.generate_content.call_count == 3


# ──────────────────────────────────────────────
# 4. All models fail with retryable errors
# ──────────────────────────────────────────────
class TestAllModelsFail:
    def test_raises_unavailable_error(self, service, mock_client):
        """All 3 models exhaust retries → JudgeLLMUnavailableError."""
        rate_limit_error = _make_api_error(
            429, "RESOURCE_EXHAUSTED", "Rate limit"
        )

        # 3 models × 2 retries = 6 failures
        mock_client.models.generate_content.side_effect = [
            rate_limit_error
        ] * 6

        with pytest.raises(JudgeLLMUnavailableError) as exc_info:
            service.evaluate("Test prompt", SampleJudgeOutput)

        assert len(exc_info.value.attempted_models) == 3
        assert mock_client.models.generate_content.call_count == 6


# ──────────────────────────────────────────────
# 5. Non-retryable error does NOT trigger fallback
# ──────────────────────────────────────────────
class TestNonRetryableNoFallback:
    def test_auth_error_fails_immediately(self, service, mock_client):
        """401 authentication error fails immediately without fallback."""
        mock_client.models.generate_content.side_effect = _make_api_error(
            401, "UNAUTHENTICATED", "Invalid API key"
        )

        with pytest.raises(JudgeLLMConfigurationError) as exc_info:
            service.evaluate("Test prompt", SampleJudgeOutput)

        assert "401" in exc_info.value.message
        # Only 1 call — no fallback attempted
        assert mock_client.models.generate_content.call_count == 1

    def test_403_permission_denied_fails_immediately(self, service, mock_client):
        """403 permission denied fails immediately without fallback."""
        mock_client.models.generate_content.side_effect = _make_api_error(
            403, "PERMISSION_DENIED", "Access denied"
        )

        with pytest.raises(JudgeLLMConfigurationError):
            service.evaluate("Test prompt", SampleJudgeOutput)

        assert mock_client.models.generate_content.call_count == 1


# ──────────────────────────────────────────────
# 6. Invalid JSON response is handled
# ──────────────────────────────────────────────
class TestInvalidJSON:
    def test_non_json_response_raises_validation_error(self, service, mock_client):
        """LLM returns non-JSON text → JudgeLLMResponseValidationError."""
        mock_response = MagicMock()
        mock_response.text = "This is not JSON at all"
        mock_client.models.generate_content.return_value = mock_response

        with pytest.raises(JudgeLLMResponseValidationError):
            service.evaluate("Test prompt", SampleJudgeOutput)

    def test_empty_response_raises_validation_error(self, service, mock_client):
        """LLM returns empty text → JudgeLLMResponseValidationError."""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_client.models.generate_content.return_value = mock_response

        with pytest.raises(JudgeLLMResponseValidationError):
            service.evaluate("Test prompt", SampleJudgeOutput)


# ──────────────────────────────────────────────
# 7. Valid JSON but invalid Pydantic schema
# ──────────────────────────────────────────────
class TestInvalidPydanticSchema:
    def test_missing_required_field_raises_validation_error(
        self, service, mock_client
    ):
        """JSON is valid but missing required 'reasoning' field."""
        mock_client.models.generate_content.return_value = _make_success_response(
            {"score": 3}  # Missing 'reasoning'
        )

        with pytest.raises(JudgeLLMResponseValidationError):
            service.evaluate("Test prompt", SampleJudgeOutput)

    def test_wrong_type_raises_validation_error(self, service, mock_client):
        """JSON is valid but 'score' is a string instead of int."""
        mock_client.models.generate_content.return_value = _make_success_response(
            {"score": "not_a_number", "reasoning": "Test"}
        )

        with pytest.raises(JudgeLLMResponseValidationError):
            service.evaluate("Test prompt", SampleJudgeOutput)

    def test_out_of_range_score_raises_validation_error(self, service, mock_client):
        """JSON is valid but score=10 exceeds the max of 5."""
        mock_client.models.generate_content.return_value = _make_success_response(
            {"score": 10, "reasoning": "Too high"}
        )

        with pytest.raises(JudgeLLMResponseValidationError):
            service.evaluate("Test prompt", SampleJudgeOutput)


# ──────────────────────────────────────────────
# 8. model_used is correctly returned
# ──────────────────────────────────────────────
class TestModelUsedTracking:
    def test_primary_model_used_tracked(self, service, mock_client):
        """model_used reflects the primary model on direct success."""
        mock_client.models.generate_content.return_value = _make_success_response(
            {"score": 4, "reasoning": "Good."}
        )

        result = service.evaluate("Test prompt", SampleJudgeOutput)
        assert result.model_used == "gemini-2.0-flash"

    def test_fallback_model_used_tracked(self, service, mock_client):
        """model_used reflects the fallback model when primary fails."""
        rate_limit_error = _make_api_error(
            429, "RESOURCE_EXHAUSTED", "Rate limit"
        )

        mock_client.models.generate_content.side_effect = [
            # Primary: 2 retries all fail
            rate_limit_error,
            rate_limit_error,
            # Fallback 1: 2 retries all fail
            rate_limit_error,
            rate_limit_error,
            # Fallback 2: succeeds
            _make_success_response({"score": 2, "reasoning": "Poor."}),
        ]

        result = service.evaluate("Test prompt", SampleJudgeOutput)
        assert result.model_used == "gemini-1.5-flash"


# ──────────────────────────────────────────────
# 9. Duplicate model names are deduplicated
# ──────────────────────────────────────────────
class TestDuplicateModelDeduplication:
    def test_duplicate_models_are_removed(self, mock_client):
        """Duplicate model names in fallback list are not attempted twice."""
        with patch("app.services.judge_llm_service.settings") as mock_s:
            mock_s.GOOGLE_API_KEY = "test-api-key"
            mock_s.JUDGE_PRIMARY_MODEL = "gemini-2.0-flash"
            mock_s.JUDGE_FALLBACK_MODELS = (
                "gemini-2.0-flash,gemini-2.0-flash,gemini-1.5-flash"
            )
            mock_s.JUDGE_MAX_RETRIES = 2
            mock_s.JUDGE_RETRY_BASE_DELAY = 0.01
            mock_s.JUDGE_REQUEST_TIMEOUT = 60
            mock_s.JUDGE_TEMPERATURE = 0.0

            from app.services.judge_llm_service import JudgeLLMService

            svc = JudgeLLMService()

        # Should be deduplicated to 2 models, not 4
        assert svc.model_chain == ["gemini-2.0-flash", "gemini-1.5-flash"]
        assert len(svc.model_chain) == 2

        # Verify that with 2 models × 2 retries = 4 total attempts
        rate_limit_error = _make_api_error(429, "RESOURCE_EXHAUSTED", "Rate limit")
        mock_client.models.generate_content.side_effect = [rate_limit_error] * 4

        with pytest.raises(JudgeLLMUnavailableError) as exc_info:
            svc.evaluate("Test prompt", SampleJudgeOutput)

        assert mock_client.models.generate_content.call_count == 4
        assert len(exc_info.value.attempted_models) == 2


# ──────────────────────────────────────────────
# Additional edge cases
# ──────────────────────────────────────────────
class TestEdgeCases:
    def test_empty_prompt_raises_config_error(self, service, mock_client):
        """Empty prompt raises JudgeLLMConfigurationError."""
        with pytest.raises(JudgeLLMConfigurationError):
            service.evaluate("", SampleJudgeOutput)

    def test_whitespace_prompt_raises_config_error(self, service, mock_client):
        """Whitespace-only prompt raises JudgeLLMConfigurationError."""
        with pytest.raises(JudgeLLMConfigurationError):
            service.evaluate("   ", SampleJudgeOutput)

    def test_server_error_503_is_retryable(self, service, mock_client):
        """503 Service Unavailable is retried, then succeeds."""
        mock_client.models.generate_content.side_effect = [
            _make_api_error(503, "UNAVAILABLE", "Service temporarily unavailable"),
            _make_success_response({"score": 4, "reasoning": "OK."}),
        ]

        result = service.evaluate("Test prompt", SampleJudgeOutput)

        assert result.result.score == 4
        assert mock_client.models.generate_content.call_count == 2

    def test_no_models_configured_raises_config_error(self, mock_client):
        """No models configured raises JudgeLLMConfigurationError at init."""
        with patch("app.services.judge_llm_service.settings") as mock_s:
            mock_s.GOOGLE_API_KEY = "test-api-key"
            mock_s.JUDGE_PRIMARY_MODEL = ""
            mock_s.JUDGE_FALLBACK_MODELS = ""
            mock_s.JUDGE_MAX_RETRIES = 2
            mock_s.JUDGE_RETRY_BASE_DELAY = 0.01
            mock_s.JUDGE_REQUEST_TIMEOUT = 60
            mock_s.JUDGE_TEMPERATURE = 0.0

            from app.services.judge_llm_service import JudgeLLMService

            with pytest.raises(JudgeLLMConfigurationError):
                JudgeLLMService()
