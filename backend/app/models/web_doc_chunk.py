import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean
from backend.app.database import Base
from backend.app.models.chunk import EmbeddingVector


class WebDocChunk(Base):
    """
    Dedicated isolated vector storage for ingested Official SAP Documentation and SAP Community chunks.
    Ensures existing 11,317 knowledge-base chunks in `document_chunks` and `github_repo_chunks`
    remain completely untouched and isolated.
    """
    __tablename__ = "web_doc_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(100), index=True, nullable=False)
    canonical_url = Column(String(1000), index=True, nullable=False)
    source_title = Column(String(500), nullable=False)
    source_category = Column(String(50), nullable=False)  # official_developer_doc, official_help_doc, sap_community
    provenance_tier = Column(String(50), nullable=False)  # official_sap, forum_web
    domain_module = Column(String(50), nullable=False, default="SAP_BRIM")
    product_name = Column(String(255), nullable=True)
    product_version = Column(String(100), nullable=True)
    author = Column(String(255), nullable=True)
    publication_date = Column(String(100), nullable=True)
    heading = Column(String(500), nullable=True)
    chunk_text = Column(Text, nullable=False)
    content_hash = Column(String(64), index=True, nullable=False)
    authority_weight = Column(Float, nullable=False, default=0.85)
    embedding = Column(EmbeddingVector, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


WebDocChunk = WebDocChunk
