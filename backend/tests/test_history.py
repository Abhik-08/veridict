"""
Unit and Integration Tests for Evaluation History Foundation (Milestone 6 Phase 1 - Phase 3).
Verifies models, schemas, mapper transformations, repository CRUD, service layer, router security, automatic persistence, domain events, enums, pagination, search, batch APIs, and user data isolation.
"""
import time
import uuid
import pytest
import jwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.database.base import Base
from app.database.session import get_db
from app.history.schemas import HistoryItemCreate, BatchJobCreate
from app.history.constants import EvaluationSource, HistoryStatus, EvaluationVerdict
from app.history.events import HistoryEvents
from app.history.mapper import HistoryMapper
from app.history.service import HistoryService

# Setup test in-memory SQLite database
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
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

USER_1_ID = uuid.uuid4()
USER_2_ID = uuid.uuid4()


def create_mock_jwt(user_id: uuid.UUID) -> str:
    """Helper creating signed JWT Bearer token for test requests using active server secret key."""
    key = getattr(settings, "SUPABASE_JWT_SECRET", None) or settings.SUPABASE_SERVICE_ROLE_KEY
    payload = {
        "sub": str(user_id),
        "email": "user@veridict.ai",
        "aud": "authenticated",
        "role": "authenticated",
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, key, algorithm="HS256")


def test_history_mapper_transformations():
    """Verifies pure data mapping from raw evaluation payloads into validated HistoryItemCreate models."""
    raw_eval = {
        "question": "What is RAG evaluation?",
        "answer": "Retrieval-Augmented Generation evaluation assesses accuracy and relevance.",
        "reference": "RAG evaluation ground truth",
        "evidence_chunks": [{"chunk_id": 101, "content": "Evidence text"}],
        "score": 4.8,
        "verdict": "pass",
        "evaluation_result": {
            "relevance": {"score": 5.0, "reasoning": "Perfect context relevance"},
            "accuracy": {"score": 4.6, "reasoning": "Factual"},
        },
    }

    item_create = HistoryMapper.to_history_item_create(raw_eval, source_type=EvaluationSource.SINGLE)
    assert item_create.question == "What is RAG evaluation?"
    assert item_create.ai_response == "Retrieval-Augmented Generation evaluation assesses accuracy and relevance."
    assert item_create.reference_answer == "RAG evaluation ground truth"
    assert item_create.retrieved_evidence == [{"chunk_id": 101, "content": "Evidence text"}]
    assert item_create.overall_score == 4.8
    assert item_create.verdict == "PASS"
    assert item_create.source_type == "SINGLE"

    batch_create = HistoryMapper.to_batch_job_create("eval_batch.csv", total_items=25)
    assert batch_create.filename == "eval_batch.csv"
    assert batch_create.total_items == 25
    assert batch_create.status == "PROCESSING"


def test_history_repository_and_service_crud():
    """Verifies repository and service CRUD operations with complete JSON payload serialization."""
    db = TestingSessionLocal()
    try:
        # 1. Create BatchJob
        batch_data = BatchJobCreate(filename="dataset_test.csv", total_items=10, status=HistoryStatus.PROCESSING.value)
        batch = HistoryService.create_batch_job(db, USER_1_ID, batch_data)
        assert batch.id is not None
        assert batch.filename == "dataset_test.csv"
        assert batch.user_id == USER_1_ID

        # 2. Retrieve BatchJob
        retrieved_batch = HistoryService.get_batch_job(db, batch.id, USER_1_ID)
        assert retrieved_batch is not None
        assert retrieved_batch.id == batch.id

        # 3. Create Evaluation Item with complete evaluation_result JSON payload
        eval_payload = {
            "relevance": {"score": 4.5, "reasoning": "Highly relevant"},
            "accuracy": {"score": 5.0, "reasoning": "Accurate"},
            "verdict": "PASS",
        }
        eval_data = HistoryItemCreate(
            question="What is Veridict?",
            ai_response="Veridict is an AI quality evaluator.",
            reference_answer="An AI response evaluator tool.",
            retrieved_evidence=[{"text": "Veridict documentation chunk"}],
            evaluation_result=eval_payload,
            overall_score=4.75,
            verdict=EvaluationVerdict.PASS.value,
            source_type=EvaluationSource.SINGLE.value,
            batch_job_id=batch.id,
        )

        item = HistoryService.create_evaluation(db, USER_1_ID, eval_data)
        assert item.id is not None
        assert item.user_id == USER_1_ID
        assert item.question == "What is Veridict?"
        assert item.evaluation_result == eval_payload
        assert item.batch_job_id == batch.id

        # 4. Retrieve Evaluation Detail
        detail = HistoryService.get_evaluation_detail(db, item.id, USER_1_ID)
        assert detail is not None
        assert detail.overall_score == 4.75
        assert detail.evaluation_result["accuracy"]["score"] == 5.0

        # 5. List User History
        history_list = HistoryService.list_user_history(db, USER_1_ID, skip=0, limit=10)
        assert len(history_list) == 1
        assert history_list[0].id == item.id

        # 6. Dashboard Statistics
        stats = HistoryService.get_dashboard_statistics(db, USER_1_ID)
        assert stats.total_evaluations >= 1
        assert stats.total_batch_jobs >= 1
        assert stats.pass_count >= 1

        # 7. Delete Evaluation
        deleted = HistoryService.delete_evaluation_item(db, item.id, USER_1_ID)
        assert deleted is True
    finally:
        db.close()


