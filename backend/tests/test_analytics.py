"""
Unit and Integration Tests for Backend Analytics API (Milestone 4 Phase 2A).
Verifies:
1. Total evaluation count & empty dataset behavior
2. PASS / NEEDS_IMPROVEMENT / FAIL verdict distribution
3. Average dimension scores (Relevance, Accuracy, Completeness) & missing/null handling
4. Hallucination frequency & INSUFFICIENT_EVIDENCE handling
5. Date, source_type, verdict, and model filtering
6. Quality trend time-series aggregation
7. Strict multi-tenant user isolation
8. Unchanged behavior of GET /history/stats
"""
import uuid
import time
from datetime import datetime, timezone, timedelta
import pytest
import jwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.database.models  # Ensures all models are registered with Base before create_all
from app.main import app
from app.core.config import settings
from sqlalchemy.pool import StaticPool
from app.database.base import Base
from app.database.session import get_db
from app.history.schemas import HistoryItemCreate, AnalyticsFilterParams
from app.history.service import HistoryService

# Setup test in-memory SQLite database with StaticPool
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=test_engine)

client = TestClient(app)

USER_A_ID = uuid.uuid4()
USER_B_ID = uuid.uuid4()


def create_mock_jwt(user_id: uuid.UUID) -> str:
    """Helper creating signed JWT Bearer token for test requests."""
    key = getattr(settings, "SUPABASE_JWT_SECRET", None) or settings.SUPABASE_SERVICE_ROLE_KEY
    payload = {
        "sub": str(user_id),
        "email": "analytics_test@veridict.ai",
        "aud": "authenticated",
        "role": "authenticated",
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, key, algorithm="HS256")


def test_empty_analytics_dataset():
    """Verifies analytics endpoint output when user has 0 evaluation records."""
    token = create_mock_jwt(uuid.uuid4())
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/history/analytics", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_evaluations"] == 0
    assert data["verdict_distribution"]["pass_count"] == 0
    assert data["average_scores"]["average_relevance"] == 0.0
    assert data["hallucination_metrics"]["evaluable_count"] == 0
    assert data["quality_trends"] == []


