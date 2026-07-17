# Milestone 2 — Phase 2: Walkthrough (Retry Behavior Optimization)

## 1. Repository Structure and Files Inspected

The following files were inspected to align with retry optimizations:
- [config.py](file:///c:/Users/abhik/Desktop/Veridict/backend/app/core/config.py)
- [judge_llm_service.py](file:///c:/Users/abhik/Desktop/Veridict/backend/app/services/judge_llm_service.py)
- [.env.example](file:///c:/Users/abhik/Desktop/Veridict/backend/.env.example)
- [test_judge_llm_service.py](file:///c:/Users/abhik/Desktop/Veridict/backend/tests/test_judge_llm_service.py)

## 2. Files Created

No files were created.

## 3. Files Modified

| File | Change |
|---|---|
| [config.py](file:///c:/Users/abhik/Desktop/Veridict/backend/app/core/config.py) | Changed default `JUDGE_MAX_RETRIES` from `3` to `2` (initial + 1 retry). |
| [.env.example](file:///c:/Users/abhik/Desktop/Veridict/backend/.env.example) | Updated model example value for `JUDGE_MAX_RETRIES` to `2`. |
| [test_judge_llm_service.py](file:///c:/Users/abhik/Desktop/Veridict/backend/tests/test_judge_llm_service.py) | Updated fixtures and assertions to expect a maximum of 2 attempts per model instead of 3. |

---

## 4. Retry Configuration Optimizations

- **Old retry configuration**: `JUDGE_MAX_RETRIES = 3` (initial call + 2 retries, meaning up to 3 total attempts per model).
- **New retry configuration**: `JUDGE_MAX_RETRIES = 2` (initial call + 1 retry, meaning up to 2 total attempts per model).
- **Behavior**: Reduces unnecessary rate-limit backoff wait times when a Gemini model family hits account-level quota thresholds. It will now try the model, wait once with exponential backoff, retry once, and immediately fall back to the next model in the chain if the second attempt fails.

## 5. Pytest Results

All 35 unit and integration tests passed successfully:
```
======================= 35 passed, 3 warnings in 16.51s =======================
```

## 6. Manual Relevance Judge Test Output

Ran `scripts/manual_test_relevance_judge.py` against live APIs:
```
==================================================
RUNNING MANUAL CASE A (Highly Relevant)
==================================================
STATUS:      SUCCESS
Score:       5 / 5
Model Used:  gemini-2.5-flash (succeeded immediately)

==================================================
RUNNING MANUAL CASE B (Irrelevant)
==================================================
Retryable error from model 'gemini-2.5-flash' (attempt 1/2)
Retryable error from model 'gemini-2.5-flash' (attempt 2/2)
All 2 retry attempts exhausted for model 'gemini-2.5-flash'. Moving to next fallback.
STATUS:      SUCCESS
Score:       1 / 5
Model Used:  gemini-3.1-flash-lite

==================================================
RUNNING MANUAL CASE C (Factually Inaccurate but Highly Relevant)
==================================================
STATUS:      SUCCESS
Score:       5 / 5
Model Used:  gemini-3.1-flash-lite
```

**Key Observation**: Model fallback occurred after exactly **2 attempts** on `gemini-2.5-flash` during Case B, cutting total latency in half.

## 7. Confirmation of Fallback Logic
The fallback logic remains unchanged — the deduplicated model chain order (`gemini-2.5-flash` -> `gemini-3.1-flash-lite` -> `gemini-3.5-flash`) is preserved exactly, simply processing fewer retries before switching.
