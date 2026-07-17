"""
End-to-End API verification script.

Calls the live FastAPI /evaluate endpoint directly with different test inputs
to verify that RAG retrieval, RelevanceJudge, and JudgeLLMService integrate
correctly under the live Gemini configuration.
"""

import urllib.request
import urllib.parse
import json
import time

def run_e2e_case(label: str, question: str, ai_response: str) -> None:
    print(f"\n==================================================")
    print(f"RUNNING E2E API CASE {label}")
    print(f"==================================================")
    print(f"Question:   {question}")
    print(f"AI Response: {ai_response}")
    print(f"--------------------------------------------------")
    
    # Prepare form payload
    data = {
        "question": question,
        "ai_response": ai_response
    }
    encoded_data = urllib.parse.urlencode(data).encode("utf-8")
    
    # Build request
    req = urllib.request.Request(
        url="http://localhost:8000/evaluate",
        data=encoded_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    start_time = time.time()
    try:
        with urllib.request.urlopen(req) as response:
            latency = time.time() - start_time
            result = json.loads(response.read().decode("utf-8"))
            print(f"STATUS:             SUCCESS")
            print(f"Latency:            {latency:.2f}s")
            
            # Check retrieval results
            chunks = result.get("retrieved_chunks", [])
            print(f"Retrieved Chunks:   {len(chunks)} chunks")
            if chunks:
                print(f"  First Chunk ID:   {chunks[0].get('id')}")
                print(f"  First Chunk Doc:  {chunks[0].get('document_id')}")
                print(f"  First Chunk Score: {chunks[0].get('score')}")
            
            # Check relevance results
            relevance = result.get("relevance_evaluation")
            if relevance:
                print(f"Relevance Score:    {relevance.get('relevance_score')} / 5")
                print(f"Relevance Label:    {get_relevance_label_text(relevance.get('relevance_score'))}")
                print(f"Reasoning:          {relevance.get('reasoning')}")
                print(f"Model Used:         {relevance.get('model_used')}")
            else:
                print("Relevance Outcome:  None (Evaluation Failed)")
                
    except Exception as e:
        print(f"STATUS:             FAILED")
        print(f"Error:              {type(e).__name__}: {e}")


def get_relevance_label_text(score: int) -> str:
    labels = {
        5: "Highly Relevant",
        4: "Mostly Relevant",
        3: "Partially Relevant",
        2: "Mostly Irrelevant",
        1: "Irrelevant"
    }
    return labels.get(score, "Unknown")


def main() -> None:
    print("Starting End-to-End API verification tests against http://localhost:8000/evaluate ...")
    
    # Test A: Highly Relevant
    run_e2e_case(
        label="A (Highly Relevant)",
        question="What is artificial intelligence?",
        ai_response="Artificial intelligence is a field of computer science focused on creating systems capable of tasks that normally require human intelligence."
    )
    
    # Test B: Irrelevant
    run_e2e_case(
        label="B (Irrelevant)",
        question="What is artificial intelligence?",
        ai_response="The Pacific Ocean is the largest ocean on Earth."
    )
    
    # Test C: Factually Inaccurate but Highly Relevant
    run_e2e_case(
        label="C (Factually Inaccurate but Highly Relevant)",
        question="Who wrote Hamlet?",
        ai_response="Hamlet was written by Charles Dickens."
    )
    
    # Test D: Completely New Arbitrary Question
    run_e2e_case(
        label="D (Arbitrary - Microwave Heating)",
        question="How do microwave ovens heat food?",
        ai_response="Microwave ovens heat food by emitting electromagnetic radiation that causes water molecules inside the food to vibrate, producing heat."
    )


if __name__ == "__main__":
    main()
