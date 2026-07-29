from typing import Annotated
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.service import AuthService
from app.auth.schemas import AuthenticatedUser

security_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    request: Request,
) -> AuthenticatedUser:
    """
    FastAPI dependency that extracts Bearer token from request headers
    and returns the authenticated user instance.

    Usage in endpoints:
        user: Annotated[AuthenticatedUser, Depends(get_current_user)]
    """
    return AuthService.authenticate_user(
        credentials.credentials,
        method=request.method,
        path=request.url.path
    )
