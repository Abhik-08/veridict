"""
Veridict Batch Input Validation Layer.

Performs pre-evaluation validation on parsed BatchQAPairInput datasets, checking
for empty fields, duplicates, and row limit constraints.
"""

import logging
from app.core.config import settings
from app.schemas.batch_evaluation import BatchQAPairInput

logger = logging.getLogger(__name__)


class BatchInputValidator:
    """Validates BatchQAPairInput datasets before sending to evaluation engine."""

    @staticmethod
    def validate(items: list[BatchQAPairInput]) -> list[BatchQAPairInput]:
        """
        Validate list of BatchQAPairInput items.

        Raises:
            ValueError: If items are empty, exceed limit, contain empty required fields, or duplicates.
        """
        if not items:
            raise ValueError("Dataset contains no QA pairs to evaluate.")

        if len(items) > settings.MAX_BATCH_ROWS:
            raise ValueError(
                f"Batch limit exceeded. Maximum allowed is {settings.MAX_BATCH_ROWS} QA pairs (found {len(items)} rows)."
            )

        seen_questions: set[str] = set()
        validated_items: list[BatchQAPairInput] = []

        for idx, item in enumerate(items, start=1):
            if not item.question or not item.question.strip():
                raise ValueError(f"Row {idx} ({item.id}): Question cannot be empty.")

            if not item.ai_response or not item.ai_response.strip():
                raise ValueError(f"Row {idx} ({item.id}): AI Response cannot be empty.")

            clean_q = item.question.strip().lower()
            if clean_q in seen_questions:
                logger.warning(f"Duplicate question detected at row {idx} ({item.id}): '{item.question[:50]}...'")

            seen_questions.add(clean_q)
            validated_items.append(item)

        return validated_items
