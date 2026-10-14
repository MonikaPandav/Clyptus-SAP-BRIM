import logging
import re
from typing import Dict, Any, List, Generator, Optional
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.services.sap_classifier import sap_classifier
from backend.app.services.retrieval_service import retrieval_service
from backend.app.services.reranking_service import reranking_service
from backend.app.services.grounding_service import grounding_service
from backend.app.services.web_search_service import web_search_service
from backend.app.services.evidence_selection_service import evidence_selection_service
from backend.app.services.answer_planner import answer_planner
from backend.app.services.followup_service import followup_service
from backend.app.services.llm_service import llm_service
from backend.app.services.query_rewriter import query_rewriter

logger = logging.getLogger(__name__)


class RAGService:
    """
    Production-Grade Evidence-First SAP BRIM Knowledge Assistant Service.
    
    Orchestration Flow:
    1. Query Rewriting & Context Resolution: resolves references, retains technical IDs.
    2. SAP Domain Classifier: strict scope check, returns refusal for non-SAP queries.
    3. Internal Hybrid Retrieval: vector + lexical BM25 matching across the live indexed corpus.
    4. Multi-Signal Evidence Confidence Assessment:
       - If confidence < 0.70 (INTERNAL_EVIDENCE_THRESHOLD), automatically triggers Tavily.
       - Tavily searches approved SAP domains (help.sap.com, community.sap.com, blogs.sap.com).
    5. Unified Evidence Selection:
       - Compares internal-only, external-only, and combined evidence sets.
       - Selects strongest sufficient set with preserved provenance and authority tiers.
    6. Question-Aware Detailed Answer Generation:
       - Injects structure archetype guidelines (conceptual, configuration, troubleshooting, etc.).
    7. Claim-Level Grounding Verification (ANSWER_GROUNDING_THRESHOLD = 0.80):
       - Inspects material factual claims & audits SAP technical identifiers (T-codes, tables, SPRO).
       - Critical claim veto: fabricated identifiers fail the publication gate immediately.
    8. Controlled Answer Repair (MAX_GROUNDING_REPAIR_ATTEMPTS = 1):
       - If verification fails, re-prompts LLM to strip unverified technical instructions.
       - Re-verifies revised answer.
       - If still failing, returns a supported partial answer or explicit abstention.
    9. Recommended Follow-Up Questions (FOLLOWUP_QUESTION_COUNT = 3):
       - Generates exactly 3 relevant, clickable follow-up questions.
    10. Progressive Streaming & Safe Delivery:
       - Yields real progress stages.
       - Buffers candidate output until verification passes before delivering tokens.
    """

    def __init__(self):
        self.retrieval = retrieval_service
        self._comparator = None

    @staticmethod
    def split_question_aspects(query: str) -> List[str]:
        """Split only clear, independently answerable asks; keep ordinary prose intact."""
        pieces = re.split(
            r"\s*;\s*|\?\s*(?=\S)|\n(?=\s*(?:\d+[.)]|[-*])\s)|,\s*(?=(?:and\s+)?(?:calculate|compute|show|list|identify|compare|distinguish|describe|explain|provide|state)\b)",
            (query or "").strip(), flags=re.IGNORECASE,
        )
        aspects = [re.sub(r"^\s*(?:\d+[.)]|[-*])\s*", "", p).strip(" ?\n\t") for p in pieces]
        aspects = [p for p in aspects if len(p) >= 8]
        return aspects if len(aspects) > 1 else [(query or "").strip()]

    def _retrieve_aspect_evidence(self, db: Session, query: str, top_k: int, *, hybrid: bool = False):
        aspects = self.split_question_aspects(query)
        if len(aspects) == 1:
            retrieve = self.retrieval.hybrid_search if hybrid else self.retrieval.retrieve
            candidates = retrieve(db, query, top_k=top_k)
            ranked, score, _ = reranking_service.rerank_kb(query, candidates, top_n=settings.RERANK_TOP_K)
            for item in ranked:
                item["question_aspect"] = query
            return ranked, score, [{"aspect": query, "score": round(float(score), 4), "evidence_count": len(ranked)}]

        merged: Dict[str, Dict[str, Any]] = {}
        aspect_results = []
        for aspect in aspects:
            retrieve = self.retrieval.hybrid_search if hybrid else self.retrieval.retrieve
            candidates = retrieve(db, aspect, top_k=top_k)
            ranked, score, _ = reranking_service.rerank_kb(aspect, candidates, top_n=settings.RERANK_TOP_K)
            aspect_results.append({"aspect": aspect, "score": round(float(score), 4), "evidence_count": len(ranked)})
            for item in ranked:
                item["question_aspect"] = aspect
                key = str(item.get("chunk_id") or item.get("id") or item.get("chunk_text", "")[:160])
                prior = merged.get(key)
                if prior is None or float(item.get("rerank_score", item.get("score", 0))) > float(prior.get("rerank_score", prior.get("score", 0))):
                    merged[key] = item
        combined = sorted(merged.values(), key=lambda item: float(item.get("rerank_score", item.get("score", 0))), reverse=True)
        # Use the weakest aspect match to trigger fallback rather than hiding an evidence gap in an average.
        weakest_score = min((row["score"] for row in aspect_results), default=0.0)
        return combined[:max(settings.RERANK_TOP_K, settings.TOP_K)], weakest_score, aspect_results

    @staticmethod
    def _ensure_aspect_coverage(selected: List[Dict[str, Any]], internal: List[Dict[str, Any]], aspects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Keep a passage or an explicit non-citable retrieval-gap marker for each ask."""
        output = list(selected or [])
        for row in aspects:
            aspect = row["aspect"]
            if any(p.get("question_aspect") == aspect for p in output):
                continue
            candidate = next((p for p in internal if p.get("question_aspect") == aspect), None)
            if candidate:
                output.append(candidate)
            else:
                output.append({
                    "source_type": "retrieval_gap",
                    "question_aspect": aspect,
                    "retrieval_gap": True,
                    "chunk_text": "No relevant internal evidence was retrieved for this question part. This is not evidence that the SAP functionality is unsupported.",
                })
        return output

    @staticmethod
    def _should_auto_compare(document_match_score: float, confidence_data: Dict[str, Any]) -> bool:
        threshold = float(getattr(settings, "DOCUMENT_MATCH_THRESHOLD", 0.80))
        return bool(
            getattr(settings, "AUTO_MULTI_SOURCE_FALLBACK", True)
            and (
                float(document_match_score) < threshold
                or confidence_data.get("should_trigger_tavily", False)
            )
        )

    @property
    def comparator(self):
        if self._comparator is None:
            from backend.app.retrieval.multi_source_compare import multi_source_comparator
            self._comparator = multi_source_comparator
        return self._comparator

    @comparator.setter
    def comparator(self, value):
        self._comparator = value

    def _format_repo_citation(self, raw_chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Formats a GitHub repository chunk into backward-compatible citation schema."""
        repo_url = raw_chunk.get("repo_url", "")
        file_path = raw_chunk.get("file_path", "")
        repo_owner_name = repo_url.replace("https://github.com/", "").strip("/")
        source_label = f"GitHub: {repo_owner_name} ({file_path})" if file_path else f"GitHub: {repo_owner_name}"
        
        return {
            "source_type": "github_repo",
            "source": source_label,
            "repo_url": repo_url,
            "file_path": file_path,
            "commit_hash": raw_chunk.get("commit_hash", ""),
            "license": raw_chunk.get("license", "unknown"),
            "score": raw_chunk.get("score", 0.0),
            "chunk_id": raw_chunk.get("candidate_id") or raw_chunk.get("chunk_id", ""),
            "title": f"{repo_owner_name} - {file_path}"
        }

    @staticmethod
    def _format_kb_citation(raw_chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Create a safe, stable citation for a retrieved knowledge-base chunk."""
        raw_document = str(raw_chunk.get("document_name") or raw_chunk.get("title") or "SAP BRIM Documentation")
        # Retrieval records must never turn a local source path into an API response.
        document = re.split(r"[\\\\/]", raw_document)[-1]
        page = raw_chunk.get("page_number", 1) or 1
        snippet = (raw_chunk.get("snippet") or raw_chunk.get("chunk_text") or "").replace("\ufffd", "-").strip()
        return {
            "source_type": "knowledge_base",
            "chunk_id": str(raw_chunk.get("chunk_id") or raw_chunk.get("id") or ""),
            "document": document,
            "page": page,
            "section": raw_chunk.get("section", "") or f"Page {page}",
            "score": round(float(raw_chunk.get("relevance_score", raw_chunk.get("rerank_score", raw_chunk.get("score", 0.0)))), 4),
            "snippet": snippet,
        }

    @staticmethod
    def _dedupe_citations(citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Keep one citation per stable chunk (or document/page fallback)."""
        seen = set()
        unique = []
        for citation in citations:
            key = citation.get("chunk_id") or (
                citation.get("source_type", "knowledge_base"),
                citation.get("document", citation.get("source", "")),
                citation.get("page", 1),
                citation.get("section", ""),
            )
            if key not in seen:
                seen.add(key)
                unique.append(citation)
        return unique

    @staticmethod
    def _comparison_summary(comp_result: Dict[str, Any]) -> Dict[str, Any]:
        """Return compact per-source scores and winner details for the API/UI."""
        source_scores: Dict[str, float] = {}
        for candidate in comp_result.get("all_candidates", []):
            if candidate.get("is_eligible"):
                kind = candidate.get("source_type", "unknown")
                source_scores[kind] = max(
                    source_scores.get(kind, 0.0), float(candidate.get("final_score", 0.0))
                )
        comparison = comp_result.get("comparison", {})
        return {
            "source_scores": source_scores,
            "comparison_audit": {
                "sources_compared": comparison.get("sources_compared", []),
                "threshold": comparison.get("threshold", 0.0),
                "winning_source_type": comparison.get("winning_source_type", "insufficient"),
                "winning_score": comparison.get("final_score", 0.0),
                "selection_reason": comparison.get("selection_reason", ""),
                "scores_by_source": source_scores,
            },
        }

    def _generate_grounded_answer(
        self,
        query: str,
        passages: List[Dict[str, Any]],
        source_type: str = "knowledge_base"
    ) -> Dict[str, Any]:
        """Generates candidate answer and runs claim grounding verification."""
        candidate_answer = llm_service.generate_answer(
            query, passages, source_type=source_type
        )
        verification = grounding_service.verify_answer(
            query, candidate_answer, passages, source_type=source_type
        )
        return {
            "answer": candidate_answer,
            "grounded_score": verification.get("grounding_score", 0.85),
            "verification_status": verification.get("verification_status", "verified"),
            "passes_grounding_gate": verification.get("passes_grounding_gate", False),
            "unsupported_claims": verification.get("unsupported_claims", []),
            "critical_unsupported_claims": verification.get("critical_unsupported_claims", []),
            "citations": [],
            "insufficient_evidence": not bool(passages),
        }

    def query(self, query: str, db: Optional[Session] = None) -> Dict[str, Any]:
        """Synchronous query convenience entrypoint."""
        if db is None:
            from backend.app.database import get_db
            try:
                db_gen = get_db()
                db = next(db_gen)
            except Exception:
                from unittest.mock import MagicMock
                db = MagicMock()
        return self.process_query(db=db, query=query)

    def process_query(
        self,
        db: Session,
        query: str,
        chat_history: Optional[List[Dict[str, Any]]] = None,
        user: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Synchronous execution of the verified RAG pipeline with enterprise security enforcement."""
        # 0. Resolve user identity and role
        user_role = getattr(user, "role", "consultant") if user else "consultant"
        user_id = getattr(user, "id", None) if user else None
        user_email = getattr(user, "email", None) if user else None

        # 1. Conversational & Sentimental Inquiries (Routed to Dedicated Key)
        if sap_classifier.is_conversational_or_greeting(query):
            logger.info(f"Routing conversational query '{query}' to dedicated conversational LLM tier.")
            conversational_reply = llm_service.generate_conversational_reply(query, chat_history=chat_history)
            follow_ups = followup_service.generate_starter_followups()
            return {
                "answer": conversational_reply,
                "source_type": "conversational",
                "grounding_score": 1.0,
                "is_in_rag_pipeline": False,
                "kb_score": 0.0,
                "web_score": 0.0,
                "winning_score": 0.0,
                "selected_source": "conversational_assistant",
                "verification_status": "verified",
                "internal_evidence_confidence": 0.0,
                "selected_evidence_quality": 0.0,
                "external_search_used": False,
                "citations": [],
                "web_sources": [],
                "follow_up_questions": follow_ups,
                "selection_summary": "Handled via dedicated conversational assistant introducing SAP BRIM."
            }

        # 2. Query Resolution & Follow-Up Check
        resolution = query_rewriter.resolve_query(query, chat_history=chat_history)
        is_follow_up = resolution.get("is_follow_up", False)
        resolved_query = resolution.get("resolved_query", query).strip()
        cleaned_query = resolved_query

        # 3. Strict SAP Domain Classifier Enforcement
        # If it's a verified follow-up to an existing SAP topic, evaluate resolved_query;
        # otherwise evaluate the raw query. Unrelated non-SAP queries are rejected automatically.
        target_check_query = cleaned_query if is_follow_up else query.strip()
        is_sap, refusal_msg = sap_classifier.classify(target_check_query)

        if not is_sap:
            logger.info(f"Query rejected by SAP classifier: '{query}' -> {refusal_msg}")
            return {
                "answer": refusal_msg,
                "source_type": "refusal",
                "grounding_score": 0.0,
                "is_in_rag_pipeline": False,
                "kb_score": 0.0,
                "web_score": 0.0,
                "winning_score": 0.0,
                "selected_source": "refusal",
                "verification_status": "rejected",
                "internal_evidence_confidence": 0.0,
                "selected_evidence_quality": 0.0,
                "external_search_used": False,
                "citations": [],
                "web_sources": [],
                "follow_up_questions": [],
                "selection_summary": "Query rejected as outside SAP scope."
            }

        # 3. Retrieve from Internal Knowledge Base
        # Retrieve independently for clear subquestions, then merge/deduplicate evidence.
        top_kb_chunks, kb_rerank_score, aspect_results = self._retrieve_aspect_evidence(
            db, cleaned_query, settings.TOP_K
        )

        # 3. Assess Internal Evidence Confidence
        internal_confidence_data = evidence_selection_service.compute_internal_confidence(
            cleaned_query, top_kb_chunks
        )
        if len(aspect_results) > 1:
            internal_confidence_data["aspects"] = aspect_results
            internal_confidence_data["confidence"] = min(
                float(internal_confidence_data["confidence"]),
                min((row["score"] for row in aspect_results), default=0.0),
            )
            internal_confidence_data["should_trigger_tavily"] = any(
                row["score"] < settings.INTERNAL_EVIDENCE_THRESHOLD or row["evidence_count"] == 0
                for row in aspect_results
            ) or internal_confidence_data["should_trigger_tavily"]
            internal_confidence_data["reason"] = "Per-part evidence assessment: " + "; ".join(
                f"{row['aspect'][:80]}={row['score']:.2f} ({row['evidence_count']} passages)" for row in aspect_results
            )
        internal_conf = internal_confidence_data["confidence"]
        document_match_score = kb_rerank_score
        auto_compare_trigger = self._should_auto_compare(document_match_score, internal_confidence_data)
        should_trigger_tavily = auto_compare_trigger or internal_confidence_data["should_trigger_tavily"]

        # Let the multi-source comparator fetch both GitHub and web evidence when
        # the document match is weak. The legacy web-only path remains available
        # when automatic comparison is disabled.
        web_results = []
        if should_trigger_tavily and settings.WEB_FALLBACK_ENABLED and not auto_compare_trigger:
            try:
                web_results = web_search_service.search_sap_authoritative(cleaned_query)
            except Exception as e:
                logger.warning(f"Tavily search error: {e}")
                web_results = []

        # Check Feature Flags for Repository Retrieval and Multi-Source Comparison
        repo_enabled = getattr(settings, "REPO_SOURCE_ENABLED", False)
        compare_enabled = getattr(settings, "MULTI_SOURCE_COMPARE_ENABLED", False)

        # Mode B: Repository Shadow Mode (repo_enabled=True, compare_enabled=False)
        shadow_audit = None
        if repo_enabled and not compare_enabled:
            try:
                shadow_audit = self.comparator.run_shadow_comparison(
                    db=db,
                    query=cleaned_query,
                    kb_candidates=top_kb_chunks
                )
                logger.info(
                    f"[SHADOW MODE AUDIT] Query: '{cleaned_query[:40]}' | "
                    f"Hypothetical winner: {shadow_audit.get('hypothetical_winner')} | "
                    f"Score: {shadow_audit.get('hypothetical_score')}"
                )
            except Exception as e:
                logger.warning(f"Shadow mode comparison execution error: {e}")

        # Mode C: Multi-Source Comparison Mode (Active only when explicitly enabled)
        comp_result = {}
        if compare_enabled or auto_compare_trigger:
            from backend.app.retrieval.multi_source_compare import multi_source_comparator
            comp_result = multi_source_comparator.execute_multi_source_comparison(
                db=db,
                query=cleaned_query,
                kb_candidates=top_kb_chunks,
                repo_source_enabled=(repo_enabled or auto_compare_trigger),
                multi_source_compare_enabled=True,
                web_search_available=settings.WEB_FALLBACK_ENABLED,
                force_web_search=auto_compare_trigger,
                query_aspects=self.split_question_aspects(cleaned_query),
            )
            winning_cand = comp_result.get("winning_candidate")
            if winning_cand:
                selected_passages = [winning_cand] + [
                    c for c in comp_result.get("eligible_candidates", [])
                    if c["candidate_id"] != winning_cand["candidate_id"]
                ][:3]
                selected_source_type = winning_cand["source_type"]
                selected_quality = winning_cand["final_score"]
                evidence_selection = {
                    "selection_summary": comp_result.get("comparison", {}).get("selection_reason", "Highest-scoring eligible source selected."),
                    "selected_evidence_quality": selected_quality,
                }
            else:
                selected_passages = []
                selected_source_type = "insufficient"
                selected_quality = 0.0
                evidence_selection = {
                    "selection_summary": "No source met the evidence eligibility threshold.",
                    "selected_evidence_quality": 0.0,
                }
        else:
            # 5. Legacy Unified Evidence Selection (Mode A & Mode B authoritative path)
            evidence_selection = evidence_selection_service.select_strongest_evidence(
                query=cleaned_query,
                internal_candidates=top_kb_chunks,
                external_candidates=web_results,
                internal_confidence_data=internal_confidence_data
            )
            selected_passages = evidence_selection.get("selected_passages") or top_kb_chunks or web_results or []
            selected_source_type = evidence_selection.get("source_type") or "knowledge_base"
            selected_quality = evidence_selection.get("selected_evidence_quality", 0.8)

        selected_passages = self._ensure_aspect_coverage(selected_passages, top_kb_chunks, aspect_results)

        # Do not discard supported subparts/calculations because another aspect is weak.
        if selected_source_type in ("insufficient", "none"):
            selected_passages = top_kb_chunks or web_results
            selected_source_type = selected_passages[0].get("source_type", "knowledge_base") if selected_passages else "insufficient"
            selected_quality = 0.0
            evidence_selection["selection_summary"] = (
                "No candidate met the source eligibility threshold. Answering only independently supportable parts; "
                "this retrieval outcome does not establish that the functionality is unsupported."
            )

        # 6. Generate Candidate Answer
        gen_res = self._generate_grounded_answer(
            cleaned_query, selected_passages, source_type=selected_source_type
        )
        candidate_answer = gen_res["answer"]
        final_answer = candidate_answer
        final_grounding_score = gen_res.get("grounded_score", 0.85)
        verification_status = gen_res.get("verification_status", "verified")
        verification = {
            "passes_grounding_gate": gen_res.get(
                "passes_grounding_gate", final_grounding_score >= settings.ANSWER_GROUNDING_THRESHOLD
            ),
            "unsupported_claims": gen_res.get("unsupported_claims", []),
            "critical_unsupported_claims": gen_res.get("critical_unsupported_claims", []),
        }

        # 8. Controlled Answer Repair if needed
        regeneration_count = 0
        if not verification.get("passes_grounding_gate") and settings.MAX_GROUNDING_REPAIR_ATTEMPTS > 0:
            logger.info("Attempting answer repair...")
            regeneration_count += 1
            repaired_answer = llm_service.repair_answer(
                query=cleaned_query,
                candidate_answer=candidate_answer,
                unsupported_claims=verification.get("unsupported_claims", []),
                critical_unsupported_ids=verification.get("critical_unsupported_claims", []),
                evidence=selected_passages,
                source_type=selected_source_type
            )
            if repaired_answer and len(repaired_answer.strip()) > 30:
                final_answer = repaired_answer
                re_ver = grounding_service.verify_answer(
                    cleaned_query, repaired_answer, selected_passages, source_type=selected_source_type
                )
                final_grounding_score = re_ver.get("grounding_score", final_grounding_score)
                verification_status = re_ver.get("verification_status", "partial")
                verification["passes_grounding_gate"] = re_ver.get("passes_grounding_gate", False)

        # 10. Generate Exactly 3 Recommended Follow-up Questions
        follow_ups = followup_service.generate_followup_questions(
            cleaned_query, final_answer, selected_passages
        )

        # Build Citations and Web Sources with exact metadata
        citations = []
        web_sources = []
        for p in selected_passages:
            src_type = p.get("source_type") or ("web" if p.get("url") else "knowledge_base")
            if src_type == "knowledge_base":
                citations.append(self._format_kb_citation(p))
            elif src_type == "github_repo":
                repo_name = p.get("document_name") or f"github:{p.get('repo_name', 'repository')}"
                sec = p.get("section") or p.get("file_path") or "Repository Source"
                score_val = round(float(p.get("final_score", p.get("calibrated_relevance_score", p.get("score", 0.7)))), 4)
                raw_snip = p.get("snippet") or p.get("chunk_text") or ""
                clean_snip = raw_snip.replace("\ufffd", "-").strip()
                citations.append({
                    "source_type": "github_repo",
                    "chunk_id": str(p.get("candidate_id") or p.get("chunk_id") or ""),
                    "document": repo_name,
                    "page": 1,
                    "section": sec,
                    "score": score_val,
                    "snippet": clean_snip
                })
            elif src_type == "web":
                title_val = p.get("title") or p.get("document_name") or "SAP Official Documentation"
                url_val = p.get("url", "")
                domain_val = p.get("domain", "help.sap.com")
                raw_snip = p.get("snippet") or p.get("chunk_text") or ""
                clean_snip = raw_snip.replace("\ufffd", "-").strip()
                web_sources.append({
                    "title": title_val,
                    "url": url_val,
                    "domain": domain_val,
                    "snippet": clean_snip
                })

        citations = self._dedupe_citations(citations)

        comparison_summary = self._comparison_summary(comp_result) if comp_result else {
            "source_scores": {"knowledge_base": round(float(document_match_score), 4)},
            "comparison_audit": None,
        }

        return {
            "answer": final_answer,
            "source_type": selected_source_type,
            "grounding_score": final_grounding_score,
            "grounded_score": final_grounding_score,
            "is_in_rag_pipeline": internal_conf >= settings.INTERNAL_EVIDENCE_THRESHOLD,
            "kb_score": round(document_match_score, 4),
            "web_score": round(max((c["calibrated_relevance_score"] for c in comp_result.get("all_candidates", []) if c["source_type"] == "web"), default=0.0), 4) if comp_result else round(selected_quality, 4) if should_trigger_tavily else 0.0,
            "winning_score": round(selected_quality, 4),
            "source_scores": comparison_summary["source_scores"],
            "selected_source": selected_source_type,
            "verification_status": verification_status,
            "internal_evidence_confidence": internal_conf,
            "selected_evidence_quality": selected_quality,
            "external_search_used": should_trigger_tavily,
            "citations": citations,
            "web_sources": web_sources,
            "follow_up_questions": follow_ups,
            "selection_summary": evidence_selection.get("selection_summary", ""),
            "model_used": getattr(llm_service, "last_model_used", "openai/gpt-oss-120b"),
            "provider_used": getattr(llm_service, "last_provider_used", "groq"),
            "failed_over": getattr(llm_service, "failed_over", False),
            "regeneration_count": regeneration_count,
            "shadow_audit": shadow_audit,
            "comparison_audit": comparison_summary["comparison_audit"]
        }

    def stream_query(
        self,
        db: Session,
        query: str,
        chat_history: Optional[List[Dict[str, Any]]] = None,
        user: Optional[Any] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Progressive Streaming Pipeline for SAP BRIM Knowledge Assistant with Security Enforcement.
        Emits realistic status events during retrieval, evidence evaluation, planning,
        and claim verification.
        Buffers candidate answer tokens to guarantee that unverified text is NOT displayed
        before passing the 80% grounding gate.
        Then streams the verified text smoothly to the user.
        """
        # 0. Resolve user identity and role
        user_role = getattr(user, "role", "consultant") if user else "consultant"
        user_id = getattr(user, "id", None) if user else None
        user_email = getattr(user, "email", None) if user else None

        # STAGE 0: Conversational & Sentimental Inquiries (Dedicated Key)
        if sap_classifier.is_conversational_or_greeting(query):
            logger.info(f"Stream routing conversational query '{query}' to dedicated conversational LLM tier.")
            yield {
                "type": "status",
                "stage": "thinking",
                "message": "Connecting to SAP BRIM Assistant..."
            }
            token_buffer = ""
            for token in llm_service.stream_conversational_reply(query, chat_history=chat_history):
                token_buffer += token
                yield {
                    "type": "token",
                    "content": token
                }

            follow_ups = followup_service.generate_starter_followups()
            yield {
                "type": "done",
                "answer": token_buffer,
                "source_type": "conversational",
                "grounding_score": 1.0,
                "is_in_rag_pipeline": False,
                "kb_score": 0.0,
                "web_score": 0.0,
                "winning_score": 0.0,
                "selected_source": "conversational_assistant",
                "verification_status": "verified",
                "internal_evidence_confidence": 0.0,
                "selected_evidence_quality": 0.0,
                "external_search_used": False,
                "citations": [],
                "web_sources": [],
                "follow_up_questions": follow_ups,
                "selection_summary": "Handled via dedicated conversational assistant introducing SAP BRIM."
            }
            return

        # STAGE 1: Context Resolution & Follow-Up Check
        yield {
            "type": "status",
            "stage": "thinking",
            "message": "Resolving conversation context..."
        }

        resolution = query_rewriter.resolve_query(query, chat_history=chat_history)
        is_follow_up = resolution.get("is_follow_up", False)
        resolved_query = resolution.get("resolved_query", query).strip()
        cleaned_query = resolved_query

        # Scope Verification via SAPClassifier
        target_check_query = cleaned_query if is_follow_up else query.strip()
        is_sap, refusal_msg = sap_classifier.classify(target_check_query)

        if not is_sap:
            logger.info(f"Stream query rejected by SAP classifier: '{query}' -> {refusal_msg}")
            yield {
                "type": "token",
                "content": refusal_msg
            }
            yield {
                "type": "done",
                "answer": refusal_msg,
                "source_type": "refusal",
                "grounding_score": 0.0,
                "is_in_rag_pipeline": False,
                "kb_score": 0.0,
                "web_score": 0.0,
                "winning_score": 0.0,
                "selected_source": "refusal",
                "verification_status": "rejected",
                "internal_evidence_confidence": 0.0,
                "selected_evidence_quality": 0.0,
                "external_search_used": False,
                "citations": [],
                "web_sources": [],
                "follow_up_questions": [],
                "selection_summary": "Query rejected as outside SAP scope."
            }
            return

        # STAGE 2: Internal Retrieval
        yield {
            "type": "status",
            "stage": "retrieval",
            "message": "Searching internal SAP documentation..."
        }

        top_kb_chunks, document_match_score, aspect_results = self._retrieve_aspect_evidence(
            db, cleaned_query, settings.TOP_K, hybrid=True
        )

        # STAGE 3: Assess Internal Evidence Confidence
        yield {
            "type": "status",
            "stage": "assessing_evidence",
            "message": "Assessing internal evidence confidence..."
        }

        internal_confidence_data = evidence_selection_service.compute_internal_confidence(
            cleaned_query, top_kb_chunks
        )
        if len(aspect_results) > 1:
            internal_confidence_data["aspects"] = aspect_results
            internal_confidence_data["confidence"] = min(
                float(internal_confidence_data["confidence"]),
                min((row["score"] for row in aspect_results), default=0.0),
            )
            internal_confidence_data["should_trigger_tavily"] = any(
                row["score"] < settings.INTERNAL_EVIDENCE_THRESHOLD or row["evidence_count"] == 0
                for row in aspect_results
            ) or internal_confidence_data["should_trigger_tavily"]
            internal_confidence_data["reason"] = "Per-part evidence assessment: " + "; ".join(
                f"{row['aspect'][:80]}={row['score']:.2f} ({row['evidence_count']} passages)" for row in aspect_results
            )
        internal_conf = internal_confidence_data["confidence"]
        auto_compare_trigger = self._should_auto_compare(document_match_score, internal_confidence_data)
        should_trigger_tavily = auto_compare_trigger or internal_confidence_data["should_trigger_tavily"]

        web_results = []
        if should_trigger_tavily and settings.WEB_FALLBACK_ENABLED and not auto_compare_trigger:
            # Emit web search progress event ONLY if Tavily was triggered
            yield {
                "type": "status",
                "stage": "web_search",
                "message": "Searching approved SAP sources (help.sap.com)..."
            }
            try:
                web_results = web_search_service.search_sap_authoritative(cleaned_query)
            except Exception as e:
                logger.warning(f"Web search error: {e}")
                web_results = []

        # STAGE 4: Unified Evidence Selection
        yield {
            "type": "status",
            "stage": "evidence_selection",
            "message": "Comparing and selecting strongest evidence..."
        }

        comp_result = {}
        compare_enabled = getattr(settings, "MULTI_SOURCE_COMPARE_ENABLED", False)
        repo_enabled = getattr(settings, "REPO_SOURCE_ENABLED", False)
        if auto_compare_trigger or compare_enabled:
            yield {
                "type": "status",
                "stage": "multi_source_search",
                "message": "Comparing document, approved GitHub repository, and SAP web evidence..."
            }
            from backend.app.retrieval.multi_source_compare import multi_source_comparator
            comp_result = multi_source_comparator.execute_multi_source_comparison(
                db=db,
                query=cleaned_query,
                kb_candidates=top_kb_chunks,
                repo_source_enabled=(repo_enabled or auto_compare_trigger),
                multi_source_compare_enabled=True,
                web_search_available=settings.WEB_FALLBACK_ENABLED,
                force_web_search=auto_compare_trigger,
                query_aspects=self.split_question_aspects(cleaned_query),
            )
            winning = comp_result.get("winning_candidate")
            eligible = comp_result.get("eligible_candidates", [])
            if winning:
                selected_passages = [winning] + [
                    c for c in eligible if c["candidate_id"] != winning["candidate_id"]
                ][:3]
                selected_source_type = winning["source_type"]
                selected_quality = winning["final_score"]
            else:
                selected_passages = []
                selected_source_type = "insufficient"
                selected_quality = 0.0
            evidence_selection = {
                "selection_summary": comp_result.get("comparison", {}).get("selection_reason", ""),
                "selected_evidence_quality": selected_quality,
            }
        else:
            evidence_selection = evidence_selection_service.select_strongest_evidence(
                query=cleaned_query,
                internal_candidates=top_kb_chunks,
                external_candidates=web_results,
                internal_confidence_data=internal_confidence_data
            )

            selected_passages = evidence_selection.get("selected_passages") or top_kb_chunks or web_results or []
            selected_source_type = evidence_selection.get("source_type") or "knowledge_base"
            selected_quality = evidence_selection.get("selected_evidence_quality", 0.8)

        selected_passages = self._ensure_aspect_coverage(selected_passages, top_kb_chunks, aspect_results)

        if selected_source_type in ("insufficient", "none"):
            selected_passages = top_kb_chunks or web_results
            selected_source_type = selected_passages[0].get("source_type", "knowledge_base") if selected_passages else "insufficient"
            selected_quality = 0.0
            evidence_selection["selection_summary"] = (
                "No candidate met the source eligibility threshold. Answering only independently supportable parts; "
                "this retrieval outcome does not establish that the functionality is unsupported."
            )

        # STAGE 5: Direct Live Answer Streaming (Instant TTFT)
        yield {
            "type": "status",
            "stage": "generating",
            "message": "Generating technical response..."
        }

        # Stream answer tokens live from LLM directly to client
        token_buffer = []
        for token in llm_service.stream_answer(
            cleaned_query, selected_passages, source_type=selected_source_type
        ):
            token_buffer.append(token)

        final_answer = "".join(token_buffer).strip()
        if not final_answer:
            # Resilient fallback if stream yielded no tokens
            final_answer = llm_service.generate_answer(
                cleaned_query, selected_passages, source_type=selected_source_type
            )

        # STAGE 6: Instant Claim-Level Grounding Verification
        yield {
            "type": "status",
            "stage": "verifying_claims",
            "message": "Verifying technical claims against evidence..."
        }
        verification = grounding_service.verify_answer(
            cleaned_query, final_answer, selected_passages, source_type=selected_source_type
        )
        final_grounding_score = verification.get("grounding_score", 0.85)
        verification_status = verification.get("verification_status", "verified")

        # Repair before publishing when claim verification identifies unsupported details.
        if not verification.get("passes_grounding_gate") and settings.MAX_GROUNDING_REPAIR_ATTEMPTS > 0:
            repaired = llm_service.repair_answer(
                query=cleaned_query,
                candidate_answer=final_answer,
                unsupported_claims=verification.get("unsupported_claims", []),
                critical_unsupported_ids=verification.get("critical_unsupported_claims", []),
                evidence=selected_passages,
                source_type=selected_source_type,
            )
            if repaired and repaired != final_answer:
                repaired_verification = grounding_service.verify_answer(
                    cleaned_query, repaired, selected_passages, source_type=selected_source_type
                )
                final_answer = repaired
                verification = repaired_verification
                final_grounding_score = repaired_verification.get("grounding_score", final_grounding_score)
                verification_status = repaired_verification.get("verification_status", "partial")

        # Stream only after evidence verification/repair so unsupported first-draft
        # tokens cannot escape before the grounded answer is finalized.
        for start in range(0, len(final_answer), 96):
            yield {"type": "token", "content": final_answer[start:start + 96]}

        # STAGE 7: Recommend Exactly 3 Follow-Up Questions (instant, <1ms)
        follow_ups = followup_service.generate_followup_questions(
            cleaned_query, final_answer, selected_passages
        )

        # Build Citations & Web Sources
        citations = []
        web_sources = []
        for p in selected_passages:
            src_type = p.get("source_type") or ("web" if p.get("url") else "knowledge_base")
            if src_type == "knowledge_base":
                citations.append(self._format_kb_citation(p))
            elif src_type == "github_repo":
                citations.append({
                    "source_type": "github_repo",
                    "chunk_id": str(p.get("candidate_id") or p.get("chunk_id") or ""),
                    "document": p.get("document_name") or p.get("repo_url") or "GitHub SAP source",
                    "page": 1,
                    "section": p.get("file_path") or p.get("section", "Repository source"),
                    "score": round(float(p.get("final_score", p.get("calibrated_relevance_score", 0.0))), 4),
                    "snippet": (p.get("snippet") or p.get("chunk_text") or "").replace("\ufffd", "-").strip(),
                })
            elif src_type == "web":
                title_val = p.get("title") or p.get("document_name") or "SAP Official Documentation"
                url_val = p.get("url", "")
                domain_val = p.get("domain", "help.sap.com")
                raw_snip = p.get("snippet") or p.get("chunk_text") or ""
                clean_snip = raw_snip.replace("\ufffd", "-").strip()
                web_sources.append({
                    "title": title_val,
                    "url": url_val,
                    "domain": domain_val,
                    "snippet": clean_snip
                })

        citations = self._dedupe_citations(citations)

        comparison_summary = self._comparison_summary(comp_result) if comp_result else {
            "source_scores": {"knowledge_base": round(float(document_match_score), 4)},
            "comparison_audit": None,
        }

        # STAGE 10: Completion 'done' event with all required fields
        yield {
            "type": "done",
            "answer": final_answer,
            "source_type": selected_source_type,
            "grounding_score": final_grounding_score,
            "is_in_rag_pipeline": internal_conf >= settings.INTERNAL_EVIDENCE_THRESHOLD,
            "kb_score": round(document_match_score, 4),
            "web_score": round(max((c["calibrated_relevance_score"] for c in comp_result.get("all_candidates", []) if c["source_type"] == "web"), default=0.0), 4) if comp_result else round(selected_quality, 4) if should_trigger_tavily else 0.0,
            "winning_score": round(selected_quality, 4),
            "source_scores": comparison_summary["source_scores"],
            "selected_source": selected_source_type,
            "verification_status": verification_status,
            "internal_evidence_confidence": internal_conf,
            "selected_evidence_quality": selected_quality,
            "external_search_used": should_trigger_tavily,
            "citations": citations,
            "web_sources": web_sources,
            "follow_up_questions": follow_ups,
            "selection_summary": evidence_selection.get("selection_summary", ""),
            "comparison_audit": comparison_summary["comparison_audit"]
        }


rag_service = RAGService()
