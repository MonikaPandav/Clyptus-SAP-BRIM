import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class WebSource(Base):
    __tablename__ = "web_sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(1000), nullable=False)
    title = Column(String(500), nullable=False)
    domain = Column(String(255), nullable=False)
    snippet = Column(Text, nullable=False)

    message = relationship("Message", back_populates="web_sources")
