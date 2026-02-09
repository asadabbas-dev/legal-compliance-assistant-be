"""Document ingestion - extract, chunk, embed, store."""

import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Chunk, Document
from app.services.embedding_service import get_embeddings
from app.services.pdf_service import chunk_text, extract_text_from_pdf

logger = logging.getLogger(__name__)


def ingest_document(db: Session, document_id: int) -> int:
    """
    Process document: extract text, chunk, embed, store.
    Returns chunk count.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise ValueError(f"Document {document_id} not found")

    file_path = Path(doc.file_path)
    if not file_path.exists():
        raise ValueError(f"File not found: {file_path}")

    db.query(Chunk).filter(Chunk.document_id == document_id).delete()

    pages = extract_text_from_pdf(file_path)
    chunks_created = 0

    for page_text, page_num in pages:
        text_chunks = chunk_text(
            page_text,
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP,
        )
        if not text_chunks:
            continue

        embeddings = get_embeddings(text_chunks)

        for i, (content, embedding) in enumerate(zip(text_chunks, embeddings)):
            chunk = Chunk(
                document_id=document_id,
                content=content,
                page_number=page_num,
                chunk_index=i,
                embedding=embedding,
            )
            db.add(chunk)
            chunks_created += 1

    db.commit()
    logger.info("Ingested document %s: %d chunks", doc.filename, chunks_created)
    return chunks_created
