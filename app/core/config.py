"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Runtime configuration for the personal RAG backend."""

    # API
    API_V1_PREFIX: str = "/api/v1"
    ENV: str = os.getenv("ENV", "development")

    # Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))
    ANONYMOUS_USER_EMAIL: str = os.getenv("ANONYMOUS_USER_EMAIL", "anonymous@local")

    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "rag_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")

    @property
    def DATABASE_URL(self) -> str:
        """Postgres URL (sync) for SQLAlchemy."""
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)
        return f"postgresql://{user}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Storage (local filesystem only)
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "uploads"))

    # LLM / embeddings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    # RAG tuning
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))  # approximate tokens
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))  # approximate tokens
    TOP_K: int = int(os.getenv("TOP_K", "5"))
    MAX_CHAT_MEMORY_MESSAGES: int = int(os.getenv("MAX_CHAT_MEMORY_MESSAGES", "16"))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
