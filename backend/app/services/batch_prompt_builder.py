"""
Veridict Batch Prompt Builder.

Isolates prompt generation and formatting from LLM execution code.
"""

from typing import Any


BATCH_EVALUATION_SYSTEM_PROMPT = """
You are Veridict Batch Evaluator, an enterprise AI response quality evaluation system.

You will be given a batch of up to 3 QA pairs. Evaluate EACH QA pair INDEPENDENTLY on 4 quality dimensions:
1. Relevance (1 to 5): How well the AI Response directly answers the user Question.
2. Accuracy (1 to 5): Factual correctness against provided Evidence/Reference or general facts.
3. Hallucination (1 to 5): 5 = Fully Grounded (no ungrounded claims), 1 = Highly Hallucinated. (Set to null if status is INSUFFICIENT_EVIDENCE).
4. Completeness (1 to 5): Coverage of all required aspects of the Question.

CRITICAL MANDATORY INSTRUCTION:
- Return ONLY a valid JSON array of evaluation objects.
- Do NOT include markdown code fences (```json or ```).
- Do NOT include conversational preambles or postscripts.
- Do NOT compare or rank items in the batch. Evaluate each item independently.
- Provide a concise 1-sentence reasoning summary for each item.

REQUIRED JSON FORMAT:
[
  {
    "id": "QA-01",
    "relevance_score": 5,
    "accuracy_score": 5,
    "hallucination_score": 5,
    "completeness_score": 5,
    "confidence": 0.95,
    "reasoning": "Response directly addresses all aspects of the query accurately."
  }
]
"""


class BatchPromptBuilder:
    """Constructs structured prompts for multi-QA Gemini evaluation batches."""

    @staticmethod
    def build_prompt(batch_items: list[dict[str, Any]]) -> str:
        """
        Format batch items into system prompt text.

        Args:
            batch_items: List of item dicts with keys: id, question, ai_response, reference_answer, evidence_text

        Returns:
            str: Full formatted prompt string.
        """
        prompt_text = "EVALUATION BATCH:\n\n"
        for item in batch_items:
            prompt_text += f"--- ITEM ID: {item['id']} ---\n"
            prompt_text += f"QUESTION: {item['question']}\n"
            prompt_text += f"AI RESPONSE: {item['ai_response']}\n"
            if item.get("reference_answer"):
                prompt_text += f"REFERENCE ANSWER: {item['reference_answer']}\n"
            if item.get("evidence_text"):
                prompt_text += f"EVIDENCE CONTEXT: {item['evidence_text']}\n"
            prompt_text += "\n"

        return f"{BATCH_EVALUATION_SYSTEM_PROMPT.strip()}\n\n{prompt_text}"
