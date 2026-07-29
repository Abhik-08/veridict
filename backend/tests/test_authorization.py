import time
import pytest
import jwt
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.config import settings
from app.database.base import Base
from app.database.session import get_db
from app.database.models.profile import Profile
from app.database.models.evaluation import Evaluation
from app.database.models.batch_job import BatchJob
from app.database.models.batch_result import BatchResult

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)


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


client = TestClient(app)


def create_test_token(sub_uuid: str, email: str = "auth_test@veridict.ai"):
    payload = {
        "sub": sub_uuid,
        "email": email,
        "aud": "authenticated",
        "iss": "https://vypgvpyfgpugcerdljyk.supabase.co/auth/v1",
        "exp": int(time.time()) + 3600,
        "app_metadata": {"provider": "email"},
        "user_metadata": {"full_name": "Auth Test User"},
    }
    return jwt.encode(payload, settings.SUPABASE_SERVICE_ROLE_KEY, algorithm="HS256")


def test_unauthenticated_request_rejected():
    endpoints = [
        ("/me", "GET"),
        ("/auth/sync-profile", "POST"),
        ("/retrieve", "POST"),
    ]
    for url, method in endpoints:
        if method == "GET":
            response = client.get(url)
        else:
            response = client.post(url, json={"query": "test"})
        assert response.status_code == 401, f"Expected 401 for {method} {url}, got {response.status_code}"


def test_invalid_token_rejected():
    headers = {"Authorization": "Bearer invalid.jwt.token"}
    response = client.get("/me", headers=headers)
    assert response.status_code == 401


def test_authenticated_request_allowed():
    user_id = str(uuid4())
    token = create_test_token(user_id, email="authorized@veridict.ai")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/auth/sync-profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["email"] == "authorized@veridict.ai"

    me_response = client.get("/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["id"] == user_id


def test_user_identity_strictly_from_jwt():
    user_id = str(uuid4())
    token = create_test_token(user_id, email="jwt_identity@veridict.ai")
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt spoofing user_id in sync request body
    response = client.post(
        "/auth/sync-profile",
        headers=headers,
        json={"id": "spoofed-user-id", "email": "spoofed@hacker.com"},
    )
    assert response.status_code == 200
    # Returned profile MUST match JWT identity, ignoring body payload spoofing
    assert response.json()["id"] == user_id
    assert response.json()["email"] == "jwt_identity@veridict.ai"
