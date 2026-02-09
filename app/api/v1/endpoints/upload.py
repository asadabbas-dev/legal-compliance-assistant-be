"""Upload PDF endpoint."""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.document import DocumentResponse, UploadResponse
from app.services.document_service import create_document
from app.services.ingestion_service import ingest_document
from app.core.database import SessionLocal

router = APIRouter(prefix="/upload", tags=["upload"])
logger = logging.getLogger(__name__)


@router.post("", response_model=UploadResponse)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a PDF file and trigger background ingestion."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    content = await file.read()
    doc = create_document(db, filename=file.filename, file_content=content)

    background_tasks.add_task(_run_ingestion, doc.id)

    return UploadResponse(
        success=True,
        message="File uploaded. Ingestion in progress.",
        document=DocumentResponse(id=doc.id, filename=doc.filename),
    )


def _run_ingestion(document_id: int) -> None:
    """Background task - ingest document in separate session."""
    db = SessionLocal()
    try:
        ingest_document(db, document_id)
    except Exception as e:
        logger.exception("Ingestion failed for document %s: %s", document_id, e)
    finally:
        db.close()
