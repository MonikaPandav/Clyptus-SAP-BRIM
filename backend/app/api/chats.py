import logging
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from starlette.concurrency import run_in_threadpool

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.chat import Chat
from backend.app.models.message import Message
from backend.app.schemas.chat import ChatCreate, ChatUpdate, ChatResponse, ChatListItem
from backend.app.schemas.message import DocumentExtractResponse
from backend.app.services.document_extractor import extract_document
from backend.app.security.auth import get_current_user, get_optional_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat(
    chat_in: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # For demo / guest users, purge prior ephemeral chats so guest chats do not store
    if current_user.email == "consultant@clyptusap.ai":
        old_chats = db.query(Chat).filter(Chat.user_id == current_user.id).all()
        for oc in old_chats:
            db.query(Message).filter(Message.chat_id == oc.id).delete(synchronize_session=False)
            db.delete(oc)
        db.commit()

    chat = Chat(
        user_id=current_user.id,
        title=chat_in.title or "New SAP Chat"
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return ChatResponse.model_validate(chat)

@router.get("", response_model=List[ChatListItem])
def list_chats(
    search: Optional[str] = Query(None, description="Search chats by title"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Never return persistent saved chats for the guest / demo user
    if current_user.email == "consultant@clyptusap.ai":
        return []

    query = (
        db.query(
            Chat.id,
            Chat.user_id,
            Chat.title,
            Chat.created_at,
            Chat.updated_at,
            func.count(Message.id).label("message_count")
        )
        .outerjoin(Message, Message.chat_id == Chat.id)
        .filter(Chat.user_id == current_user.id)
    )

    if search:
        query = query.filter(Chat.title.ilike(f"%{search}%"))

    results = (
        query.group_by(Chat.id)
        .order_by(Chat.updated_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        ChatListItem(
            id=r.id,
            user_id=r.user_id,
            title=r.title,
            created_at=r.created_at,
            updated_at=r.updated_at,
            message_count=r.message_count
        )
        for r in results
    ]

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Strictly query by both chat_id and authenticated user_id to prevent enumeration or cross-user leaks
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    return ChatResponse.model_validate(chat)

@router.patch("/{chat_id}", response_model=ChatResponse)
def update_chat(
    chat_id: str,
    chat_in: ChatUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    chat.title = chat_in.title.strip()
    chat.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(chat)
    return ChatResponse.model_validate(chat)

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    db.delete(chat)
    db.commit()
    return None

@router.post("/extract-document", response_model=DocumentExtractResponse)
async def extract_chat_document(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Extracts text and page metadata from uploaded PDF, Word (DOCX), PNG, or plain text documents.
    Enforces maximum file size limit of 25MB and returns structured content for question answering.
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded")

    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 25MB limit."
        )

    try:
        extracted = await run_in_threadpool(extract_document, file.filename, content)
        if not extracted.get("text", "").strip():
            raise ValueError(f"No readable text could be extracted from '{file.filename}'.")
        return DocumentExtractResponse(**extracted)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing document {file.filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract document contents. Please try another supported file."
        )
