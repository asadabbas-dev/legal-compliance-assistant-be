"""Chat endpoints."""

from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth.deps import get_optional_current_user
from app.models import User
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatMessagePipelineResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatResponse,
    CreateChatRequest,
)
from app.services.chat_service import (
    create_chat,
    get_chat,
    get_chat_messages,
    list_chats,
    process_chat_message,
)
from app.services.rag_service import query_rag
from app.services.user_service import get_or_create_anonymous_user

router = APIRouter(prefix="/chat", tags=["chat"])


def _to_chat_response(chat) -> ChatResponse:
    return ChatResponse(id=chat.id, title=chat.title, created_at=chat.created_at)


def _to_message_response(message) -> ChatMessageResponse:
    meta = message.metadata_json or {}
    return ChatMessageResponse(
        id=message.id,
        role=message.role,
        content=message.content,
        created_at=message.created_at,
        citations=meta.get("citations", []),
        confidence_score=meta.get("confidence_score"),
    )


@router.post("/create", response_model=ChatResponse)
def create_chat_endpoint(
    body: CreateChatRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if not current_user:
        return ChatResponse(id=uuid4(), title=body.title, created_at=datetime.utcnow())
    chat = create_chat(db, user_id=current_user.id, title=body.title)
    return _to_chat_response(chat)


@router.get("", response_model=list[ChatResponse])
def list_chat_endpoint(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if not current_user:
        return []
    chats = list_chats(db, user_id=current_user.id)
    return [_to_chat_response(c) for c in chats]


@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat_endpoint(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if not current_user:
        return ChatResponse(id=chat_id, title="Guest chat", created_at=datetime.utcnow())
    chat = get_chat(db, user_id=current_user.id, chat_id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return _to_chat_response(chat)


@router.get("/{chat_id}/history", response_model=ChatHistoryResponse)
def get_history(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if not current_user:
        return ChatHistoryResponse(
            chat=ChatResponse(id=chat_id, title="Guest chat", created_at=datetime.utcnow()),
            messages=[],
        )
    chat = get_chat(db, user_id=current_user.id, chat_id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    rows = get_chat_messages(db, user_id=current_user.id, chat_id=chat_id)
    return ChatHistoryResponse(chat=_to_chat_response(chat), messages=[_to_message_response(m) for m in rows])


@router.post("/{chat_id}/message", response_model=ChatMessagePipelineResponse)
def post_message(
    chat_id: UUID,
    body: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if not current_user:
        guest = get_or_create_anonymous_user(db)
        rag = query_rag(db, user_id=guest.id, question=body.content)
        now = datetime.utcnow()
        return ChatMessagePipelineResponse(
            user_message=ChatMessageResponse(
                id=uuid4(),
                role="user",
                content=body.content,
                created_at=now,
                citations=[],
                confidence_score=None,
            ),
            assistant_message=ChatMessageResponse(
                id=uuid4(),
                role="assistant",
                content=rag.answer,
                created_at=now,
                citations=[
                    {
                        "document": c.document,
                        "page": c.page,
                        "section": c.section,
                        "chunk_id": c.chunk_id,
                        "similarity_score": c.similarity_score,
                        "snippet": c.snippet,
                    }
                    for c in rag.citations
                ],
                confidence_score=rag.confidence_score,
            ),
        )
    try:
        user_msg, assistant_msg = process_chat_message(
            db,
            user_id=current_user.id,
            chat_id=chat_id,
            content=body.content,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ChatMessagePipelineResponse(
        user_message=_to_message_response(user_msg),
        assistant_message=_to_message_response(assistant_msg),
    )
