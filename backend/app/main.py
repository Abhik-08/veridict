import logging
import asyncio
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.retrieval import router as retrieval_router
from app.api.evaluation import router as evaluation_router
from app.api.batch_evaluation import router as batch_evaluation_router
from app.api.auth import router as auth_router
from app.history.router import router as history_router
from app.services.pdf_ingestion_service import PDFIngestionService
from app.database.session import engine, get_db
from app.database.base import Base
import app.database.models  # Ensures all models are imported before create_all
from app.common.exceptions.base import BaseAppException
from app.common.models.responses import ErrorResponse
from app.core.config import settings

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
    description="Enterprise AI Response Quality & Hallucination Evaluator API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BaseAppException)
async def base_app_exception_handler(request: Request, exc: BaseAppException):
    """Global exception handler converting BaseAppException into structured ErrorResponse JSON."""
    error_payload = ErrorResponse(
        error=exc.error_code,
        message=exc.message,
        details=exc.details,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload.model_dump(),
    )


# --------------------------------------------------
# Namespace Expiration Scheduler (PDF Ingestion Purge)
# --------------------------------------------------
async def run_cleanup_scheduler() -> None:
    """Hourly background loop triggering purge of expired namespaces."""
    logger.info("Initializing PDF Namespace Expiration Scheduler (Purge TTL: %sh)", settings_ttl_hours())
    
    ingestion_service = PDFIngestionService()
    
    while True:
        try:
            deleted = ingestion_service.cleanup_expired_namespaces()
            if deleted:
                logger.info(f"Scheduler successfully deleted {len(deleted)} expired namespaces: {deleted}")
        except Exception:
            logger.exception("Error in scheduled cleanup loop")
        
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
    """FastAPI application startup hook to create tables and run background scheduler tasks."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully via SQLAlchemy Base.metadata.")
    except Exception as exc:
        logger.warning(f"Could not connect to database on startup (will verify on endpoint call): {exc}")

    task = asyncio.create_task(run_cleanup_scheduler())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)


@app.get("/", summary="Root Status", description="Returns API operational greeting.")
def root():
    """Root endpoint greeting."""
    return {
        "message": "🚀 Veridict Backend Running"
    }


@app.api_route("/health", methods=["GET", "HEAD"], summary="Health Check", description="Returns system health status.")
def health():
    """Health check endpoint."""
    return {
        "status": "healthy"
    }


@app.get("/db-health", summary="Database Health Check", description="Verifies PostgreSQL database connectivity.")
def db_health(db: Annotated[Session, Depends(get_db)]):
    """Database health check endpoint verifying PostgreSQL connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "database": "Supabase PostgreSQL"
        }
    except Exception as exc:
        logger.exception("Database health check failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(exc)}"
        )


# ==============================
# Register API Routers
# ==============================
app.include_router(auth_router)
app.include_router(retrieval_router)
app.include_router(evaluation_router)
app.include_router(batch_evaluation_router)
app.include_router(history_router)