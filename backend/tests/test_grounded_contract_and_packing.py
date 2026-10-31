import json
import uuid
import pytest
from unittest.mock import MagicMock, patch

from backend.app.config import settings
from backend.app.database import SessionLocal, init_db
from backend.app.services.retrieval_service import retrieval_service
from backend.app.schemas.grounded_generation import (
    GroundedAnswerResponse,
    GroundedClaim,
    ContextPackingResult
)
from backend.app.services.context_packing_service import (
    ContextPackingService,
    context_packing_service
)
from backend.app.services.grounded_generator_service import (
    GroundedGeneratorService,
    grounded_generator_service
)


# ==============================================================================
# STEP 2 TESTS: CONTEXT PACKING CORRECTIONS
# ==============================================================================

def test_context_packing_header_format():
    """Verify chunk format is exactly: [chunk_id | tier | module | source | page] followed by text."""
    service = ContextPackingService()
    service.calibrated_threshold = 0.40

    raw_chunks = [
        {
            "chunk_id": "chunk-101",
            "document_name": "SAP CI1.pdf",
            "page_number": 42,
            "chunk_text": "Billable items are created with status 0 (raw) or 2 (billable).",
            "score": 0.85
        }
    ]

    res = service.pack_context("How are billable items processed in CI?", raw_chunks)
    assert res.is_insufficient is False
    assert len(res.packed_chunks) == 1

    header = res.packed_chunks[0].to_context_header()
    assert header == "[chunk-101 | official_sap | CI | SAP CI1.pdf | 42]"
    assert "[chunk-101 | official_sap | CI | SAP CI1.pdf | 42]\nBillable items are created with status 0 (raw) or 2 (billable)." in res.packed_text


def test_context_packing_ranks_by_relevance_x_tier_weight():
    """Verify chunks are ranked by relevance x configurable tier weight (not tier first)."""
    service = ContextPackingService()
    service.calibrated_threshold = 0.40

    # Book with very high relevance (0.95 * 0.85 = 0.8075)
    # Official SAP with moderate relevance (0.75 * 1.0 = 0.750)
    raw_chunks = [
        {
            "chunk_id": "official-1",
            "document_name": "SAP CC.pdf",
            "page_number": 20,
            "chunk_text": "Standard charge plan configuration in CC.",
            "score": 0.75
        },
        {
            "chunk_id": "book-1",
            "document_name": "SAP BRIM Press Book 2nd Edition - Expertsoft.pdf",
            "page_number": 12,
            "chunk_text": "Architectural guidelines for CC charge plans.",
            "score": 0.95
        }
    ]

    res = service.pack_context("Explain charge plans in CC", raw_chunks)
    assert len(res.packed_chunks) == 2
    # Because 0.95 * 0.85 (0.8075) > 0.75 * 1.0 (0.75), book-1 ranks first
    assert res.packed_chunks[0].chunk_id == "book-1"
    assert res.packed_chunks[1].chunk_id == "official-1"


def test_context_packing_deduplication_keeps_highest_tier():
    """Verify deduplication keeps the highest-tier copy among near-duplicates."""
    service = ContextPackingService()
    service.calibrated_threshold = 0.40
    service.dedupe_threshold = 0.80

    text = "The rating engine in SAP Convergent Charging evaluates chargeable items using charge plans and range tables."

    raw_chunks = [
        {
            "chunk_id": "self-1",
            "document_name": "synthetic_notes.txt",
            "page_number": 1,
            "chunk_text": text,
            "score": 0.92  # Higher relevance but lower tier
        },
        {
            "chunk_id": "official-1",
            "document_name": "SAP CC.pdf",
            "page_number": 15,
            "chunk_text": text,
            "score": 0.90  # Official SAP tier
        }
    ]

    res = service.pack_context("How does CC rate events?", raw_chunks)
    assert len(res.packed_chunks) == 1
    # Must keep official_sap copy, not self_authored
    assert res.packed_chunks[0].chunk_id == "official-1"
    assert res.packed_chunks[0].tier == "official_sap"


def test_context_packing_splits_web_tier():
    """Verify web chunks are categorized into official-sap-domain vs forum."""
    service = ContextPackingService()

    official_web = {"source_type": "web", "url": "https://help.sap.com/docs/brim", "document_name": "help.sap.com", "page_number": 1, "score": 0.8}
    forum_web = {"source_type": "web", "url": "https://community.sap.com/blogs/user/brim-tips", "document_name": "community.sap.com", "page_number": 1, "score": 0.8}

    assert service.infer_chunk_tier(official_web) == "official-sap-domain"
    assert service.infer_chunk_tier(forum_web) == "forum"


def test_context_packing_dynamic_budget_scaling():
    """Verify token budget scales dynamically with detected modules."""
    service = ContextPackingService()
    service.base_budget = 1500
    service.per_module_budget = 600
    service.max_token_limit = 5000

    single_mod = service.compute_dynamic_budget(["CI"])
    assert single_mod == 2100

    three_mods = service.compute_dynamic_budget(["SOM", "CC", "CI"])
    assert three_mods == 3300


# ==============================================================================
# STEP 1 TESTS: GENERATION CONTRACT & PARSER CORRECTIONS
# ==============================================================================

