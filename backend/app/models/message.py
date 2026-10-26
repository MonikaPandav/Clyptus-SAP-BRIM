import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String(36), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # 'user', 'assistant'
    content = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=True)  # 'knowledge_base', 'web', 'refusal', 'error'
    grounding_score = Column(Float, nullable=True)
    feedback = Column(String(10), nullable=True)  # 'up', 'down' or NULL; assistant answers only
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    chat = relationship("Chat", back_populates="messages")
    citations = relationship("Citation", back_populates="message", cascade="all, delete-orphan")
    web_sources = relationship("WebSource", back_populates="message", cascade="all, delete-orphan")
    images = relationship("WebImage", back_populates="message", cascade="all, delete-orphan")
    uploaded_attachments = relationship("UploadedAttachment", back_populates="message", cascade="all, delete-orphan")
