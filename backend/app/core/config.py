from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==============================
    # Environment & Server Config
    # ==============================
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    JWT_DEBUG_LOGGING: bool = False
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    # ==============================
    # AI & LLM Settings
    # ==============================
    GOOGLE_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # ==============================
    # Pinecone Vector Store
    # ==============================
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "veridict-knowledge-base"
    PINECONE_NAMESPACE: str = "default"

    # ==============================
    # Database & Supabase
    # ==============================
    DATABASE_URL: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # ==============================
    # Knowledge Base & Chunking
    # ==============================
    SAMPLE_SIZE: int = 1000
    RANDOM_SEED: int = 42
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    TOP_K: int = 5
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
    # PDF Ingestion & Optimization
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
    # Batch Evaluation Configuration
    # ==============================
    MAX_BATCH_ROWS: int = 30
    BATCH_SIZE: int = 3
    MAX_BATCH_RETRIES: int = 2

    # ==============================
    # Pydantic Settings Configuration
    # ==============================
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()