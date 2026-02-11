"""Document schemas."""

from datetime import datetime

from pydantic import BaseModel


class DocumentItem(BaseModel):
    id: int
    filename: str
    file_type: str
    status: str
    created_at: datetime


class DocumentResponse(BaseModel):
    id: int
    filename: str


class DocumentListResponse(BaseModel):
    success: bool = True
    documents: list[DocumentItem]


class UploadResponse(BaseModel):
    success: bool = True
    message: str
    document: DocumentResponse


class ProcessDocumentRequest(BaseModel):
    document_id: int
