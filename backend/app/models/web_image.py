import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.database import Base


class WebImage(Base):
    """Attributed visual metadata returned by Tavily; no image data is proxied or stored."""

    __tablename__ = "web_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(2000), nullable=False)
    description = Column(Text, nullable=True)
    alt_text = Column(String(1000), nullable=True)
    source_url = Column(String(2000), nullable=True)
    source_title = Column(String(500), nullable=True)

    message = relationship("Message", back_populates="images")
