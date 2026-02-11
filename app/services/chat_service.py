"""Chat service for creation/history/message processing."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Chat, ChatMessage
from app.services.embedding_service import get_embedding
from app.services.rag_service import query_rag


def create_chat(db: Session, *, user_id: UUID, title: str) -> Chat:
    chat = Chat(user_id=user_id, title=title)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_chat(db: Session, *, user_id: UUID, chat_id) -> Chat | None:
    return db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()


def list_chats(db: Session, *, user_id: UUID) -> list[Chat]:
    return db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.created_at.desc()).all()


def get_chat_messages(db: Session, *, user_id: UUID, chat_id) -> list[ChatMessage]:
    chat = get_chat(db, user_id=user_id, chat_id=chat_id)
    if not chat:
        return []
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def process_chat_message(db: Session, *, user_id: UUID, chat_id, content: str):
    chat = get_chat(db, user_id=user_id, chat_id=chat_id)
    if not chat:
        raise ValueError("Chat not found")

    user_msg = ChatMessage(
        chat_id=chat_id,
        role="user",
        content=content,
        embedding=get_embedding(content),
        metadata_json={},
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    rag = query_rag(db, user_id=user_id, question=content, chat_id=chat_id)
    citations_payload = [
        {
            "document": c.document,
            "page": c.page,
            "section": c.section,
            "chunk_id": c.chunk_id,
            "similarity_score": c.similarity_score,
            "snippet": c.snippet,
        }
        for c in rag.citations
    ]

    assistant_msg = ChatMessage(
        chat_id=chat_id,
        role="assistant",
        content=rag.answer,
        metadata_json={
            "citations": citations_payload,
            "confidence_score": rag.confidence_score,
        },
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)
    return user_msg, assistant_msg
