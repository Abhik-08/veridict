import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.auth.jwt import verify_jwt
from app.auth.schemas import JWTClaims, AuthenticatedUser
from app.database.models.profile import Profile
from app.database.repositories.profile_repository import ProfileRepository

logger = logging.getLogger(__name__)


class AuthService:
    """
    Reusable Authentication Service layer for token validation,
    claims extraction, user instance resolution, and profile synchronization.
    """

    @staticmethod
    def verify_jwt(token: str, method: Optional[str] = None, path: Optional[str] = None) -> JWTClaims:
        """Verifies JWT token and returns parsed JWTClaims."""
        return verify_jwt(token, method=method, path=path)

    @staticmethod
    def extract_claims(token: str, method: Optional[str] = None, path: Optional[str] = None) -> JWTClaims:
        """Extracts claims from a verified JWT token."""
        return verify_jwt(token, method=method, path=path)

    @staticmethod
    def authenticate_user(
        token: str,
        method: Optional[str] = None,
        path: Optional[str] = None
    ) -> AuthenticatedUser:
        """
        Authenticates incoming token and converts claims into an AuthenticatedUser instance.
        """
        claims = verify_jwt(token, method=method, path=path)
        return AuthenticatedUser(
            id=claims.sub,
            email=claims.email,
            provider=claims.provider or "email",
        )

    @staticmethod
    def sync_profile(user: AuthenticatedUser, claims: JWTClaims, db: Session) -> Profile:
        """
        Synchronizes an authenticated user with PostgreSQL profiles table.
        Auto-creates profile if missing or reuses existing.
        """
        repo = ProfileRepository(db)
        user_uuid = UUID(user.id)

        # Extract metadata from claims if present
        user_meta = claims.user_metadata or {}
        full_name = user_meta.get("full_name") or user_meta.get("name")
        avatar_url = user_meta.get("avatar_url") or user_meta.get("picture")

        profile = repo.create_or_get_profile(
            profile_id=user_uuid,
            email=user.email or f"{user.id}@veridict.user",
            full_name=full_name,
            avatar_url=avatar_url,
            provider=user.provider,
        )

        logger.info("Profile synchronized successfully for user ID")
        return profile

    @staticmethod
    def get_profile(user_id: str, db: Session) -> Optional[Profile]:
        """Retrieves user profile from database by user ID UUID string."""
        repo = ProfileRepository(db)
        try:
            user_uuid = UUID(user_id)
            return repo.get_by_id(user_uuid)
        except ValueError:
            return None
