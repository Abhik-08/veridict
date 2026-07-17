from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==============================
    # Environment
    # ==============================
    GOOGLE_API_KEY: str
    PINECONE_API_KEY: str

    # ==============================
    # Knowledge Base
    # ==============================
    SAMPLE_SIZE: int = 1000
    RANDOM_SEED: int = 42

    # ==============================
    # Chunking
    # ==============================
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100

    # ==============================
    # Retrieval
    # ==============================
    TOP_K: int = 5

    # ==============================
    # Models
    # ==============================
    EMBEDDING_MODEL: str = "gemini-embedding-001"

    # ==============================
    # Judge LLM Configuration
    # ==============================
    JUDGE_PRIMARY_MODEL: str = "gemini-2.5-flash"
    JUDGE_FALLBACK_MODELS: str = "gemini-3.1-flash-lite,gemini-3.5-flash"
    JUDGE_MAX_RETRIES: int = 2
    JUDGE_RETRY_BASE_DELAY: float = 1.0
    JUDGE_REQUEST_TIMEOUT: int = 60
    JUDGE_TEMPERATURE: float = 0.0

    # ==============================
    # Vector Database
    # ==============================
    PINECONE_INDEX_NAME: str = "veridict-knowledge-base"

    # ==============================
    # PDF Ingestion & Optimization Configuration
    # ==============================
    MAX_PDF_PAGES: int = 500
    MAX_PDF_SIZE_BYTES: int = 52428800  # 50 MB
    EMBEDDING_BATCH_SIZE: int = 20
    UPSERT_BATCH_SIZE: int = 100
    PDF_NAMESPACE_TTL_HOURS: int = 24
    MAX_BACKGROUND_TASKS: int = 5
    CACHE_ENABLED: bool = True
    PDF_CACHE_FILE: str = "app/knowledge/processed/pdf_cache.json"
    INGESTION_JOBS_FILE: str = "app/knowledge/processed/ingestion_jobs.json"

    # ==============================
    # Pydantic Settings Configuration
    # ==============================
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()