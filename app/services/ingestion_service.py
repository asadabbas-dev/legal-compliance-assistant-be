"""Background ingestion pipeline for documents."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import DocumentChunk
from app.services.chunking_service import semantic_chunk_pages
from app.services.document_service import (
    get_document_by_id,
    materialize_document_to_local_temp,
    set_document_status,
)
from app.services.embedding_service import get_embeddings
from app.services.text_extraction_service import extract_text

logger = logging.getLogger(__name__)


def ingest_document(db: Session, document_id: int) -> int:
    """Ingest one document into vector chunks."""
    document = get_document_by_id(db, document_id)
    if not document:
        raise ValueError(f"Document {document_id} not found")

    set_document_status(db, document, "processing")
    local_path = materialize_document_to_local_temp(document)

    try:
        pages = extract_text(local_path, document.file_type)
        chunks = semantic_chunk_pages(
            pages,
            chunk_size_tokens=settings.CHUNK_SIZE,
            overlap_tokens=settings.CHUNK_OVERLAP,
        )

        db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()

        if not chunks:
            set_document_status(db, document, "ready")
            return 0

        embeddings = get_embeddings([c.chunk_text for c in chunks])
        for chunk, embedding in zip(chunks, embeddings):
            row = DocumentChunk(
                document_id=document.id,
                user_id=document.user_id,
                chunk_text=chunk.chunk_text,
                embedding=embedding,
                page_number=chunk.page_number,
                section=chunk.section,
                token_count=chunk.token_count,
                metadata_json={"source": document.filename},
            )
            db.add(row)

        db.commit()
        set_document_status(db, document, "ready")
        return len(chunks)
    except Exception:
        set_document_status(db, document, "failed")
        logger.exception("Ingestion failed for document_id=%s", document_id)
        raise
    finally:
        if str(local_path).startswith(tempfile.gettempdir()):
            try:
                Path(local_path).unlink(missing_ok=True)
            except Exception:
                pass
