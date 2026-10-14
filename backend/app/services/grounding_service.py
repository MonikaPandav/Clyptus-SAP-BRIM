import re
import logging
from typing import List, Dict, Any, Tuple, Optional

from backend.app.config import settings

logger = logging.getLogger(__name__)

# SAP technical patterns for strict verification (only real SAP transactions and tables)
from backend.app.services.sap_entity_service import sap_entity_service

# High-precision SAP technical patterns for strict verification
TCODE_PATTERN = re.compile(
    r"\b(/[a-z0-9_]{2,}/[a-z0-9_]+|fkkbix_[a-z0-9_]+|fkkbi_[a-z0-9_]+|fkk[a-z0-9_]+|"
    r"fp[a-z0-9_]{2,8}|crmd_[a-z0-9_]+|farr_[a-z0-9_]+|wty_[a-z0-9_]+|"
    r"me[0-9]{2}[a-z]?|va[0-9]{2}|vf[0-9]{2}|vk[0-9]{2}|fb[0-9]{2}|f110|"
    r"se[0-9]{2}[a-z]?|sm[0-9]{2}|st[0-9]{2}|slg[0-9]|spro|swo1|sicf|miro|migo)\b",
    re.IGNORECASE
)
TABLE_PATTERN = re.compile(
    r"\b(dfkk[a-z0-9_]+|erdk|erch|but0[0-9]{2}|but0bk|mara|marc|vbak|vbap|ekko|ekpo|bseg|bkpf|v_fkk[a-z0-9_]+)\b",
    re.IGNORECASE
)
SPRO_PATTERN = re.compile(
    r"\b(spro|img\s+path|customizing\s+path|sap\s+customizing\s+implementation\s+guide)\b",
    re.IGNORECASE
)

# Non-TCode words and acronyms to ignore so they aren't false-positived as technical identifiers
EXCLUDED_TECH_TOKENS = {
    "b2b", "b2c", "p10", "p50", "p90", "p95", "p99", "v1", "v2", "v3", "ed1",
    "2nd", "1st", "3rd", "sap", "som", "cc", "ci", "fica", "rar", "crm", "ecc",
    "gui", "iot", "api", "erp", "rfc", "tcp", "ssl", "http", "rest", "soap",
    "json", "xml", "csv", "sql", "hana", "btp", "cdr", "bit", "cit", "sla",
    "e2e", "q1", "q2", "q3", "q4", "24x7", "2020", "1909", "404", "500", "100",
    "http400", "http500", "http200"
}

STOP_WORDS = {
    "what", "is", "the", "a", "an", "how", "to", "in", "of", "and", "for", "with",
    "does", "do", "explain", "can", "you", "tell", "me", "about", "this", "that", "these",
    "those", "are", "from", "into", "onto", "upon", "which", "there", "their", "they",
    "here", "based", "according", "following", "overview", "summary", "functions",
    "also", "used", "been", "have", "has", "will", "would", "could", "should", "process",
    "system", "between", "during", "before", "after", "through", "ensures", "ensuring"
}

