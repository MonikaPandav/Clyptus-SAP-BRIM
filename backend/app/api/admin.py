from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.security.auth import verify_admin_key_or_user
from backend.app.ingestion.ingest import run_ingestion

router = APIRouter(prefix="/admin", tags=["Admin / Developer Ingestion"])

@router.post("/documents/ingest")
def trigger_ingestion(
    authorized: bool = Depends(verify_admin_key_or_user),
    db: Session = Depends(get_db)
):
    """
    Developer-only ingestion endpoint.
    Scans backend/knowledge_base/documents/ for PDFs, extracts, chunks, embeds, and stores them.
    """
    results = run_ingestion(db)
    return {
        "status": "success",
        "message": "Ingestion process completed successfully.",
        "details": results
    }
