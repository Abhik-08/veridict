import uuid
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.database.models.profile import Profile


class ProfileRepository:
    """
    Repository layer for Profile database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, profile_id: UUID | str) -> Optional[Profile]:
        target_uuid = UUID(str(profile_id)) if not isinstance(profile_id, UUID) else profile_id
        return self.db.query(Profile).filter(Profile.id == target_uuid).first()

    def get_by_email(self, email: str) -> Optional[Profile]:
        return self.db.query(Profile).filter(Profile.email == email).first()

    def create(
        self,
        email: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        provider: str = "email",
        profile_id: Optional[UUID | str] = None,
    ) -> Profile:
        if profile_id:
            target_uuid = UUID(str(profile_id)) if not isinstance(profile_id, UUID) else profile_id
        else:
            target_uuid = uuid.uuid4()

        profile = Profile(
            id=target_uuid,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
            provider=provider,
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def create_or_get_profile(
        self,
        profile_id: UUID | str,
        email: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        provider: str = "email",
    ) -> Profile:
        target_uuid = UUID(str(profile_id)) if not isinstance(profile_id, UUID) else profile_id
        existing = self.get_by_id(target_uuid)
        if existing:
            # Update fields if metadata provided
            updated = False
            if full_name and existing.full_name != full_name:
                existing.full_name = full_name
                updated = True
            if avatar_url and existing.avatar_url != avatar_url:
                existing.avatar_url = avatar_url
                updated = True
            if updated:
                self.db.commit()
                self.db.refresh(existing)
            return existing

        # Check by email as fallback
        existing_email = self.get_by_email(email)
        if existing_email:
            return existing_email

        return self.create(
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
            provider=provider,
            profile_id=target_uuid,
        )
