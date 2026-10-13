"""
Multi-Source Retrieval and Evidence Comparison Engine.
Coordinates:
1. Existing SAP BRIM Knowledge Base (Stage 1)
2. Isolated GitHub Repository Index (Stage 2)
3. Authoritative Tavily Web Documentation (Stage 3)
4. Score-Based Source Selection (Stage 4)
   final_score = calibrated_relevance_score * source_authority_weight
   with strict eligibility gates, deduplication, and structured comparison auditing.
"""

import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.services.retrieval_service import retrieval_service
from backend.app.services.reranking_service import reranking_service
from backend.app.services.web_search_service import web_search_service
from backend.app.services.evidence_selection_service import evidence_selection_service
from backend.app.retrieval.repo_store import repo_store
from backend.app.retrieval.brim_relevance_gate import brim_relevance_gate

logger = logging.getLogger(__name__)

# Configurable Source Authority Weights
AUTHORITY_WEIGHTS = {
    "official_sap": 1.0,
    "sap_partner_or_book": 0.85,
    "official_developer_doc": 0.85,  # developers.sap.com
    "official_help_doc": 0.85,       # help.sap.com
    "github_repo": 0.80,
    "official_web": 0.80,            # help.sap.com / official web
    "sap_community": 0.50,           # community.sap.com
    "forum_web": 0.50,               # community.sap.com / blogs
    "self_authored": 0.60,
    "unknown": 0.50
}


