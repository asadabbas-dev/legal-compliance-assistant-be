"""Document business logic - create, list."""

import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Document


def create_document(db: Session, filename: str, file_content: bytes) -> Document:
    """Save file to disk and create document record."""
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file_path = settings.UPLOAD_DIR / unique_name
    file_path.write_bytes(file_content)

    doc = Document(filename=filename, file_path=str(file_path))
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def list_documents(db: Session) -> list[Document]:
    """List all documents ordered by created_at desc."""
    return db.query(Document).order_by(Document.created_at.desc()).all()
