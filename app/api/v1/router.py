"""API v1 router - aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import ask, documents, feedback, upload

api_router = APIRouter()

api_router.include_router(upload.router)
api_router.include_router(documents.router)
api_router.include_router(ask.router)
api_router.include_router(feedback.router)
