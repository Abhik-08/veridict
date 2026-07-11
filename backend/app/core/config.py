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
    # Vector Database
    # ==============================
    PINECONE_INDEX_NAME: str = "veridict-knowledge-base"

    # ==============================
    # Pydantic Settings Configuration
    # ==============================
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()