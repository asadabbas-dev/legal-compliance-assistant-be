"""Application entry point - FastAPI app factory."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1.router import api_router
from app.models import Chunk, Document, Feedback  # noqa: F401 - register models

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: enable pgvector, create tables. Shutdown: cleanup."""
    logger.info("Starting up...")
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        Base.metadata.create_all(bind=engine)
        logger.info("Database ready.")
    except Exception as e:
        logger.warning("Database not available: %s. Upload/Ask will fail until DB is configured.", e)
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Legal / Compliance Knowledge Assistant API",
    description="RAG-based Q&A for company documents",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
def health():
    """Health check for load balancers / monitoring."""
    return {"status": "ok"}