def test_generation_contract_loads_system_prompt_with_glossary_and_premise_rule():
    """Verify system prompt contains fixed glossary, premise correction rule, and identifier rule."""
    generator = GroundedGeneratorService()
    prompt = generator.load_system_prompt()
    assert "FIXED ACRONYM GLOSSARY" in prompt
    assert "PREMISE CORRECTION RULE" in prompt
    assert "CRITICAL IDENTIFIER RULE" in prompt
    assert "calculations" in prompt


def test_strip_reasoning_and_preamble_before_json_parsing():
    """Verify <think> reasoning blocks and introductory preambles are stripped cleanly."""
    generator = GroundedGeneratorService()

    raw_model_response = (
        "Here is the requested SAP analysis:\n\n"
        "<think>\n"
        "Let me examine chunk-101. The transaction is FPC1 in Convergent Invoicing.\n"
        "We should format the output conforming to the GroundedAnswerResponse schema.\n"
        "</think>\n"
        "```json\n"
        "{\n"
        '  "summary": "Convergent Invoicing aggregates billable items into billing documents.",\n'
        '  "sections": [{"title": "CI Overview", "module": "CI"}],\n'
        '  "claims": [{\n'
        '    "claim_id": "c1",\n'
        '    "text": "FPC1 executes invoicing of billable items.",\n'
        '    "citations": ["chunk-101"],\n'
        '    "identifiers_used": ["FPC1"],\n'
        '    "module": "CI",\n'
        '    "support": "direct"\n'
        "  }],\n"
        '  "calculations": [],\n'
        '  "premise_correction": null,\n'
        '  "gaps": [],\n'
        '  "next_questions": ["What is FPC0 used for?"]\n'
        "}\n"
        "```\n"
    )

    stripped = generator.strip_reasoning_and_preamble(raw_model_response)
    assert "<think>" not in stripped
    assert stripped.startswith("{")
    assert stripped.endswith("}")

    validated = generator._parse_and_validate(raw_model_response)
    assert validated.summary == "Convergent Invoicing aggregates billable items into billing documents."
    assert validated.claims[0].identifiers_used == ["FPC1"]


def test_contract_gaps_cannot_contain_identifiers_absent_from_context():
    """Verify gaps cannot introduce ungrounded technical identifiers absent from context."""
    from backend.app.services.evidence_selection_service import EvidenceSelectionService

    context_text = "Standard subscription order processing in SOM. Provider orders are created."
    known_tech_ids = EvidenceSelectionService._extract_technical_identifiers(context_text)

    gap_valid = "Pricing logic configuration for mass migration was not found in context."
    gap_invalid = "The specific transaction code /1FE/FAKE_TCODE_999 and table DFKK_FABRICATED were missing."

    invalid_ids = [
        tid for tid in EvidenceSelectionService._extract_technical_identifiers(gap_invalid)
        if tid not in known_tech_ids
    ]
    assert len(invalid_ids) > 0
    assert "/1fe/fake_tcode_999" in invalid_ids or "dfkk_fabricated" in invalid_ids

    valid_ids = [
        tid for tid in EvidenceSelectionService._extract_technical_identifiers(gap_valid)
        if tid not in known_tech_ids
    ]
    assert len(valid_ids) == 0


def test_rate_limit_backoff_handling():
    """Verify 429 errors trigger backoff retries and report rate_limited status on exhaustion."""
    generator = GroundedGeneratorService()
    generator.max_rate_limit_retries = 2
    generator.base_backoff_sec = 0.01  # Fast backoff for test

    with patch.object(generator, "_call_fixed_generator_with_backoff", return_value=(None, "rate_limited")):
        packing = ContextPackingResult(
            packed_chunks=[],
            packed_text="[c1 | official_sap | SOM | som.pdf | 1]\nText",
            is_insufficient=False,
            top_score=0.85
        )
        res = generator.generate_grounded_answer("How does SOM work?", packing)
        assert res["status"] == "rate_limited"
        assert res["answer_response"].is_abstention is True
        assert "Rate limit" in res["answer_response"].abstention_reason


# ==============================================================================
# INTEGRATION TEST: REAL RETRIEVER & REAL CHUNK UUIDs
# ==============================================================================

def test_integration_real_retriever_and_chunk_uuids():
    """
    Integration test using real retriever and real chunk UUIDs from the live database.
    Verifies that real UUIDs are retrieved, formatted into packed headers, and preserved.
    """
    init_db()
    db = SessionLocal()
    try:
        query = "Explain billable item classes in Convergent Invoicing"
        retrieved = retrieval_service.hybrid_search(db, query, top_k=5)
        assert len(retrieved) > 0

        # Verify real chunk UUID structure
        top_chunk = retrieved[0]
        cid = top_chunk["chunk_id"]
        # Validate that chunk_id is a valid UUID string
        parsed_uuid = uuid.UUID(str(cid))
        assert parsed_uuid is not None

        # Pack real context
        packing = context_packing_service.pack_context(query, retrieved)
        assert packing.is_insufficient is False
        assert len(packing.packed_chunks) > 0

        retrieved_ids = [c["chunk_id"] for c in retrieved]
        first_packed = packing.packed_chunks[0]
        assert first_packed.chunk_id in retrieved_ids
        assert f"[{first_packed.chunk_id} | " in packing.packed_text
        assert first_packed.tier in ("official_sap", "book", "self_authored", "official-sap-domain", "forum")
    finally:
        db.close()
