"""
Shared Judge LLM Service.

Provides reusable infrastructure for all Judge Agents to communicate
with the Gemini generative API. Handles model selection, fallback chains,
retry logic with exponential backoff, structured JSON output, and
Pydantic validation.
"""

import json
import logging
import random
import time
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError, ServerError

from app.core.config import settings
from app.core.exceptions import (
    JudgeLLMConfigurationError,
    JudgeLLMResponseValidationError,
    JudgeLLMUnavailableError,
)
from app.schemas.judge import JudgeLLMResult

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# ──────────────────────────────────────────────
# HTTP status codes / gRPC statuses that are
# safe to retry (transient provider errors).
# ──────────────────────────────────────────────
_RETRYABLE_STATUS_CODES: set[int] = {429, 500, 503}

_RETRYABLE_GRPC_STATUSES: set[str] = {
    "RESOURCE_EXHAUSTED",
    "UNAVAILABLE",
    "DEADLINE_EXCEEDED",
    "INTERNAL",
}


def _is_retryable(error: APIError) -> bool:
    """
    Classify whether an APIError is transient and safe to retry.

    Returns True for rate-limit, quota, and temporary service errors.
    Returns False for authentication, permission, or malformed-request errors.
    """
    # Check HTTP status code
    if error.code in _RETRYABLE_STATUS_CODES:
        return True

    # Check gRPC / API status string
    if error.status and error.status.upper() in _RETRYABLE_GRPC_STATUSES:
        return True

    # Check message for common rate-limit phrases
    if error.message:
        message_lower = error.message.lower()
        if any(
            phrase in message_lower
            for phrase in ("rate limit", "quota", "resource exhausted")
        ):
            return True

    return False


