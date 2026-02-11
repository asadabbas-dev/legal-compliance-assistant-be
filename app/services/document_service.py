"""Document persistence and storage operations."""

from __future__ import annotations

import tempfile
import uuid
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Document
from app.services.storage_service import get_storage_service


def build_storage_key(user_id: UUID, filename: str) -> str:
    return f"{user_id}/{uuid.uuid4().hex}_{filename}"


def create_document(
    db: Session,
    *,
    user_id: UUID,
    filename: str,
    file_type: str,
    file_bytes: bytes,
) -> Document:
    storage = get_storage_service()
    key = build_storage_key(user_id, filename)
    storage.put_bytes(key, file_bytes, content_type=file_type)

    document = Document(
        user_id=user_id,
        filename=filename,
        file_type=file_type,
        storage_path=key,
        status="pending",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def list_documents(db: Session, user_id: UUID) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .all()
    )


def get_document(db: Session, user_id: UUID, document_id: int) -> Document | None:
    return (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == user_id)
        .first()
    )


def get_document_by_id(db: Session, document_id: int) -> Document | None:
    return db.query(Document).filter(Document.id == document_id).first()


def set_document_status(db: Session, document: Document, status: str) -> None:
    document.status = status
    db.commit()


def materialize_document_to_local_temp(document: Document) -> Path:
    """Return a local filesystem path for processing."""
    storage = get_storage_service()
    local_path = storage.get_local_path(document.storage_path)
    if local_path:
        return local_path
    data = storage.get_bytes(document.storage_path)
    suffix = Path(document.filename).suffix or ".bin"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(data)
    tmp.close()
    return Path(tmp.name)
