from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.database.models.batch_job import BatchJob
from app.database.models.batch_result import BatchResult


class BatchRepository:
    """
    Repository layer for Batch Evaluation Job & Results operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_job_by_id(self, batch_job_id: UUID) -> Optional[BatchJob]:
        return self.db.query(BatchJob).filter(BatchJob.id == batch_job_id).first()

    def get_user_jobs(self, user_id: UUID, limit: int = 50) -> List[BatchJob]:
        return (
            self.db.query(BatchJob)
            .filter(BatchJob.user_id == user_id)
            .order_by(BatchJob.created_at.desc())
            .limit(limit)
            .all()
        )

    def create_job(self, filename: str, total_rows: int, user_id: Optional[UUID] = None) -> BatchJob:
        job = BatchJob(
            user_id=user_id,
            filename=filename,
            total_rows=total_rows,
            status="PENDING",
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_job_progress(
        self, batch_job_id: UUID, processed_rows: int, status: str, progress: float
    ) -> Optional[BatchJob]:
        job = self.get_job_by_id(batch_job_id)
        if not job:
            return None
        job.processed_rows = processed_rows
        job.status = status
        job.progress = progress
        self.db.commit()
        self.db.refresh(job)
        return job

    def add_result(self, batch_job_id: UUID, question: str, ai_response: str, overall_score: Optional[float] = None, verdict: Optional[str] = None, reasoning: Optional[str] = None) -> BatchResult:
        result = BatchResult(
            batch_job_id=batch_job_id,
            question=question,
            ai_response=ai_response,
            overall_score=overall_score,
            verdict=verdict,
            reasoning=reasoning,
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result
