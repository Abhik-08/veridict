"""
Veridict Batch LLM Evaluation Service.

Evaluates a batch of up to 3 QA pairs in ONE combined Gemini API call.
Parses structured JSON containing dimension scores and reasoning
for each QA pair independently.
"""

import logging
import time
from typing import Any
from google import genai
from google.genai import types

from app.core.config import settings
from app.services.batch_prompt_builder import BatchPromptBuilder
from app.services.batch_response_validator import BatchResponseValidator

logger = logging.getLogger(__name__)


class BatchLLMService:
    """Invokes Gemini LLM with a combined multi-QA batch prompt."""

    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    def evaluate_batch(
        self, batch_items: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Evaluate a batch of up to 3 QA pairs in a single Gemini call.
        """
        if not batch_items:
            return []

        full_prompt = BatchPromptBuilder.build_prompt(batch_items)
        models_to_try = [
            settings.JUDGE_PRIMARY_MODEL,
            *[m.strip() for m in settings.JUDGE_FALLBACK_MODELS.split(",") if m.strip()],
        ]

        last_error = None
        for model_name in models_to_try:
            for attempt in range(settings.MAX_BATCH_RETRIES + 1):
                try:
                    return self._execute_single_attempt(model_name, full_prompt, attempt, len(batch_items))
                except Exception as exc:
                    last_error = exc
                    time.sleep(settings.JUDGE_RETRY_BASE_DELAY * (2 ** attempt))

        raise RuntimeError(
            f"All Batch LLM attempts failed. Last error: {str(last_error)}"
        )

    def _execute_single_attempt(
        self, model_name: str, full_prompt: str, attempt: int, num_items: int
    ) -> list[dict[str, Any]]:
        logger.info(
            f"Invoking Batch LLM model '{model_name}' (attempt {attempt + 1}/{settings.MAX_BATCH_RETRIES + 1}) for batch of {num_items} items"
        )
        response = self.client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=settings.JUDGE_TEMPERATURE,
            ),
        )

        raw_text = (getattr(response, "text", "") or "").strip()
        return BatchResponseValidator.validate_and_parse(raw_text)
