"""Pydantic schemas for API request/response validation."""

from app.schemas.auth import LoginRequest, MeResponse, RegisterRequest, TokenResponse
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatMessagePipelineResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatResponse,
    CreateChatRequest,
)
from app.schemas.document import (
    DocumentItem,
    DocumentListResponse,
    DocumentResponse,
    ProcessDocumentRequest,
    UploadResponse,
)
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "MeResponse",
    "DocumentItem",
    "DocumentListResponse",
    "DocumentResponse",
    "ProcessDocumentRequest",
    "UploadResponse",
    "CreateChatRequest",
    "ChatResponse",
    "ChatMessageRequest",
    "ChatMessageResponse",
    "ChatHistoryResponse",
    "ChatMessagePipelineResponse",
    "RAGQueryRequest",
    "RAGQueryResponse",
    "FeedbackRequest",
    "FeedbackResponse",
]
