"""
Veridict Batch Response Validator.

Validates structured JSON output returned by Gemini LLM against schema,
score ranges, confidence bounds, and item ID presence.
"""

import json
import re
from typing import Any


class BatchResponseValidator:
    """Validates raw LLM response text into validated evaluation result dicts."""

    @staticmethod
    def validate_and_parse(raw_text: str) -> list[dict[str, Any]]:
        """
        Clean, parse, and validate JSON output from LLM.
        """
        if not raw_text or not raw_text.strip():
            raise ValueError("LLM returned empty response text.")

        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE).strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as err:
            raise ValueError(f"Failed to parse LLM JSON response: {str(err)}")

        if not isinstance(parsed, list):
            raise ValueError("LLM response must be a JSON array of evaluation objects.")

        if not parsed:
            raise ValueError("LLM response array is empty.")

        return [BatchResponseValidator._validate_single_item(idx, item) for idx, item in enumerate(parsed)]

    @staticmethod
    def _validate_single_item(idx: int, item: Any) -> dict[str, Any]:
        if not isinstance(item, dict):
            raise ValueError(f"Batch item at index {idx} is not a valid JSON object.")

        item_id = item.get("id")
        if not item_id:
            raise ValueError(f"Batch item at index {idx} is missing required field 'id'.")

        for score_key in ["relevance_score", "accuracy_score", "completeness_score"]:
            score_val = item.get(score_key)
            if score_val is None or not (1 <= float(score_val) <= 5):
                raise ValueError(f"Item '{item_id}': '{score_key}' must be between 1 and 5 (got {score_val}).")

        hal_val = item.get("hallucination_score")
        if hal_val is not None and not (1 <= float(hal_val) <= 5):
            raise ValueError(f"Item '{item_id}': 'hallucination_score' must be between 1 and 5 or null (got {hal_val}).")

        reasoning = item.get("reasoning", "")
        if not isinstance(reasoning, str):
            reasoning = str(reasoning)

        return {
            "id": str(item_id),
            "relevance_score": float(item["relevance_score"]),
            "accuracy_score": float(item["accuracy_score"]),
            "hallucination_score": float(hal_val) if hal_val is not None else None,
            "completeness_score": float(item["completeness_score"]),
            "reasoning": reasoning.strip(),
        }
