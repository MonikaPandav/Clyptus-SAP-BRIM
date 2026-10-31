import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.app.database import Base


class UploadedAttachment(Base):
    """Extracted, user-provided text retained with its chat message for follow-ups."""

    __tablename__ = "uploaded_attachments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(500), nullable=False)
    file_type = Column(String(32), nullable=False, default="txt")
    page_count = Column(Integer, nullable=True)
    extracted_text = Column(Text, nullable=False)

    message = relationship("Message", back_populates="uploaded_attachments")
