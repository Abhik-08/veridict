import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials

from app.auth.dependencies import get_current_user, security_scheme
from app.auth.schemas import AuthenticatedUser, ProfileResponse
from app.auth.service import AuthService
from app.database.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Authentication"])


@router.post("/auth/sync-profile", response_model=ProfileResponse)
def sync_profile(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Synchronizes authenticated user with PostgreSQL profiles table.
    Auto-creates profile if missing or returns existing.
    """
    try:
        claims = AuthService.extract_claims(credentials.credentials)
        profile = AuthService.sync_profile(user, claims, db)
        return ProfileResponse(
            id=str(profile.id),
            email=profile.email,
            full_name=profile.full_name,
            avatar_url=profile.avatar_url,
            provider=profile.provider,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Profile synchronization failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile synchronization failed: {str(exc)}",
        ) from exc


@router.get("/me", response_model=ProfileResponse)
def get_me(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Returns authenticated user profile.
    Auto-syncs profile if not found in database.
    """
    try:
        profile = AuthService.get_profile(user.id, db)
        if not profile:
            claims = AuthService.extract_claims(credentials.credentials)
            profile = AuthService.sync_profile(user, claims, db)

        return ProfileResponse(
            id=str(profile.id),
            email=profile.email,
            full_name=profile.full_name,
            avatar_url=profile.avatar_url,
            provider=profile.provider,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Could not retrieve user profile: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve user profile: {str(exc)}",
        ) from exc
