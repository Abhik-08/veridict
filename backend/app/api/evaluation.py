from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
    BackgroundTasks
)

from app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationResponse
)
from app.services.evaluation_service import EvaluationService
from app.services.pdf_ingestion_service import PDFIngestionService

router = APIRouter(
    prefix="/evaluate",
    tags=["AI Response Evaluation"]
)

evaluation_service = EvaluationService()
pdf_ingestion_service = PDFIngestionService()


@router.post(
    "",
    response_model=EvaluationResponse
)
async def evaluate_response(
    background_tasks: BackgroundTasks,
    question: str = Form(...),
    ai_response: str = Form(...),
    reference_answer: str | None = Form(None),
    pdf_file: UploadFile | None = File(None)
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


@router.get(
    "/status/{namespace}",
    response_model=dict
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