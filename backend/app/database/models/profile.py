from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.database.base import BaseModel


class Profile(BaseModel):
    """
    Profile Model: Represents an authenticated user profile in Supabase PostgreSQL.
    """

    __tablename__ = "profiles"

    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    provider = Column(String(50), nullable=False, default="email")

    # Relationships
    evaluations = relationship("Evaluation", back_populates="user", cascade="all, delete-orphan")
    batch_jobs = relationship("BatchJob", back_populates="user", cascade="all, delete-orphan")