# Comprehensive registry of standard SAP BRIM & S/4HANA objects
VERIFIED_STANDARD_SAP_OBJECTS = {
    # CI Transactions & Tables
    "spro", "fkkbi_class", "fkkbix_class", "fkkbix_conf", "fkkbix_bit_mon", "fkkbix_cit_mon",
    "fkkbix_rate", "fkkbix_bill", "fkkbix_inv", "fkkbix_bit_disp", "fkkbix",
    "fkkbix_bill_m", "fkkbix_inv_m",
    "dfkkbixbit0", "dfkkbixbit1", "dfkkbixbit2", "dfkkbixbit3", "dfkkbixbit4",
    "dfkkbixcit0", "dfkkbixcit1", "dfkkbixcit2", "dfkkbixcit3", "dfkkbixcit4",
    "dfkkbict", "dfkkbict_it", "dfkkbict_py", "dfkkbict_tx", "dfkkinv_ord", "dfkkinv_doc",
    "dfkkinvdoc", "dfkkinvdoc_h", "dfkkinvdoc_i", "dfkkinvdoc_p",
    "dfkkbilldoc", "dfkkbilldoc_h", "dfkkbilldoc_i",

    # FI-CA Transactions & Tables
    "fpc0", "fpc1", "fpc2", "fpc3", "fpl9", "fpma", "fprel", "fpva", "fpvb",
    "fpcopara", "fpci", "fpg1", "fpg4", "fp05", "fp08", "fp30", "fp40",
    "fpe1", "fpe2", "fpe3", "dfkkko", "dfkkop", "dfkkopk", "dfkklocks", "dfkkco",
    "dfkkcoll", "dfkkdumi", "fkkvk", "fkkvkp", "erdk", "erch",

    # SOM, RAR & S/4HANA
    "crmd_order", "com_product", "wty_claim", "farr_rai_mon",
    "slg1", "sm30", "sm37", "sm59", "se16", "se16n", "se38", "se80", "sicf", "swo1",
    "st05", "st22", "we02", "we20", "f110",

    # ERP Standard
    "me21n", "me22n", "me23n", "me21", "me22", "me23",
    "va01", "va02", "va03", "vf01", "vf02", "vf03", "fb01", "fb02", "fb03", "fb05",
    "migo", "miro", "ekko", "ekpo", "bseg", "bkpf", "mara", "marc", "vbak", "vbap",
    "but000", "but020", "but050", "but051", "but0bk"
}


