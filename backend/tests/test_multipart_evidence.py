from backend.app.services.rag_service import RAGService
from backend.app.services.llm_service import LLMService
from backend.app.services.web_search_service import WebSearchService
from backend.app.retrieval.multi_source_compare import MultiSourceComparator
from backend.app.services.grounding_service import GroundingService
from unittest.mock import MagicMock, patch


def test_clear_multi_part_questions_are_split_for_independent_retrieval():
    query = "Explain billable-item creation; calculate the prorated amount; distinguish the FI-CA posting document."
    aspects = RAGService.split_question_aspects(query)
    assert len(aspects) == 3
    assert "billable-item creation" in aspects[0]
    assert "calculate" in aspects[1]
    assert "FI-CA" in aspects[2]


def test_single_question_is_not_artificially_split():
    query = "How does Convergent Invoicing process billable items?"
    assert RAGService.split_question_aspects(query) == [query]


def test_each_question_part_gets_retrieval_or_explicit_gap_marker():
    aspects = [
        {"aspect": "Explain CI billing", "score": 0.7, "evidence_count": 1},
        {"aspect": "Explain FI-CA posting", "score": 0.0, "evidence_count": 0},
    ]
    internal = [{"question_aspect": "Explain CI billing", "chunk_text": "CI passage"}]
    result = RAGService._ensure_aspect_coverage([internal[0]], internal, aspects)
    assert result[0]["chunk_text"] == "CI passage"
    assert result[1]["source_type"] == "retrieval_gap"
    assert "not evidence" in result[1]["chunk_text"]


def test_context_labels_release_and_non_citable_retrieval_gap():
    context = LLMService._format_evidence_context([
        {"source_type": "knowledge_base", "question_aspect": "CI billable items", "document_name": "CI Guide", "release": "2023", "chunk_text": "Documented BIT behavior."},
        {"source_type": "retrieval_gap", "question_aspect": "FI-CA posting", "chunk_text": "No passage retrieved; not proof of unsupported behavior."},
    ])
    assert "release: 2023" in context
    assert "CI billable items" in context
    assert "NOT A SOURCE" in context


def test_search_domain_validation_rejects_host_suffix_spoofing():
    assert WebSearchService._is_approved_sap_domain("https://help.sap.com/docs/product")
    assert not WebSearchService._is_approved_sap_domain("https://help.sap.com.attacker.example/docs")


def test_repository_fallback_searches_each_question_part():
    comparator = MultiSourceComparator()
    db = MagicMock()
    aspects = ["Explain CI billable-item processing", "Explain FI-CA posting"]
    with patch("backend.app.retrieval.multi_source_compare.repo_store.search_repo_chunks", return_value=[]) as search:
        comparator.execute_multi_source_comparison(
            db=db,
            query="; ".join(aspects),
            kb_candidates=[],
            repo_source_enabled=True,
            multi_source_compare_enabled=True,
            web_search_available=False,
            query_aspects=aspects,
        )
    assert [call.args[1] for call in search.call_args_list] == aspects


def test_localized_evidence_gap_does_not_zero_out_partial_answer():
    result = GroundingService().verify_answer(
        query="Explain CI and FI-CA document flow",
        answer="CI processes billable items. The FI-CA posting relationship was not established by the retrieved passages.",
        evidence_passages=[{"chunk_text": "CI processes billable items."}],
    )
    assert result["verification_status"] != "abstention"