class JudgeLLMService:
    """
    Reusable service for sending evaluation prompts to the Gemini
    generative API and receiving validated, structured Pydantic responses.

    Features:
    - Configurable primary model with ordered fallbacks
    - Exponential-backoff retries for transient failures
    - Automatic model fallback on exhaustion/unavailability
    - Structured JSON output via response_schema
    - Pydantic validation of LLM responses
    - model_used tracking for scoring-consistency audits
    """

    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.temperature = settings.JUDGE_TEMPERATURE
        self.max_retries = settings.JUDGE_MAX_RETRIES
        self.base_delay = settings.JUDGE_RETRY_BASE_DELAY
        self.request_timeout = settings.JUDGE_REQUEST_TIMEOUT

        # Build deduplicated ordered model chain
        self.model_chain = self._build_model_chain()

        if not self.model_chain:
            raise JudgeLLMConfigurationError(
                "No Judge LLM models configured. "
                "Set JUDGE_PRIMARY_MODEL and/or JUDGE_FALLBACK_MODELS."
            )

        logger.info(
            "JudgeLLMService initialized — model chain: %s",
            self.model_chain,
        )

    def _build_model_chain(self) -> list[str]:
        """
        Build an ordered, deduplicated list of model names from
        the primary model and fallback models configuration.
        """
        seen: set[str] = set()
        chain: list[str] = []

        # Primary model
        primary = settings.JUDGE_PRIMARY_MODEL.strip()
        if primary:
            seen.add(primary)
            chain.append(primary)

        # Fallback models (comma-separated)
        fallback_raw = settings.JUDGE_FALLBACK_MODELS.strip()
        if fallback_raw:
            for model_name in fallback_raw.split(","):
                name = model_name.strip()
                if name and name not in seen:
                    seen.add(name)
                    chain.append(name)

        return chain

    def evaluate(
        self,
        prompt: str,
        output_model: Type[T],
    ) -> JudgeLLMResult[T]:
        """
        Send an evaluation prompt to the Gemini generative API and
        return a validated, structured Pydantic result.

        Iterates through the configured model chain. For each model,
        retries transient failures with exponential backoff before
        moving to the next fallback model.

        Args:
            prompt: The evaluation prompt to send to the LLM.
            output_model: Pydantic BaseModel class defining the
                          expected structured output schema.

        Returns:
            JudgeLLMResult containing the validated result and
            the model name that produced it.

        Raises:
            JudgeLLMConfigurationError: Non-retryable config/auth error.
            JudgeLLMResponseValidationError: LLM returned invalid output.
            JudgeLLMUnavailableError: All models exhausted.
        """
        if not prompt or not prompt.strip():
            raise JudgeLLMConfigurationError("Evaluation prompt cannot be empty.")

        logger.info(
            "Judge LLM request started — output_model=%s, model_chain=%s",
            output_model.__name__,
            self.model_chain,
        )

        last_error: Exception | None = None

        for model_name in self.model_chain:
            try:
                result = self._call_model_with_retries(
                    model_name=model_name,
                    prompt=prompt,
                    output_model=output_model,
                )
                return result

            except (JudgeLLMConfigurationError, JudgeLLMResponseValidationError):
                # Non-retryable — do not try the next model
                raise

            except JudgeLLMUnavailableError as exc:
                # This model exhausted its retries — try next
                logger.warning(
                    "Model '%s' exhausted retries. Moving to next fallback.",
                    model_name,
                )
                last_error = exc
                continue

        # All models exhausted
        raise JudgeLLMUnavailableError(
            message="All configured Judge LLM models are currently unavailable.",
            attempted_models=list(self.model_chain),
        )

    def _call_model_with_retries(
        self,
        model_name: str,
        prompt: str,
        output_model: Type[T],
    ) -> JudgeLLMResult[T]:
        """
        Attempt to call a single Gemini model with exponential-backoff
        retries for transient failures.

        Args:
            model_name: Gemini model identifier.
            prompt: The evaluation prompt.
            output_model: Expected Pydantic output schema.

        Returns:
            JudgeLLMResult on success.

        Raises:
            JudgeLLMConfigurationError: Non-retryable error.
            JudgeLLMResponseValidationError: Invalid structured output.
            JudgeLLMUnavailableError: All retry attempts exhausted.
        """
        logger.info("Attempting model: '%s'", model_name)

        for attempt in range(self.max_retries):
            try:
                return self._call_model(
                    model_name=model_name,
                    prompt=prompt,
                    output_model=output_model,
                )

            except APIError as exc:
                if not _is_retryable(exc):
                    # Non-retryable API error — fail immediately
                    logger.error(
                        "Non-retryable API error from model '%s': "
                        "code=%s status=%s message=%s",
                        model_name,
                        exc.code,
                        exc.status,
                        exc.message,
                    )
                    raise JudgeLLMConfigurationError(
                        f"Non-retryable error from Gemini API: "
                        f"{exc.code} {exc.status} — {exc.message}"
                    ) from exc

                # Retryable — apply exponential backoff
                delay = self._compute_backoff_delay(attempt)
                logger.warning(
                    "Retryable error from model '%s' (attempt %d/%d): "
                    "code=%s status=%s — retrying in %.2fs",
                    model_name,
                    attempt + 1,
                    self.max_retries,
                    exc.code,
                    exc.status,
                    delay,
                )
                time.sleep(delay)

            except (json.JSONDecodeError, KeyError, TypeError, IndexError) as exc:
                # Malformed response — treat as validation error
                logger.error(
                    "Failed to parse response from model '%s': %s",
                    model_name,
                    exc,
                )
                raise JudgeLLMResponseValidationError(
                    message=f"Failed to parse LLM response: {exc}",
                    raw_response=None,
                ) from exc

            except ValidationError as exc:
                # Pydantic validation failure
                logger.error(
                    "Pydantic validation failed for model '%s' response: %s",
                    model_name,
                    exc,
                )
                raise JudgeLLMResponseValidationError(
                    message=f"LLM response failed schema validation: {exc}",
                    raw_response=None,
                ) from exc

        # All retry attempts exhausted for this model
        logger.warning(
            "All %d retry attempts exhausted for model '%s'.",
            self.max_retries,
            model_name,
        )
        raise JudgeLLMUnavailableError(
            message=f"Model '{model_name}' exhausted all retry attempts.",
            attempted_models=[model_name],
        )

    def _call_model(
        self,
        model_name: str,
        prompt: str,
        output_model: Type[T],
    ) -> JudgeLLMResult[T]:
        """
        Make a single call to the Gemini generative API.

        Requests structured JSON output matching the provided Pydantic
        model schema, parses and validates the response.

        Args:
            model_name: Gemini model identifier.
            prompt: The evaluation prompt.
            output_model: Expected Pydantic output schema.

        Returns:
            JudgeLLMResult on success.

        Raises:
            APIError: On any Gemini API error.
            json.JSONDecodeError: If response text is not valid JSON.
            ValidationError: If JSON does not match the Pydantic schema.
        """
        config = types.GenerateContentConfig(
            temperature=self.temperature,
            response_mime_type="application/json",
            response_schema=output_model,
        )

        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config,
        )

        # Extract text from response
        raw_text = response.text
        if not raw_text or not raw_text.strip():
            raise JudgeLLMResponseValidationError(
                message="Gemini returned an empty response.",
                raw_response=raw_text,
            )

        # Parse JSON
        parsed = json.loads(raw_text)

        # Validate with Pydantic
        validated = output_model.model_validate(parsed)

        logger.info(
            "Judge LLM call succeeded — model_used='%s'",
            model_name,
        )

        return JudgeLLMResult[output_model](
            result=validated,
            model_used=model_name,
        )

    def _compute_backoff_delay(self, attempt: int) -> float:
        """
        Compute exponential backoff delay with random jitter.

        Pattern: base_delay * 2^attempt + random(0, 0.5)

        Args:
            attempt: Zero-based retry attempt number.

        Returns:
            Delay in seconds.
        """
        delay = self.base_delay * (2 ** attempt)
        jitter = random.uniform(0, 0.5)
        return delay + jitter
