from backend.app.services.rag_service import RAGService


def test_kb_citation_has_stable_provenance_and_never_leaks_a_path():
    citation = RAGService._format_kb_citation({
        "chunk_id": "chunk-42",
        "document_name": r"C:\private\knowledge_base\SAP CI1.pdf",
        "page_number": 18,
        "section": "Billable item lifecycle",
        "rerank_score": 0.88,
        "chunk_text": "Billable items are processed by Convergent Invoicing.",
    })

    assert citation["chunk_id"] == "chunk-42"
    assert citation["source_type"] == "knowledge_base"
    assert citation["document"] == "SAP CI1.pdf"
    assert "C:\\" not in citation["document"]


def test_citation_deduplication_prefers_one_entry_per_chunk():
    citations = [
        {"chunk_id": "chunk-1", "document": "SAP CI1.pdf", "page": 1},
        {"chunk_id": "chunk-1", "document": "SAP CI1.pdf", "page": 1},
        {"chunk_id": "chunk-2", "document": "SAP CI1.pdf", "page": 2},
    ]
    assert len(RAGService._dedupe_citations(citations)) == 2
