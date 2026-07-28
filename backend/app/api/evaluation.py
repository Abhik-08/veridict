from datetime import datetime
from typing import Annotated, Any
from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
    BackgroundTasks,
    Response,
    Body
)

from app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationResponse
)
from app.services.evaluation_service import EvaluationService
from app.services.pdf_ingestion_service import PDFIngestionService
from app.services.pdf_report_generator import PDFReportGenerator

router = APIRouter(
    prefix="/evaluate",
    tags=["AI Response Evaluation"]
)

evaluation_service = EvaluationService()
pdf_ingestion_service = PDFIngestionService()
pdf_report_generator = PDFReportGenerator()


@router.post(
    "",
    response_model=EvaluationResponse,
    responses={
        500: {"description": "Internal Server Error during evaluation"}
    }
)
async def evaluate_response(
    background_tasks: BackgroundTasks,
    question: Annotated[str, Form(...)],
    ai_response: Annotated[str, Form(...)],
    reference_answer: Annotated[str | None, Form()] = None,
    pdf_file: Annotated[UploadFile | None, File()] = None
):
    """
    Prepare the evaluation payload.

    Accepts:
    - User question
    - AI response
    - Optional reference answer
    - Optional PDF document

    The uploaded PDF (if provided) will be ingested asynchronously in the background.
    """
    try:
        request = EvaluationRequest(
            question=question,
            ai_response=ai_response,
            reference_answer=reference_answer
        )

        return await evaluation_service.evaluate(
            request=request,
            pdf_file=pdf_file,
            background_tasks=background_tasks
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post(
    "/export-pdf",
    responses={
        500: {"description": "Internal Server Error during PDF generation"}
    }
)
async def export_evaluation_pdf(payload: Annotated[dict[str, Any], Body()]):
    """
    Generate and stream an enterprise multi-page PDF evaluation report.
    """
    try:
        pdf_bytes = pdf_report_generator.generate_report(payload)
        now_str = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"Veridict-Evaluation-Report-{now_str}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF evaluation report: {str(e)}"
        )


@router.get(
    "/status/{namespace}",
    response_model=dict,
    responses={
        404: {"description": "Ingestion task namespace not found"}
    }
)
def get_ingestion_status(namespace: str):
    """
    Get the processing status and performance metrics for a PDF ingestion task.
    """
    status_data = pdf_ingestion_service.get_job_status(namespace)
    if not status_data:
        raise HTTPException(
            status_code=404,
            detail=f"Ingestion task with namespace '{namespace}' not found."
        )
    return status_data