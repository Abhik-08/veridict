"""
Manual integration test for the RelevanceJudge agent.

This test calls the live Gemini API using the configured key and settings.
It runs three test cases (A, B, and C) to sanity check the relevance judge.
"""

import sys
import os

# Add parent directory to sys.path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agents.relevance_judge import RelevanceJudge
from app.services.judge_llm_service import JudgeLLMService


def run_test_case(judge: RelevanceJudge, label: str, question: str, ai_response: str) -> None:
    print("\n==================================================")
    print(f"RUNNING MANUAL CASE {label}")
    print("==================================================")
    print(f"Question:   {question}")
    print(f"AI Response: {ai_response}")
    print("--------------------------------------------------")
    
    try:
        result = judge.evaluate_relevance(question, ai_response)
        print("STATUS:      SUCCESS")
        print(f"Score:       {result.result.relevance_score} / 5")
        print(f"Reasoning:   {result.result.reasoning}")
        print(f"Model Used:  {result.model_used}")
    except Exception as e:
        print("STATUS:      FAILED")
        print(f"Error:       {type(e).__name__}: {e}")


def main() -> None:
    print("Initializing Relevance Judge and Live JudgeLLMService...")
    # Initialize the live service
    try:
        judge_service = JudgeLLMService()
        judge = RelevanceJudge(judge_llm_service=judge_service)
    except Exception as e:
        print(f"Failed to initialize service: {e}")
        print("Please check your GOOGLE_API_KEY environment variable configuration.")
        return

    # Case A: Highly Relevant
    run_test_case(
        judge=judge,
        label="A (Highly Relevant)",
        question="What is photosynthesis?",
        ai_response="Photosynthesis is the process by which plants use light energy to produce chemical energy."
    )

    # Case B: Completely Irrelevant
    run_test_case(
        judge=judge,
        label="B (Irrelevant)",
        question="What is photosynthesis?",
        ai_response="The Roman Empire was one of the largest civilizations in ancient history."
    )

    # Case C: Factually Inaccurate but Highly Relevant
    run_test_case(
        judge=judge,
        label="C (Factually Inaccurate but Highly Relevant)",
        question="What is the capital of France?",
        ai_response="The capital of France is Berlin."
    )


if __name__ == "__main__":
    main()
