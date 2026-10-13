import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from backend.app.database import Base
from backend.app.models.chunk import EmbeddingVector


class GithubRepoChunk(Base):
    """
    Dedicated isolated vector storage for ingested GitHub repository chunks.
    Ensures existing 10,661 knowledge-base chunks in `document_chunks` remain completely untouched.
    """
    __tablename__ = "github_repo_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repo_url = Column(String(255), index=True, nullable=False)
    repo_name = Column(String(255), nullable=False)
    commit_hash = Column(String(64), nullable=False)
    file_path = Column(String(500), nullable=False)
    section = Column(String(255), nullable=True)
    chunk_text = Column(Text, nullable=False)
    content_hash = Column(String(64), index=True, nullable=False)
    license = Column(String(50), nullable=False, default="unknown")
    license_status = Column(String(50), nullable=False, default="unknown")
    provenance_tier = Column(String(50), nullable=False, default="github_repo")
    module = Column(String(50), nullable=False, default="unknown")
    anchor_similarity = Column(Float, nullable=False, default=0.0)
    relevance_gate_version = Column(String(20), nullable=False, default="1.0")
    embedding = Column(EmbeddingVector, nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


GitHubRepoChunk = GithubRepoChunk
