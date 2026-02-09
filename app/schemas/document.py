"""Document API schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentItem(BaseModel):
    """Single document in list response."""

    id: int
    filename: str
    created_at: datetime


class DocumentResponse(BaseModel):
    """Document with id and filename (for upload response)."""

    id: int
    filename: str


class DocumentListResponse(BaseModel):
    """Response for GET /documents."""

    success: bool = True
    documents: list[DocumentItem]


class UploadResponse(BaseModel):
    """Response for POST /upload."""

    success: bool = True
    message: str
    document: DocumentResponse
