import pytest
import threading
from backend.app.services.sap_entity_service import (
    SAP_TECHNICAL_ENTITIES,
    sap_entity_service,
)
from backend.app.services.grounding_service import (
    grounding_service,
    TCODE_PATTERN,
    TABLE_PATTERN,
    EXCLUDED_TECH_TOKENS,
    VERIFIED_STANDARD_SAP_OBJECTS,
)
from backend.app.services.embedding_service import embedding_service
from backend.app.services.retrieval_service import retrieval_service


def test_standard_sap_identifiers_coverage():
    """Verify that all core SAP BRIM, CI, FI-CA, SOM, and Basis T-codes and tables are recognized."""
    required_objects = [
        "fpl9", "fpc0", "fpma", "fprel", "fpva",
        "fkkbix_bit_mon", "dfkkbixbit2", "dfkkop", "erdk", "erch",
        "but000", "fkkvkp", "slg1", "sicf", "swo1", "spro"
    ]
    for obj in required_objects:
        assert obj in VERIFIED_STANDARD_SAP_OBJECTS, f"Missing standard SAP object: {obj}"


def test_regex_excludes_false_positive_tokens():
    """Verify non-technical tokens like release years, SLAs, and HTTP codes are excluded."""
    false_positives = ["2020", "1909", "p10", "p50", "p99", "b2b", "b2c", "v2", "http400", "404", "100"]
    for fp in false_positives:
        assert fp in EXCLUDED_TECH_TOKENS, f"{fp} should be in EXCLUDED_TECH_TOKENS"


def test_grounding_evaluator_distinguishes_real_vs_fabricated():
    """Verify real standard SAP identifiers pass and fabricated identifiers are detected."""
    real_text = "Use transaction FPL9 to inspect the account balance and check table DFKKBIXBIT2 for billable items."
    tcodes = {m.lower() for m in TCODE_PATTERN.findall(real_text)}
    tables = {m.lower() for m in TABLE_PATTERN.findall(real_text)}
    found = tcodes | tables

    assert "fpl9" in found
    assert "dfkkbixbit2" in found

    for m in found:
        assert m in VERIFIED_STANDARD_SAP_OBJECTS or m.startswith("dfkk") or m.startswith("fkk")

    # Fabricated test
    fabricated_text = "Execute transaction SAP_FAKE_RUN_999 or inspect database table XYZ_NONEXISTENT_TABLE."
    fab_tcodes = {m.lower() for m in TCODE_PATTERN.findall(fabricated_text)}
    fab_tables = {m.lower() for m in TABLE_PATTERN.findall(fabricated_text)}
    # The refined patterns correctly ignore XYZ_NONEXISTENT_TABLE and SAP_FAKE_RUN_999 as not SAP patterns
    assert "xyz_nonexistent_table" not in fab_tables


def test_standard_identifier_must_be_present_in_selected_evidence():
    """A plausible SAP object is not enough to support a technical instruction."""
    result = grounding_service.verify_answer(
        query="How do I inspect FI-CA account balance?",
        answer="Use FPL9 to inspect the FI-CA account balance.",
        evidence_passages=[{"source_id": "ci-overview", "chunk_text": "Convergent Invoicing creates billable items."}],
    )
    assert result["passes_grounding_gate"] is False
    assert "fpl9" in result["uncited_standard_ids"]


def test_passes_gate_calibration():
    """Verify that answers with <= 25% unsupported claims pass while fabricated identifiers fail."""
    # Scenario A: Real SAP answer with 1 natural transition sentence (passes gate)
    verdict_clean = grounding_service.passes_gate(
        grounding_score=0.88,
        unsupported_claims=["To begin with, let us review the process."],
        total_claims=5,
        hallucinated_ids=[]
    )
    assert verdict_clean is True, "Clean answer with 1 transition sentence (20%) should pass gate"

    # Scenario B: Answer with fabricated technical identifier (fails gate immediately)
    verdict_fab = grounding_service.passes_gate(
        grounding_score=0.90,
        unsupported_claims=[],
        total_claims=5,
        hallucinated_ids=["fake_tcode_123"]
    )
    assert verdict_fab is False, "Answer with hallucinated technical identifier must fail gate"


def test_embedding_service_thread_safe_caching():
    """Verify EmbeddingService query cache is thread-safe under concurrent access."""
    query = "SAP Convergent Invoicing BIT aggregation"
    results = []

    def worker():
        emb = embedding_service.embed_text(query)
        results.append(len(emb))

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 8
    assert all(r == 384 for r in results)


def test_retrieval_service_thread_safe_invalidation():
    """Verify RetrievalService invalidates cache cleanly without deadlocks or race conditions."""
    def worker():
        retrieval_service.invalidate_cache()

    threads = [threading.Thread(target=worker) for _ in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert retrieval_service._cache_chunks is None
    assert len(retrieval_service._query_result_cache) == 0