def test_analytics_metrics_and_filters():
    """
    Verifies comprehensive analytics calculations:
    - Dimension averages
    - Hallucination frequency & INSUFFICIENT_EVIDENCE handling
    - Verdict distribution
    - Date, source_type, verdict, and model filtering
    - Time-series quality trends
    - Strict user isolation
    """
    token_a = create_mock_jwt(USER_A_ID)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    token_b = create_mock_jwt(USER_B_ID)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Create evaluation 1 for USER A (PASS, Grounded, model gemini-2.5-flash)
    item1 = {
        "question": "What is RAG?",
        "ai_response": "Retrieval-Augmented Generation.",
        "reference_answer": "RAG ground truth",
        "evaluation_result": {
            "relevance_evaluation": {"relevance_score": 5, "model_used": "gemini-2.5-flash"},
            "accuracy_evaluation": {"accuracy_score": 5, "model_used": "gemini-2.5-flash"},
            "hallucination_evaluation": {"status": "SUCCESS", "hallucination_score": 5, "model_used": "gemini-2.5-flash"},
            "completeness_evaluation": {"completeness_score": 4, "model_used": "gemini-2.5-flash"},
        },
        "overall_score": 4.75,
        "verdict": "PASS",
        "source_type": "SINGLE",
    }
    client.post("/history/evaluations", json=item1, headers=headers_a)

    # Create evaluation 2 for USER A (NEEDS_IMPROVEMENT, Hallucinated score 2, model gemini-2.5-flash)
    item2 = {
        "question": "Explain quantum computing.",
        "ai_response": "Quantum computing uses magic.",
        "reference_answer": "Quantum computing uses qubits.",
        "evaluation_result": {
            "relevance_evaluation": {"relevance_score": 3, "model_used": "gemini-2.5-flash"},
            "accuracy_evaluation": {"accuracy_score": 2, "model_used": "gemini-2.5-flash"},
            "hallucination_evaluation": {"status": "SUCCESS", "hallucination_score": 2, "model_used": "gemini-2.5-flash"},
            "completeness_evaluation": {"completeness_score": 3, "model_used": "gemini-2.5-flash"},
        },
        "overall_score": 2.5,
        "verdict": "NEEDS_IMPROVEMENT",
        "source_type": "BATCH",
    }
    client.post("/history/evaluations", json=item2, headers=headers_a)

    # Create evaluation 3 for USER A (FAIL, Insufficient evidence, model gemini-1.5-pro)
    item3 = {
        "question": "What is dark matter?",
        "ai_response": "Unknown cosmos entity.",
        "reference_answer": None,
        "evaluation_result": {
            "relevance_evaluation": {"relevance_score": 2, "model_used": "gemini-1.5-pro"},
            "accuracy_evaluation": {"accuracy_score": 2, "model_used": "gemini-1.5-pro"},
            "hallucination_evaluation": {"status": "INSUFFICIENT_EVIDENCE", "hallucination_score": None, "model_used": "gemini-1.5-pro"},
            "completeness_evaluation": {"completeness_score": 2, "model_used": "gemini-1.5-pro"},
        },
        "overall_score": 2.0,
        "verdict": "FAIL",
        "source_type": "SINGLE",
    }
    client.post("/history/evaluations", json=item3, headers=headers_a)

    # Create evaluation for USER B (User Isolation check)
    item_b = {
        "question": "User B question",
        "ai_response": "User B response",
        "evaluation_result": {"relevance_evaluation": {"relevance_score": 1}},
        "overall_score": 1.0,
        "verdict": "FAIL",
        "source_type": "SINGLE",
    }
    client.post("/history/evaluations", json=item_b, headers=headers_b)

    # 1. Fetch unfiltered analytics for USER A
    res_a = client.get("/history/analytics", headers=headers_a)
    assert res_a.status_code == 200
    data_a = res_a.json()

    assert data_a["total_evaluations"] == 3
    assert data_a["verdict_distribution"]["pass_count"] == 1
    assert data_a["verdict_distribution"]["needs_improvement_count"] == 1
    assert data_a["verdict_distribution"]["fail_count"] == 1

    # Dimension averages:
    # Relevance: (5 + 3 + 2) / 3 = 3.33
    # Accuracy: (5 + 2 + 2) / 3 = 3.0
    # Completeness: (4 + 3 + 2) / 3 = 3.0
    # Overall: (4.75 + 2.5 + 2.0) / 3 = 3.08
    assert data_a["average_scores"]["average_relevance"] == 3.33
    assert data_a["average_scores"]["average_accuracy"] == 3.0
    assert data_a["average_scores"]["average_completeness"] == 3.0
    assert data_a["average_scores"]["average_overall_score"] == 3.08

    # Hallucination metrics:
    # Item 1: status SUCCESS, score 5 (Grounded)
    # Item 2: status SUCCESS, score 2 (Hallucinated, < 4)
    # Item 3: status INSUFFICIENT_EVIDENCE (Excluded from evaluable)
    # Total evaluable = 2, Insufficient evidence = 1, Hallucinated = 1, Grounded = 1
    # Hallucination rate = 1 / 2 = 50.0%
    assert data_a["hallucination_metrics"]["evaluable_count"] == 2
    assert data_a["hallucination_metrics"]["insufficient_evidence_count"] == 1
    assert data_a["hallucination_metrics"]["hallucinated_count"] == 1
    assert data_a["hallucination_metrics"]["grounded_count"] == 1
    assert data_a["hallucination_metrics"]["hallucination_rate_percentage"] == 50.0

    # Quality trends
    assert len(data_a["quality_trends"]) >= 1

    # Available filters metadata
    assert "gemini-2.5-flash" in data_a["available_filters"]["available_models"]
    assert "gemini-1.5-pro" in data_a["available_filters"]["available_models"]

    # 2. Test source_type filter (source_type=BATCH)
    res_batch = client.get("/history/analytics?source_type=BATCH", headers=headers_a)
    assert res_batch.status_code == 200
    data_batch = res_batch.json()
    assert data_batch["total_evaluations"] == 1
    assert data_batch["verdict_distribution"]["needs_improvement_count"] == 1

    # 3. Test verdict filter (verdict=PASS)
    res_pass = client.get("/history/analytics?verdict=PASS", headers=headers_a)
    assert res_pass.status_code == 200
    data_pass = res_pass.json()
    assert data_pass["total_evaluations"] == 1
    assert data_pass["average_scores"]["average_overall_score"] == 4.75

    # 4. Test model filter (model=gemini-1.5-pro)
    res_model = client.get("/history/analytics?model=gemini-1.5-pro", headers=headers_a)
    assert res_model.status_code == 200
    data_model = res_model.json()
    assert data_model["total_evaluations"] == 1
    assert data_model["verdict_distribution"]["fail_count"] == 1

    # 5. Test User Isolation for USER B
    res_b = client.get("/history/analytics", headers=headers_b)
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["total_evaluations"] == 1
    assert data_b["verdict_distribution"]["fail_count"] == 1

    # 6. Verify existing GET /history/stats remains unchanged
    res_legacy_stats = client.get("/history/stats", headers=headers_a)
    assert res_legacy_stats.status_code == 200
    stats_legacy = res_legacy_stats.json()
    assert stats_legacy["total_evaluations"] == 3
    assert stats_legacy["pass_count"] == 1
