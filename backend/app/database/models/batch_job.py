from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import BaseModel


class BatchJob(BaseModel):
    """
    BatchJob Model: Tracks asynchronous dataset batch evaluation tasks.
    """

    __tablename__ = "batch_jobs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)

    filename = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="PENDING", index=True)
    progress = Column(Float, nullable=False, default=0.0)
    total_rows = Column(Integer, nullable=False, default=0)
    processed_rows = Column(Integer, nullable=False, default=0)

    # Relationships
    user = relationship("Profile", back_populates="batch_jobs")
    results = relationship("BatchResult", back_populates="batch_job", cascade="all, delete-orphan")
