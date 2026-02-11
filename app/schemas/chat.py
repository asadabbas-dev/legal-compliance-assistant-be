"""Chat and message schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateChatRequest(BaseModel):
    title: str = Field(default="New chat", min_length=1, max_length=255)


class ChatResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime


class MessageCitation(BaseModel):
    document: str
    page: int
    section: str | None = None
    chunk_id: int
    similarity_score: float
    snippet: str


class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime
    citations: list[MessageCitation] = []
    confidence_score: float | None = None


class ChatHistoryResponse(BaseModel):
    chat: ChatResponse
    messages: list[ChatMessageResponse]


class ChatMessagePipelineResponse(BaseModel):
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
