"""
Custom exceptions for the Judge LLM infrastructure.

Hierarchy:
    JudgeLLMError (base)
    ├── JudgeLLMConfigurationError    — invalid config, bad schema, programming errors
    ├── JudgeLLMResponseValidationError — valid JSON but fails Pydantic validation
    └── JudgeLLMUnavailableError      — all configured models exhausted after retries
"""


class JudgeLLMError(Exception):
    """Base exception for all Judge LLM errors."""

    def __init__(self, message: str = "Judge LLM error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


class JudgeLLMConfigurationError(JudgeLLMError):
    """
    Raised when the Judge LLM service encounters a non-retryable
    configuration or programming error.

    Examples:
    - Invalid API key / authentication failure
    - Malformed request parameters
    - Invalid Pydantic output schema
    """

    def __init__(self, message: str = "Judge LLM configuration error.") -> None:
        super().__init__(message)


class JudgeLLMResponseValidationError(JudgeLLMError):
    """
    Raised when the Gemini API returns valid JSON that does not
    conform to the expected Pydantic output model.
    """

    def __init__(
        self,
        message: str = "Judge LLM response validation failed.",
        raw_response: str | None = None,
    ) -> None:
        self.raw_response = raw_response
        super().__init__(message)


class JudgeLLMUnavailableError(JudgeLLMError):
    """
    Raised when all configured Judge LLM models have been exhausted
    due to transient provider errors (rate limits, quota, service outages).
    """

    def __init__(
        self,
        message: str = "All configured Judge LLM models are currently unavailable.",
        attempted_models: list[str] | None = None,
    ) -> None:
        self.attempted_models = attempted_models or []
        super().__init__(message)
