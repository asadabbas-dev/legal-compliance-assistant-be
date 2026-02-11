"""Document endpoints: upload/process/list/get."""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.deps import get_optional_current_user
from app.models import User
from app.schemas.document import (
    DocumentItem,
    DocumentListResponse,
    DocumentResponse,
    ProcessDocumentRequest,
    UploadResponse,
)
from app.services.document_service import create_document, get_document, list_documents
from app.services.ingestion_service import ingest_document
from app.services.user_service import get_or_create_anonymous_user
from app.core.database import SessionLocal

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)

def _run_ingestion(document_id: int) -> None:
    local_db = SessionLocal()
    try:
        ingest_document(local_db, document_id)
    except Exception:
        logger.exception("Ingestion background task failed for document_id=%s", document_id)
    finally:
        local_db.close()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    actor = current_user or get_or_create_anonymous_user(db)
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    name = file.filename.lower()
    if not (name.endswith(".pdf") or name.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX are supported")
    content = await file.read()
    file_type = file.content_type or ("application/pdf" if name.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    document = create_document(
        db,
        user_id=actor.id,
        filename=file.filename,
        file_type=file_type,
        file_bytes=content,
    )
    background_tasks.add_task(_run_ingestion, document.id)
    return UploadResponse(
        success=True,
        message="File uploaded. Ingestion started.",
        document=DocumentResponse(id=document.id, filename=document.filename),
    )


@router.post("/process")
def process_document(
    payload: ProcessDocumentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    actor = current_user or get_or_create_anonymous_user(db)
    document_id = payload.document_id
    document = get_document(db, actor.id, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    background_tasks.add_task(_run_ingestion, document.id)
    return {"success": True, "message": "Processing triggered", "document_id": document.id}


@router.get("", response_model=DocumentListResponse)
def list_documents_endpoint(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    actor = current_user or get_or_create_anonymous_user(db)
    docs = list_documents(db, actor.id)
    return DocumentListResponse(
        success=True,
        documents=[
            DocumentItem(
                id=d.id,
                filename=d.filename,
                file_type=d.file_type,
                status=d.status,
                created_at=d.created_at,
            )
            for d in docs
        ],
    )


@router.get("/{document_id}", response_model=DocumentItem)
def get_document_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    actor = current_user or get_or_create_anonymous_user(db)
    d = get_document(db, actor.id, document_id)
    if not d:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentItem(
        id=d.id,
        filename=d.filename,
        file_type=d.file_type,
        status=d.status,
        created_at=d.created_at,
    )
