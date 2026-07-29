"""
Veridict Batch Evaluation API Router.

Exposes endpoints for CSV upload, Digital QA PDF upload, progress tracking,
and CSV/PDF export downloads.
"""

from typing import Annotated
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)

from app.auth.dependencies import get_current_user
from app.auth.schemas import AuthenticatedUser
from app.schemas.batch_evaluation import BatchProgress
from app.services.batch_evaluation_service import BatchEvaluationService
from app.services.batch_parsers import CSVBatchParser, PDFBatchParser
from app.services.batch_report_generator import BatchReportGenerator
from app.services.pdf_ingestion_service import PDFIngestionService

router = APIRouter(prefix="/evaluate/batch", tags=["Batch Evaluation"])
batch_service = BatchEvaluationService()
ingestion_service = PDFIngestionService()


@router.post(
    "/csv",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start CSV Batch Evaluation Task",
)
async def evaluate_batch_csv(
    file: Annotated[UploadFile, File(description="CSV Upload file containing Question and AI Response columns")],
    evidence_pdf: Annotated[UploadFile | None, File(description="Optional evidence context PDF")] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user: Annotated[AuthenticatedUser, Depends(get_current_user)] = None,
) -> BatchProgress:
    """Parse CSV upload, resolve optional evidence PDF, and launch background batch evaluation."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a valid CSV file (.csv).",
        )

    content = await file.read()
    try:
        items = CSVBatchParser.parse(content)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )

    # Process optional evidence PDF
    pdf_namespace = None
    if evidence_pdf and evidence_pdf.filename:
        pdf_content = await evidence_pdf.read()
        try:
            pdf_namespace, _ = await ingestion_service.ingest_pdf(
                file_content=pdf_content,
                filename=evidence_pdf.filename,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Evidence PDF processing failed: {str(exc)}",
            )

    job = batch_service.create_job(
        filename=file.filename,
        file_type="CSV",
        items=items,
    )

    background_tasks.add_task(
        batch_service.process_batch_job,
        batch_id=job.batch_id,
        items=items,
        pdf_namespace=pdf_namespace,
    )

    return job


@router.post(
    "/pdf",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start Digital QA PDF Batch Evaluation Task",
)
async def evaluate_batch_pdf(
    file: Annotated[UploadFile, File(description="Digital searchable QA PDF file")],
    evidence_pdf: Annotated[UploadFile | None, File(description="Optional evidence context PDF")] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user: Annotated[AuthenticatedUser, Depends(get_current_user)] = None,
) -> BatchProgress:
    """Parse Digital QA PDF upload, resolve optional evidence PDF, and launch background batch evaluation."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a valid PDF file (.pdf).",
        )

    content = await file.read()
    try:
        items = PDFBatchParser.parse(content)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )

    pdf_namespace = None
    if evidence_pdf and evidence_pdf.filename:
        evidence_content = await evidence_pdf.read()
        try:
            pdf_namespace, _ = await ingestion_service.ingest_pdf(
                file_content=evidence_content,
                filename=evidence_pdf.filename,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Evidence PDF processing failed: {str(exc)}",
            )

    job = batch_service.create_job(
        filename=file.filename,
        file_type="PDF",
        items=items,
    )

    background_tasks.add_task(
        batch_service.process_batch_job,
        batch_id=job.batch_id,
        items=items,
        pdf_namespace=pdf_namespace,
    )

    return job


@router.get(
    "/progress/{batch_id}",
    summary="Get Batch Evaluation Progress",
)
async def get_batch_progress(
    batch_id: str,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)] = None,
) -> BatchProgress:
    """Fetch current progress status of an active or completed batch evaluation job."""
    progress = batch_service.get_progress(batch_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch job '{batch_id}' not found.",
        )
    return progress


@router.get(
    "/export-csv/{batch_id}",
    summary="Export Evaluated CSV Report",
)
async def export_batch_csv(
    batch_id: str,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)] = None,
) -> Response:
    """Download evaluated dataset results as a CSV file."""
    progress = batch_service.get_progress(batch_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch job '{batch_id}' not found.",
        )

    csv_bytes = BatchReportGenerator.generate_batch_csv(progress.items)
    safe_filename = f"veridict_batch_eval_{batch_id}.csv"

    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"',
            "Content-Type": "text/csv; charset=utf-8",
        },
    )


@router.get(
    "/export-pdf/{batch_id}",
    summary="Export Executive Batch Evaluation PDF Report",
)
async def export_batch_pdf(
    batch_id: str,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)] = None,
) -> Response:
    """Download executive batch evaluation report as a PDF document."""
    progress = batch_service.get_progress(batch_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch job '{batch_id}' not found.",
        )

    pdf_bytes = BatchReportGenerator.generate_batch_pdf(progress)
    safe_filename = f"veridict_batch_report_{batch_id}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"',
            "Content-Type": "application/pdf",
        },
    )
