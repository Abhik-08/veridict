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

# Setup test in-memory SQLite database with StaticPool
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


def create_test_token(sub_uuid: str, email: str = "sync_user@veridict.ai", name: str = "Sync User"):
    payload = {
        "sub": sub_uuid,
        "email": email,
        "aud": "authenticated",
        "iss": "https://vypgvpyfgpugcerdljyk.supabase.co/auth/v1",
        "exp": int(time.time()) + 3600,
        "app_metadata": {"provider": "google"},
        "user_metadata": {"full_name": name, "avatar_url": "https://example.com/avatar.jpg"},
    }
    return jwt.encode(payload, settings.SUPABASE_SERVICE_ROLE_KEY, algorithm="HS256")


def test_sync_profile_endpoint():
    user_uuid = str(uuid4())
    token = create_test_token(user_uuid)

    response = client.post(
        "/auth/sync-profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_uuid
    assert data["email"] == "sync_user@veridict.ai"
    assert data["full_name"] == "Sync User"
    assert data["avatar_url"] == "https://example.com/avatar.jpg"
    assert data["provider"] == "google"


def test_get_me_endpoint():
    user_uuid = str(uuid4())
    token = create_test_token(user_uuid, email="me_user@veridict.ai", name="Me User")

    # First call syncs profile
    sync_resp = client.post(
        "/auth/sync-profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert sync_resp.status_code == 200

    # Call /me endpoint
    me_resp = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["id"] == user_uuid
    assert me_data["email"] == "me_user@veridict.ai"
    assert me_data["full_name"] == "Me User"


def test_sync_profile_idempotent():
    user_uuid = str(uuid4())
    token = create_test_token(user_uuid)

    # First sync
    resp1 = client.post("/auth/sync-profile", headers={"Authorization": f"Bearer {token}"})
    assert resp1.status_code == 200

    # Second sync (same user)
    resp2 = client.post("/auth/sync-profile", headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 200
    assert resp2.json()["id"] == resp1.json()["id"]
