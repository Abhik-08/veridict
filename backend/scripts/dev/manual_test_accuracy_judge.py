"""
Manual integration test for the AccuracyJudge agent.

This test calls the live Gemini API using the configured key and settings.
It runs test cases to sanity check the accuracy judge.
"""

import sys
import os

# Add parent directory to sys.path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.accuracy_judge import AccuracyJudge
from app.services.judge_llm_service import JudgeLLMService


def run_test_case(judge: AccuracyJudge, label: str, question: str, ai_response: str, reference_answer: str | None = None, retrieved_evidence: str | None = None) -> None:
    print("\n==================================================")
    print(f"RUNNING MANUAL CASE {label}")
    print("==================================================")
    print(f"Question:           {question}")
    print(f"AI Response:        {ai_response}")
    print(f"Reference Answer:   {reference_answer or 'None'}")
    print(f"Retrieved Evidence: {retrieved_evidence or 'None'}")
    print("--------------------------------------------------")
    
    try:
        result = judge.evaluate_accuracy(
            question=question,
            ai_response=ai_response,
            reference_answer=reference_answer,
            retrieved_evidence=retrieved_evidence
        )
        print("STATUS:      SUCCESS")
        print(f"Score:       {result.result.accuracy_score} / 5")
        print(f"Reasoning:   {result.result.reasoning}")
        print(f"Model Used:  {result.model_used}")
    except Exception as e:
        print("STATUS:      FAILED")
        print(f"Error:       {type(e).__name__}: {e}")


def main() -> None:
    print("Initializing Accuracy Judge and Live JudgeLLMService...")
    # Initialize the live service
    try:
        judge_service = JudgeLLMService()
        judge = AccuracyJudge(judge_llm_service=judge_service)
    except Exception as e:
        print(f"Failed to initialize service: {e}")
        print("Please check your GOOGLE_API_KEY environment variable configuration.")
        return

    # Case A: Completely Accurate
    run_test_case(
        judge=judge,
        label="A (Completely Accurate)",
        question="What is the capital of France?",
        ai_response="The capital of France is Paris.",
        reference_answer="Paris",
        retrieved_evidence="France is a country in Europe. Its capital city is Paris."
    )

    # Case B: Partially Accurate (Hallucinated facts)
    run_test_case(
        judge=judge,
        label="B (Partially Accurate)",
        question="Who was the first president of the United States?",
        ai_response="George Washington was the first president of the United States, and he served for 12 years.",
        reference_answer="George Washington.",
        retrieved_evidence="George Washington served as the first president of the United States from 1789 to 1797 (8 years)."
    )

    # Case C: Completely Inaccurate
    run_test_case(
        judge=judge,
        label="C (Completely Inaccurate)",
        question="What is the capital of France?",
        ai_response="The capital of France is Berlin.",
        reference_answer="Paris",
        retrieved_evidence="France is a country in Europe. Its capital city is Paris."
    )
    
    # Case D: No Evidence Provided
    run_test_case(
        judge=judge,
        label="D (No Evidence)",
        question="What is the speed of light?",
        ai_response="The speed of light is approximately 299,792 kilometers per second.",
        reference_answer=None,
        retrieved_evidence=None
    )


if __name__ == "__main__":
    main()
