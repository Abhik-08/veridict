import logging
import asyncio
from fastapi import FastAPI

from app.api.retrieval import router as retrieval_router
from app.api.evaluation import router as evaluation_router
from app.services.pdf_ingestion_service import PDFIngestionService

# --------------------------------------------------
# Structured Logging Initialization (Phase I)
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Veridict API",
    version="1.0.0",
    description="AI Response Quality Evaluator Backend"
)


# --------------------------------------------------
# Temporary Namespace Expiration Scheduler (Phase F)
# --------------------------------------------------
async def run_cleanup_scheduler() -> None:
    """Hourly background loop triggering purge of expired namespaces."""
    logger.info("Initializing PDF Namespace Expiration Scheduler (Purge TTL: %sh)", settings_ttl_hours())
    
    # Instantiate inside task to ensure loop compatibility
    ingestion_service = PDFIngestionService()
    
    while True:
        try:
            deleted = ingestion_service.cleanup_expired_namespaces()
            if deleted:
                logger.info(f"Scheduler successfully deleted {len(deleted)} expired namespaces: {deleted}")
        except Exception:
            logger.exception("Error in scheduled cleanup loop")
        
        # Sleep for 1 hour (3600 seconds)
        await asyncio.sleep(3600)


def settings_ttl_hours() -> int:
    try:
        from app.core.config import settings
        return settings.PDF_NAMESPACE_TTL_HOURS
    except Exception:
        return 24


# To prevent premature garbage collection of background tasks
background_tasks = set()


@app.on_event("startup")
async def startup_event() -> None:
    """FastAPI application startup hook to run background scheduler tasks."""
    task = asyncio.create_task(run_cleanup_scheduler())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)


@app.get("/")
def root():
    """
    Root endpoint.
    """
    return {
        "message": "🚀 Veridict Backend Running"
    }


@app.get("/health")
def health():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy"
    }


# ==============================
# Register API Routers
# ==============================
app.include_router(retrieval_router)
app.include_router(evaluation_router)