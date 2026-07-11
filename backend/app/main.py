from fastapi import FastAPI

from app.api.retrieval import router as retrieval_router
from app.api.evaluation import router as evaluation_router

app = FastAPI(
    title="Veridict API",
    version="1.0.0",
    description="AI Response Quality Evaluator Backend"
)


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