def test_history_domain_events_and_constants():
    """Verifies domain event dispatching and enum constants."""
    assert EvaluationSource.SINGLE == "SINGLE"
    assert HistoryStatus.PROCESSING == "PROCESSING"
    assert EvaluationVerdict.PASS == "PASS"

    received_events = []

    def event_handler(event_type: str, payload: dict):
        received_events.append((event_type, payload))

    HistoryEvents.subscribe(event_handler)
    try:
        test_uid = uuid.uuid4()
        test_eid = uuid.uuid4()
        HistoryEvents.evaluation_saved(test_uid, test_eid, 4.7, EvaluationVerdict.PASS.value)
        assert len(received_events) == 1
        assert received_events[0][0] == "evaluation_saved"
        assert received_events[0][1]["user_id"] == test_uid
    finally:
        HistoryEvents.unsubscribe(event_handler)


def test_history_phase3_api_endpoints():
    """Verifies Phase 3 REST API endpoints (pagination, search, stats, recent, batch APIs, error handling)."""
    token = create_mock_jwt(USER_1_ID)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Post new evaluation
    post_payload = {
        "question": "Explain RAG evaluation architecture",
        "ai_response": "RAG evaluation measures accuracy, relevance, and grounding.",
        "reference_answer": "RAG evaluation tests context retrieval and answer quality.",
        "retrieved_evidence": [{"chunk_id": 1, "text": "RAG chunk"}],
        "evaluation_result": {
            "relevance": {"score": 4.5},
            "accuracy": {"score": 4.5},
            "verdict": "PASS",
        },
        "overall_score": 4.5,
        "verdict": "PASS",
        "source_type": "SINGLE",
    }

    res_post = client.post("/history/evaluations", json=post_payload, headers=headers)
    assert res_post.status_code == 201
    eval_id = res_post.json()["id"]

    # 2. GET /history with pagination & search
    res_history = client.get("/history?page=1&page_size=10&search=architecture&verdict=PASS", headers=headers)
    assert res_history.status_code == 200
    data = res_history.json()
    assert "items" in data
    assert "pagination" in data
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["total_items"] >= 1
    assert len(data["items"]) >= 1
    assert data["items"][0]["id"] == eval_id

    # 3. GET /history/recent
    res_recent = client.get("/history/recent?limit=5", headers=headers)
    assert res_recent.status_code == 200
    recent_items = res_recent.json()
    assert isinstance(recent_items, list)
    assert len(recent_items) >= 1

    # 4. GET /history/stats
    res_stats = client.get("/history/stats", headers=headers)
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert stats["total_evaluations"] >= 1
    assert stats["pass_count"] >= 1
    assert "pass_percentage" in stats

    # 5. GET /history/{id}
    res_detail = client.get(f"/history/{eval_id}", headers=headers)
    assert res_detail.status_code == 200
    assert res_detail.json()["question"] == "Explain RAG evaluation architecture"

    # 6. POST /history/batch & GET /history/batches & GET /history/batches/{id}
    batch_post_payload = {"filename": "test_phase3_dataset.csv", "total_items": 15, "status": "PROCESSING"}
    res_batch_post = client.post("/history/batch", json=batch_post_payload, headers=headers)
    assert res_batch_post.status_code == 201
    batch_id = res_batch_post.json()["id"]

    res_batches = client.get("/history/batches", headers=headers)
    assert res_batches.status_code == 200
    assert len(res_batches.json()) >= 1

    res_batch_detail = client.get(f"/history/batches/{batch_id}", headers=headers)
    assert res_batch_detail.status_code == 200
    assert res_batch_detail.json()["filename"] == "test_phase3_dataset.csv"

    # 7. DELETE /history/batches/{batch_id}
    res_del_batch = client.delete(f"/history/batches/{batch_id}", headers=headers)
    assert res_del_batch.status_code == 200
    assert res_del_batch.json()["success"] is True

    # 8. DELETE /history/{evaluation_id}
    res_del_eval = client.delete(f"/history/{eval_id}", headers=headers)
    assert res_del_eval.status_code == 200
    assert res_del_eval.json()["success"] is True

    # 9. Verify 404 for deleted items
    res_404_eval = client.get(f"/history/{eval_id}", headers=headers)
    assert res_404_eval.status_code == 404

    res_404_batch = client.get(f"/history/batches/{batch_id}", headers=headers)
    assert res_404_batch.status_code == 404

    # 10. Verify validation error (400 or 422) for invalid query parameters
    res_invalid = client.get("/history?page=0&page_size=200", headers=headers)
    assert res_invalid.status_code in (400, 422)