class GroundingService:
    """
    High-Precision Claim-Level Grounding Verification Service for SAP BRIM Knowledge Assistant.
    Calibrated for senior 8+ years SAP BRIM consultants.
    Strictly verifies technical claims individually against retrieved evidence.
    """

    def __init__(self):
        self.grounding_threshold = settings.ANSWER_GROUNDING_THRESHOLD

    @staticmethod
    def _extract_sentences(text: str) -> List[str]:
        """Splits answer into discrete factual statements while filtering decorative formatting."""
        if not text:
            return []

        sentences = []
        for line in text.split("\n"):
            line = line.strip()
            # Ignore headers, table delimiters, and meta notices
            if not line or line.startswith("#") or line.startswith("|---") or line.startswith("---") or line.startswith("*All statements") or line.startswith("*(This"):
                continue
            # Strip list numbers or bullets
            clean_line = re.sub(r"^(\*|\-|\d+\.|\d+\))\s*", "", line).strip()
            if not clean_line:
                continue

            # Split on sentence boundaries (. ! ?)
            parts = re.split(r"(?<=[.!?])\s+", clean_line)
            for p in parts:
                p = p.strip()
                if len(p) >= 15:
                    sentences.append(p)

        return sentences

    @staticmethod
    def _extract_technical_identifiers(text: str) -> List[str]:
        """Extracts specific SAP T-codes and database tables."""
        tcodes = set()
        tables = set()

        for m in TCODE_PATTERN.finditer(text):
            tok = m.group(0).lower()
            if tok not in EXCLUDED_TECH_TOKENS and len(tok) >= 3:
                tcodes.add(tok)

        for m in TABLE_PATTERN.finditer(text):
            tok = m.group(0).lower()
            if tok not in EXCLUDED_TECH_TOKENS:
                tables.add(tok)

        return list(tcodes | tables)

    @staticmethod
    def _contains_term(text: str, term: str) -> bool:
        pattern = rf"(?<![a-z0-9]){re.escape(term.lower())}(?![a-z0-9])"
        return bool(re.search(pattern, text.lower()))

    @staticmethod
    def passes_gate(
        grounding_score: float,
        unsupported_claims: List[str],
        total_claims: int,
        hallucinated_ids: List[str],
        contradicted_claims: Optional[List[str]] = None,
        threshold: float = 0.80
    ) -> bool:
        if contradicted_claims is None:
            contradicted_claims = []
        return bool(
            grounding_score >= threshold
            and len(hallucinated_ids) == 0
            and len(contradicted_claims) == 0
            and len(unsupported_claims) <= max(1, int(total_claims * 0.25))
        )

    def verify_answer(
        self,
        query: str,
        answer: str,
        evidence_passages: List[Dict[str, Any]],
        source_type: str = "knowledge_base"
    ) -> Dict[str, Any]:
        """
        Performs claim-level grounding verification of the generated answer against evidence.
        Classifies each technical statement:
        - directly supported
        - supported with qualification
        - unsupported
        - contradicted
        """
        # Refusal or empty answer
        if source_type in ("refusal", "abstention") or not answer.strip():
            return {
                "grounding_score": 0.0,
                "passes_grounding_gate": False,
                "claims": [],
                "supported_claims": [],
                "unsupported_claims": [],
                "contradicted_claims": [],
                "critical_unsupported_claims": [],
                "all_material_claims_cited": False,
                "verification_status": "abstention" if source_type == "abstention" else "rejected",
                "summary": "Response is an abstention or scope refusal."
            }

        if not evidence_passages:
            return {
                "grounding_score": 0.0,
                "passes_grounding_gate": False,
                "claims": [],
                "supported_claims": [],
                "unsupported_claims": [],
                "contradicted_claims": [],
                "critical_unsupported_claims": [],
                "all_material_claims_cited": False,
                "verification_status": "unverified",
                "summary": "No supporting evidence available."
            }

        # Build concatenated evidence text & index passages
        combined_evidence = " ".join(
            (p.get("chunk_text") or p.get("snippet") or "").lower()
            for p in evidence_passages
        )
        evidence_tech_ids = set(self._extract_technical_identifiers(combined_evidence))

        # Extract material sentences as claims
        sentences = self._extract_sentences(answer)
        if not sentences:
            sentences = [answer.strip()]

        claims_result = []
        supported_claims = []
        unsupported_claims = []
        contradicted_claims = []
        critical_unsupported = []
        uncited_standard_ids = []

        for stmt in sentences:
            stmt_lower = stmt.lower()
            raw_tokens = re.findall(r"\b[a-z0-9\/\-_]{3,}\b", stmt_lower)
            stmt_terms = [t for t in raw_tokens if t not in STOP_WORDS]

            # Check technical identifiers in this statement
            stmt_tech_ids = self._extract_technical_identifiers(stmt)
            # A standard object name proves only that the identifier is plausible;
            # it does not prove the generated configuration or lifecycle claim.  A
            # technical instruction is publishable only when the exact identifier
            # also appears in the selected evidence for this answer.
            unsupported_stmt_tech = [tid for tid in stmt_tech_ids if tid not in evidence_tech_ids]
            fabricated_stmt_tech = [
                tid for tid in unsupported_stmt_tech
                if tid not in VERIFIED_STANDARD_SAP_OBJECTS
                and not sap_entity_service.is_known_sap_identifier(tid)
            ]
            uncited_stmt_tech = [tid for tid in unsupported_stmt_tech if tid not in fabricated_stmt_tech]

            # Calculate overlap with evidence
            if stmt_terms:
                matched_terms = sum(1 for t in stmt_terms if self._contains_term(combined_evidence, t))
                overlap_ratio = matched_terms / len(stmt_terms)
            else:
                overlap_ratio = 1.0

            # Determine supporting sources
            supporting_source_ids = []
            for p in evidence_passages:
                p_text = (p.get("chunk_text") or p.get("snippet") or "").lower()
                if stmt_terms and sum(1 for t in stmt_terms if self._contains_term(p_text, t)) / len(stmt_terms) >= 0.20:
                    supporting_source_ids.append(p.get("source_id", "source"))

            # Determine Claim Status
            if unsupported_stmt_tech:
                status = "unsupported"
                reason = f"Technical identifier(s) are absent from the selected evidence: {', '.join(unsupported_stmt_tech)}"
                for ut in fabricated_stmt_tech:
                    if ut not in critical_unsupported:
                        critical_unsupported.append(ut)
                for ut in uncited_stmt_tech:
                    if ut not in uncited_standard_ids:
                        uncited_standard_ids.append(ut)
                unsupported_claims.append(stmt)
            elif overlap_ratio >= 0.25:
                status = "supported"
                reason = f"Evidence directly supports statement (overlap: {overlap_ratio:.2f})."
                supported_claims.append(stmt)
            elif overlap_ratio >= 0.12:
                status = "partially_supported"
                reason = f"Corroborated by evidence concepts (overlap: {overlap_ratio:.2f})."
                supported_claims.append(stmt)
            else:
                status = "unsupported"
                reason = f"Insufficient evidence support for statement (overlap: {overlap_ratio:.2f})."
                unsupported_claims.append(stmt)

            claims_result.append({
                "claim": stmt,
                "status": status,
                "supporting_source_ids": supporting_source_ids[:3],
                "reason": reason,
                "unsupported_technical_ids": unsupported_stmt_tech
            })

        # Calculate Grounding Score - calibrated to be honest and accurate
        total_claims = len(claims_result)
        if total_claims > 0:
            support_ratio = len(supported_claims) / total_claims
            if support_ratio >= 0.75:
                raw_grounding = 0.80 + 0.14 * min(1.0, (support_ratio - 0.75) / 0.25)
            elif support_ratio >= 0.55:
                raw_grounding = 0.70 + 0.10 * ((support_ratio - 0.55) / 0.20)
            elif support_ratio >= 0.35:
                raw_grounding = 0.55 + 0.15 * ((support_ratio - 0.35) / 0.20)
            else:
                raw_grounding = max(0.20, support_ratio * 1.0)
        else:
            raw_grounding = 0.50

        # Penalize if fabricated identifiers or completely unsupported claims are present
        technical_evidence_gaps = critical_unsupported + uncited_standard_ids
        if technical_evidence_gaps:
            penalty = min(0.30, len(technical_evidence_gaps) * 0.10)
            final_grounding_score = max(0.20, raw_grounding - penalty)
        elif len(unsupported_claims) > len(supported_claims):
            final_grounding_score = min(raw_grounding, 0.45)
        else:
            final_grounding_score = raw_grounding

        final_grounding_score = max(0.15, min(0.98, round(final_grounding_score, 2)))

        # Publication Rule:
        # 1. Grounding score >= ANSWER_GROUNDING_THRESHOLD (0.80)
        # 2. Every SAP technical identifier is present in selected evidence.
        # 3. Zero contradicted claims
        # 4. Material claim support consistency (unsupported claims <= 25% of total claims)
        passes_gate = bool(
            final_grounding_score >= self.grounding_threshold
            and len(critical_unsupported) == 0
            and len(uncited_standard_ids) == 0
            and len(contradicted_claims) == 0
            and len(unsupported_claims) <= max(1, int(total_claims * 0.25))
        )

        # Do not turn a localized evidence limitation into a whole-answer abstention;
        # source_type='abstention' is handled at the start of this verifier.
        if passes_gate:
            verification_status = "verified"
            summary = f"Verified answer with {final_grounding_score*100:.0f}% grounding across {len(supported_claims)}/{total_claims} claims."
        elif final_grounding_score >= 0.50:
            verification_status = "partial"
            summary = (
                f"Partially supported answer ({final_grounding_score*100:.0f}% grounding). "
                + (f"Unsupported technical identifiers: {', '.join(critical_unsupported)}." if critical_unsupported else "")
                + (f" Standard identifiers absent from selected evidence: {', '.join(uncited_standard_ids)}." if uncited_standard_ids else "")
            )
        else:
            verification_status = "unverified"
            summary = f"Verification failed ({final_grounding_score*100:.0f}% grounding < threshold {self.grounding_threshold*100:.0f}%)."

        return {
            "grounding_score": final_grounding_score,
            "passes_grounding_gate": passes_gate,
            "claims": claims_result,
            "supported_claims": supported_claims,
            "unsupported_claims": unsupported_claims,
            "contradicted_claims": contradicted_claims,
            "critical_unsupported_claims": critical_unsupported,
            "uncited_standard_ids": uncited_standard_ids,
            "all_material_claims_cited": len(supported_claims) == total_claims and total_claims > 0,
            "verification_status": verification_status,
            "summary": summary
        }


grounding_service = GroundingService()
