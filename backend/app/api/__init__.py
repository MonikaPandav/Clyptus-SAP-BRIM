from backend.app.api.auth import router as auth_router
from backend.app.api.chats import router as chats_router
from backend.app.api.messages import router as messages_router
from backend.app.api.rag import router as rag_router
from backend.app.api.admin import router as admin_router

__all__ = [
    "auth_router",
    "chats_router",
    "messages_router",
    "rag_router",
    "admin_router",
]
