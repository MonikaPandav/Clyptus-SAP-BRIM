"""
Golden Regression Test: 20 Representative Queries.
Verifies that with all flags default OFF:
- Legacy retrieval produces 100% deterministic, identical candidates
- All existing API response fields are preserved without change
- No fields are renamed or removed
"""

import pytest
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.database import SessionLocal, init_db
from backend.app.services.retrieval_service import retrieval_service

REPRESENTATIVE_QUERIES = [
    "What is SAP BRIM?",
    "What is Convergent Charging?",
    "Explain the 3-Way Match verification process in SAP MM",
    "What is a Billable Item in Convergent Invoicing?",
    "Explain Contract Accounts Receivable and Payable in FI-CA",
    "How does CC integrate with CI?",
    "What is a Consumption Item in SAP CC?",
    "What is the function of table DFKKOP in FI-CA?",
    "How does the Order Distribution Infrastructure (ODI) work in SOM?",
    "Explain revenue recognition in SAP RAR",
    "What transaction code is used for account balance display in FI-CA?",
    "What is transaction FPCM1 used for?",
    "Explain master agreement configuration in SAP SOM",
    "What are the components of a charge plan in SAP CC?",
    "How are billable items aggregated during invoicing in CI?",
    "Explain clearing control in SAP FI-CA",
    "What is transaction SPRO used for in SAP?",
    "Explain device as a service in SAP BRIM SOM",
    "How does SAP Ariba integrate with S/4HANA for supplier sourcing?",
    "What is budget billing in FI-CA?"
]

REQUIRED_CHUNK_FIELDS = {
    "chunk_id", "document_id", "document_name", "source_type",
    "page_number", "section", "chunk_text", "snippet",
    "vector_score", "bm25_score", "rrf_score", "score"
}


@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    yield db
    db.close()


def test_flags_default_off():
    """Verify that all new architectural feature flags are strictly default OFF."""
    assert settings.SHADOW_MODE_ENABLED is False
    assert settings.EXCLUDE_OFF_DOMAIN_DOCS is False
    assert settings.USE_CORPUS_METADATA_V2 is False


def test_20_queries_golden_retrieval_consistency(db_session: Session):
    """
    Executes 20 representative queries twice with all flags OFF and asserts
    identical retrieval candidates, rankings, and response structures.
    """
    for query in REPRESENTATIVE_QUERIES:
        # Run 1
        results_1 = retrieval_service.hybrid_search(db_session, query, top_k=5)
        # Run 2
        results_2 = retrieval_service.hybrid_search(db_session, query, top_k=5)

        assert len(results_1) > 0, f"Query '{query}' returned no results"
        assert len(results_1) == len(results_2), f"Mismatch in count for '{query}'"

        # Assert identical chunk IDs and ranking
        ids_1 = [r["chunk_id"] for r in results_1]
        ids_2 = [r["chunk_id"] for r in results_2]
        assert ids_1 == ids_2, f"Ranking order changed between runs for '{query}'"

        # Assert all required fields exist on every chunk
        for chunk in results_1:
            for field in REQUIRED_CHUNK_FIELDS:
                assert field in chunk, f"Missing required response field '{field}' in chunk"
                assert chunk[field] is not None or field in ("section", "document_id")