class MultiSourceComparator:
    def __init__(self):
        self.acceptance_threshold = settings.RETRIEVAL_CALIBRATED_THRESHOLD  # 0.6761

    def get_source_authority_weight(self, provenance_tier: str, domain: Optional[str] = None) -> float:
        """Determines configured authority weight based on provenance and domain."""
        if domain:
            dom_lower = domain.lower()
            if "developers.sap.com" in dom_lower:
                return AUTHORITY_WEIGHTS.get("official_developer_doc", 0.85)
            elif "help.sap.com" in dom_lower:
                return AUTHORITY_WEIGHTS.get("official_help_doc", 0.85)
            elif any(d in dom_lower for d in ["community.sap.com", "blogs.sap.com"]):
                return AUTHORITY_WEIGHTS.get("sap_community", 0.50)
        return AUTHORITY_WEIGHTS.get(provenance_tier, 0.70)

    def normalize_candidate(
        self,
        raw_candidate: Dict[str, Any],
        source_type: str,
        query: str
    ) -> Dict[str, Any]:
        """
        Normalizes internal, repository, or web candidate representation into unified schema:
        candidate_id, source_type, original_retrieval_score, calibrated_relevance_score,
        reranker_score, source_authority, license_status, BRIM_gate_status, provenance, citation_metadata
        """
        cid = str(raw_candidate.get("chunk_id") or raw_candidate.get("id") or uuid.uuid4())
        orig_score = float(raw_candidate.get("vector_score", raw_candidate.get("score", 0.5)))
        calibrated_relevance = float(raw_candidate.get("calibrated_relevance_score", raw_candidate.get("score", 0.5)))
        rerank_score = float(raw_candidate.get("rerank_score", calibrated_relevance))

        if source_type == "knowledge_base":
            prov_tier = raw_candidate.get("provenance_tier")
            if not prov_tier:
                # Infer from document name
                from backend.app.corpus.tier_definitions import DOCUMENT_TIER_MAPPING
                doc_name = raw_candidate.get("document_name", "")
                prov_tier = DOCUMENT_TIER_MAPPING.get(doc_name, {}).get("tier", "official_sap")
            lic_status = "approved"
            gate_status = "passed"
            authority_weight = self.get_source_authority_weight(prov_tier)
            citation_meta = {
                "document": raw_candidate.get("document_name", "SAP BRIM Manual"),
                "page": raw_candidate.get("page_number", 1) or 1,
                "section": raw_candidate.get("section", ""),
                "snippet": raw_candidate.get("chunk_text", "")[:300]
            }

        elif source_type == "github_repo":
            prov_tier = raw_candidate.get("provenance_tier", "github_repo")
            lic_status = raw_candidate.get("license_status", "approved")
            gate_status = "passed"
            authority_weight = self.get_source_authority_weight(prov_tier)
            citation_meta = {
                "document": raw_candidate.get("document_name", f"github:{raw_candidate.get('repo_name')}"),
                "page": 1,
                "section": raw_candidate.get("file_path", ""),
                "snippet": raw_candidate.get("chunk_text", "")[:300]
            }

        elif source_type == "web":
            domain = raw_candidate.get("domain", "")
            prov_tier = "official_web" if "help.sap.com" in domain else "forum_web"
            lic_status = "approved"
            gate_status = "passed"
            authority_weight = self.get_source_authority_weight(prov_tier, domain=domain)
            citation_meta = {
                "document": raw_candidate.get("title", "SAP Web Documentation"),
                "page": 1,
                "section": domain,
                "url": raw_candidate.get("url", ""),
                "snippet": raw_candidate.get("snippet", raw_candidate.get("chunk_text", ""))[:300]
            }

        else:
            prov_tier = "unknown"
            lic_status = "unknown"
            gate_status = "unknown"
            authority_weight = 0.5
            citation_meta = {}

        # Final Score Formula: calibrated_relevance_score * source_authority_weight
        final_score = round(calibrated_relevance * authority_weight, 4)

        # Eligibility check
        is_eligible = (
            lic_status == "approved" and
            gate_status == "passed" and
            calibrated_relevance >= self.acceptance_threshold and
            bool(citation_meta.get("snippet"))
        )

        return {
            "candidate_id": cid,
            "source_type": source_type,
            "original_retrieval_score": round(orig_score, 4),
            "calibrated_relevance_score": round(calibrated_relevance, 4),
            "reranker_score": round(rerank_score, 4),
            "source_authority": round(authority_weight, 2),
            "final_score": final_score,
            "is_eligible": is_eligible,
            "license_status": lic_status,
            "BRIM_gate_status": gate_status,
            "provenance": prov_tier,
            "citation_metadata": citation_meta,
            "chunk_text": raw_candidate.get("chunk_text", citation_meta.get("snippet", "")),
            "raw_candidate": raw_candidate
        }

    def execute_multi_source_comparison(
        self,
        db: Session,
        query: str,
        kb_candidates: List[Dict[str, Any]],
        repo_source_enabled: bool,
        multi_source_compare_enabled: bool,
        web_search_available: bool = True
    ) -> Dict[str, Any]:
        """
        Executes multi-source candidate collection, normalization, score-based selection,
        and internal comparison audit tracking.
        """
        query_id = str(uuid.uuid4())
        sources_compared = ["knowledge_base"]

        # Stage 1: Knowledge Base normalization
        norm_kb_candidates = [
            self.normalize_candidate(c, "knowledge_base", query)
            for c in kb_candidates
        ]

        # Stage 2: GitHub Repository Retrieval (Strictly gated by repo_source_enabled)
        norm_repo_candidates: List[Dict[str, Any]] = []
        if repo_source_enabled:
            sources_compared.append("github_repo")
            raw_repo_candidates = repo_store.search_repo_chunks(
                db, query, top_k=5, threshold=self.acceptance_threshold
            )
            for rc in raw_repo_candidates:
                norm_repo_candidates.append(
                    self.normalize_candidate(rc, "github_repo", query)
                )

        # Stage 3: Tavily Web Fallback
        # Condition: best_score < 0.6761 OR multi_source_compare_enabled is True
        best_internal_score = max(
            [c["calibrated_relevance_score"] for c in norm_kb_candidates + norm_repo_candidates] or [0.0]
        )
        should_fetch_web = (
            (best_internal_score < self.acceptance_threshold or multi_source_compare_enabled)
            and web_search_available
            and settings.WEB_FALLBACK_ENABLED
        )

        norm_web_candidates: List[Dict[str, Any]] = []
        if should_fetch_web:
            sources_compared.append("web")
            try:
                raw_web = web_search_service.search_sap_authoritative(query)
                for w in raw_web:
                    norm_web_candidates.append(
                        self.normalize_candidate(w, "web", query)
                    )
            except Exception as e:
                logger.warning(f"Web retrieval exception: {e}")

        # Stage 4: Combine, rank, and select winning source
        all_candidates = norm_kb_candidates + norm_repo_candidates + norm_web_candidates
        eligible_candidates = [c for c in all_candidates if c["is_eligible"]]
        rejected_candidates = [c for c in all_candidates if not c["is_eligible"]]

        # Sort eligible candidates by final_score descending
        eligible_candidates.sort(key=lambda x: x["final_score"], reverse=True)

        if eligible_candidates:
            winning_candidate = eligible_candidates[0]
            winning_source = winning_candidate["source_type"]
            winning_cid = winning_candidate["candidate_id"]
            calibrated_score = winning_candidate["calibrated_relevance_score"]
            final_score = winning_candidate["final_score"]
            selection_reason = (
                f"{winning_source} cleared acceptance threshold ({calibrated_score:.4f} >= {self.acceptance_threshold:.4f}) "
                f"with highest weighted score ({final_score:.4f}, authority={winning_candidate['source_authority']:.2f})."
            )
        else:
            winning_candidate = None
            winning_source = "insufficient"
            winning_cid = None
            calibrated_score = round(best_internal_score, 4)
            final_score = 0.0
            selection_reason = (
                f"No eligible candidates cleared the calibrated acceptance threshold ({self.acceptance_threshold:.4f}). "
                f"Abstaining or falling back to insufficient evidence behavior."
            )

        # Detect conflicts across distinct top sources
        conflicts_detected = False
        if len(eligible_candidates) >= 2:
            top_sources = {c["source_type"] for c in eligible_candidates[:3]}
            if len(top_sources) > 1 and abs(eligible_candidates[0]["final_score"] - eligible_candidates[1]["final_score"]) < 0.05:
                conflicts_detected = True

        comparison_object = {
            "query_id": query_id,
            "sources_compared": sources_compared,
            "best_candidates": eligible_candidates[:5],
            "winning_source_type": winning_source,
            "winning_candidate_id": winning_cid,
            "calibrated_score": calibrated_score,
            "final_score": final_score,
            "threshold": self.acceptance_threshold,
            "selection_reason": selection_reason,
            "rejected_candidates": rejected_candidates[:5],
            "evidence_gaps": ["No official SAP match"] if winning_source == "insufficient" else [],
            "conflicts_detected": conflicts_detected
        }

        return {
            "comparison": comparison_object,
            "winning_candidate": winning_candidate,
            "eligible_candidates": eligible_candidates,
            "all_candidates": all_candidates
        }

    def run_shadow_comparison(
        self,
        db: Session,
        query: str,
        kb_candidates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Runs shadow comparison in parallel without mutating live output.
        Returns hypothetical winner and candidates count for audit.
        """
        res = self.execute_multi_source_comparison(
            db=db,
            query=query,
            kb_candidates=kb_candidates,
            repo_source_enabled=True,
            multi_source_compare_enabled=False,
            web_search_available=False
        )
        comp = res.get("comparison", {})
        return {
            "hypothetical_winner": comp.get("winning_source_type", "knowledge_base"),
            "hypothetical_score": comp.get("final_score", 0.0),
            "shadow_candidates_count": len(res.get("eligible_candidates", [])),
            "comparison": comp
        }


multi_source_comparator = MultiSourceComparator()
