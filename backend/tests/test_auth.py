import time
import pytest
import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.auth.jwt import verify_jwt
from app.auth.service import AuthService
from app.auth.dependencies import get_current_user
from app.auth.schemas import AuthenticatedUser

mock_app = FastAPI()


@mock_app.get("/protected-route")
def protected_route(user: AuthenticatedUser = Depends(get_current_user)):
    return {"status": "authenticated", "user_id": user.id, "email": user.email}


client = TestClient(mock_app)


def create_mock_jwt(sub: str = "user-123-uuid", email: str = "user@veridict.ai", exp_offset: int = 3600):
    payload = {
        "sub": sub,
        "email": email,
        "aud": "authenticated",
        "iss": "https://vypgvpyfgpugcerdljyk.supabase.co/auth/v1",
        "exp": int(time.time()) + exp_offset,
        "app_metadata": {"provider": "email"},
    }
    return jwt.encode(payload, settings.SUPABASE_SERVICE_ROLE_KEY, algorithm="HS256")


def test_verify_jwt_success():
    token = create_mock_jwt()
    claims = verify_jwt(token)
    assert claims.sub == "user-123-uuid"
    assert claims.email == "user@veridict.ai"
    assert claims.provider == "email"


def test_verify_jwt_expired():
    token = create_mock_jwt(exp_offset=-100)
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt(token)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


def test_verify_jwt_empty():
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt("")
    assert exc_info.value.status_code == 401


def test_auth_service_authenticate_user():
    token = create_mock_jwt(sub="user-456", email="test456@veridict.ai")
    user = AuthService.authenticate_user(token)
    assert isinstance(user, AuthenticatedUser)
    assert user.id == "user-456"
    assert user.email == "test456@veridict.ai"


def test_protected_route_success():
    token = create_mock_jwt(sub="user-789", email="protected@veridict.ai")
    response = client.get("/protected-route", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "authenticated"
    assert data["user_id"] == "user-789"


def test_protected_route_missing_header():
    response = client.get("/protected-route")
    assert response.status_code == 403 or response.status_code == 401


def test_protected_route_invalid_token():
    response = client.get("/protected-route", headers={"Authorization": "Bearer invalid.token.str"})
    assert response.status_code == 401
