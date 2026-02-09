"""Documents list endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.document import DocumentItem, DocumentListResponse
from app.services.document_service import list_documents

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
def list_documents_endpoint(db: Session = Depends(get_db)):
    """List all uploaded documents."""
    docs = list_documents(db)
    return DocumentListResponse(
        success=True,
        documents=[
            DocumentItem(id=d.id, filename=d.filename, created_at=d.created_at)
            for d in docs
        ],
    )
