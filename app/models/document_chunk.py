"""Vectorized document chunks for retrieval."""

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

EMBEDDING_DIM = 1536


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)
    page_number = Column(Integer, nullable=False, default=1)
    section = Column(String(255), nullable=True)
    token_count = Column(Integer, nullable=False, default=0)
    metadata_json = Column(JSONB, nullable=True)

    document = relationship("Document", back_populates="chunks")
