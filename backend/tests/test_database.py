import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.base import Base
from app.database.session import get_db
from app.database.models.profile import Profile
from app.database.models.evaluation import Evaluation
from app.database.models.batch_job import BatchJob
from app.database.models.batch_result import BatchResult
from app.database.repositories.profile_repository import ProfileRepository
from app.database.repositories.evaluation_repository import EvaluationRepository
from app.database.repositories.batch_repository import BatchRepository

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


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


def test_db_health_endpoint():
    client = TestClient(app)
    response = client.get("/db-health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    assert data["database"] == "Supabase PostgreSQL"


def test_profile_repository():
    db = TestingSessionLocal()
    repo = ProfileRepository(db)

    # Test profile creation
    profile = repo.create(email="test@veridict.ai", full_name="Test User")
    assert profile.id is not None
    assert profile.email == "test@veridict.ai"
    assert profile.full_name == "Test User"
    assert profile.provider == "email"

    # Test lookup by email
    found = repo.get_by_email("test@veridict.ai")
    assert found is not None
    assert found.id == profile.id

    # Test lookup by ID
    found_id = repo.get_by_id(profile.id)
    assert found_id is not None
    assert found_id.email == "test@veridict.ai"
    db.close()


def test_evaluation_repository():
    db = TestingSessionLocal()
    profile_repo = ProfileRepository(db)
    eval_repo = EvaluationRepository(db)

    user = profile_repo.create(email="eval_user@veridict.ai")

    eval_item = eval_repo.create(
        user_id=user.id,
        question="What is RAG?",
        ai_response="Retrieval-Augmented Generation.",
        overall_score=4.5,
        verdict="PASS",
        reasoning="Accurate and grounded.",
    )
    assert eval_item.id is not None
    assert eval_item.user_id == user.id
    assert eval_item.overall_score == 4.5
    assert eval_item.verdict == "PASS"

    user_evals = eval_repo.get_by_user_id(user.id)
    assert len(user_evals) == 1
    assert user_evals[0].id == eval_item.id
    db.close()


def test_batch_repository():
    db = TestingSessionLocal()
    batch_repo = BatchRepository(db)

    job = batch_repo.create_job(filename="dataset.csv", total_rows=10)
    assert job.id is not None
    assert job.filename == "dataset.csv"
    assert job.status == "PENDING"
    assert job.total_rows == 10

    # Update progress
    updated = batch_repo.update_job_progress(job.id, processed_rows=5, status="PROCESSING", progress=50.0)
    assert updated.processed_rows == 5
    assert updated.status == "PROCESSING"

    # Add result item
    res = batch_repo.add_result(
        batch_job_id=job.id,
        question="Q1",
        ai_response="A1",
        overall_score=5.0,
        verdict="PASS",
        reasoning="Perfect response",
    )
    assert res.id is not None
    assert res.batch_job_id == job.id
    assert res.overall_score == 5.0
    db.close()
