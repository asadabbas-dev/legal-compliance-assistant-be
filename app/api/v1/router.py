"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, chat, documents, feedback, rag

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(chat.router)
api_router.include_router(rag.router)
api_router.include_router(feedback.router)
