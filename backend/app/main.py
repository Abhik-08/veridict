from fastapi import FastAPI

app = FastAPI(
    title="Veridict API",
    version="1.0.0",
    description="AI Response Quality Evaluator Backend"
)


@app.get("/")
def root():
    return {
        "message": "🚀 Veridict Backend Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }