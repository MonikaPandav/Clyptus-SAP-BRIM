from pydantic import BaseModel, ConfigDict
from typing import Optional

class CitationResponse(BaseModel):
    id: Optional[str] = None
    chunk_id: Optional[str] = None
    source_type: Optional[str] = None
    document: str
    page: int
    section: Optional[str] = None
    score: float
    snippet: str

    model_config = ConfigDict(from_attributes=True)

class WebSourceResponse(BaseModel):
    id: Optional[str] = None
    title: str
    url: str
    domain: str
    snippet: str

    model_config = ConfigDict(from_attributes=True)
