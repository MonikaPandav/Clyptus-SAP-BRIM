"""
BRIM-Specific Relevance Gate for GitHub Repository Chunks.
Enforces strict pre-embedding filtering:
1. Validates against the 638-identifier BRIM index (corpus_identifier_index.json).
2. Evaluates contextual seed keywords with token boundaries and acronym disambiguation.
3. Computes dense semantic similarity against verified SAP BRIM anchor embeddings (384-dim).
4. Strictly enforces:
   KEEP = (MATCHES_IDENTIFIER_INDEX or MATCHES_CONTEXTUAL_BRIM_KEYWORD_SET) and ANCHOR_SIMILARITY >= CALIBRATED_THRESHOLD
5. Emits machine-readable rejection reasons and tracks low-yield thresholds.
"""

import os
import re
import json
import hashlib
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple, Optional

from backend.app.config import settings
from backend.app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"
IDENTIFIER_INDEX_PATH = CORPUS_DIR / "corpus_identifier_index.json"

# Curated, verified SAP BRIM Anchor Passages across all 6 BRIM modules
VERIFIED_BRIM_ANCHORS = [
    # Anchor 1: SOM (Subscription Order Management)
    (
        "SAP Subscription Order Management SOM manages the lifecycle of subscription products, "
        "provider orders, and provider contracts. Master data objects include Business Partner BUT000, "
        "Contract Account VKONT table FKKVKP, and technical resource data. Order Distribution Infrastructure "
        "ODI asynchronously distributes provider contracts to SAP Convergent Charging and SAP FI-CA."
    ),
    # Anchor 2: CC (Convergent Charging)
    (
        "SAP Convergent Charging CC provides real-time high-throughput rating and charging for consumption events. "
        "Core structures include charge plans, allowance plans, pricing logic trees, subscriber accounts, "
        "and the BART charging batch architecture. CC rates usage metrics and dispatches charged items to CI."
    ),
    # Anchor 3: CI (Convergent Invoicing)
    (
        "SAP Convergent Invoicing CI processes consumption items CIT and billable items BIT. "
        "Billable items move from Raw status 0 to Billable status 2 and Billed status 4 via transaction FKKBIX_BILL_M. "
        "Invoicing runs aggregate billing documents into official invoicing documents and contract accounting subledger documents."
    ),
    # Anchor 4: FI-CA (Contract Accounts Receivable and Payable)
    (
        "SAP FI-CA Contract Accounts Receivable and Payable is the high-volume subledger for BRIM. "
        "Open and cleared items reside in table DFKKOP. It manages incoming payments, clearing variants, dunning procedures, "
        "reconciliation keys, posting area 0010, and integration to standard general ledger ACDOCA BSEG."
    ),
    # Anchor 5: RAR (Revenue Accounting and Reporting)
    (
        "SAP Revenue Accounting and Reporting RAR integrates with BRIM to comply with IFRS 15 and ASC 606 revenue standards. "
        "Revenue accounting items RAI are created from provider contracts and billing documents to recognize revenue across performance obligations POB."
    ),
    # Anchor 6: Convergent Mediation
    (
        "SAP Convergent Mediation collects raw offline and online network events, performs mediation and filtering, "
        "and normalizes CDRs into standard consumption items CIT and billable items BIT for rating in CC or invoicing in CI."
    ),
    # Anchor 7: End-to-End BRIM Architecture & APIs
    (
        "SAP Billing and Revenue Innovation Management BRIM end-to-end integration architecture linking "
        "quote-to-cash subscription billing, rating, convergent invoicing, financial contract accounts, "
        "and partner revenue sharing."
    )
]

# Explicit contextual disambiguation vocabularies for short acronyms
ACRONYM_CONTEXTS = {
    "cc": {
        "convergent charging", "charging", "rating", "sap cc", "charge plan", "allowance",
        "bart", "subscriber account", "provider contract", "sap brim", "charging contract"
    },
    "ci": {
        "convergent invoicing", "invoicing", "billing", "sap ci", "billable item", "bit",
        "consumption item", "cit", "fkkbix", "invoicing document", "sap brim", "fkkinv"
    },
    "som": {
        "subscription order", "subscription order management", "sap som", "provider order",
        "odi", "order distribution", "solution quotation", "subscription product", "sap brim"
    },
    "rar": {
        "revenue accounting", "revenue recognition", "ifrs 15", "pob", "performance obligation",
        "sap rar", "contract reversal", "rai", "revenue contract"
    },
    "bit": {
        "billable item", "convergent invoicing", "fkkbix", "consumption item", "billing",
        "status 0", "status 2", "status 4", "raw item", "billable items"
    },
    "cit": {
        "consumption item", "convergent invoicing", "rating", "mediation", "consumption items",
        "fkkbixcit"
    }
}

# Negative contexts that indicate unambiguous FALSE matches for BRIM terms
FALSE_POSITIVE_INDICATORS = {
    "electric vehicle": "ev_charging_false_positive",
    "ev charging": "ev_charging_false_positive",
    "ocpp": "ev_charging_false_positive",
    "kilowatt": "ev_charging_false_positive",
    "battery charging": "ev_charging_false_positive",
    "brim financial": "brim_financial_false_positive",
    "brim mastercard": "brim_financial_false_positive",
    "credit card rewards": "brim_financial_false_positive",
    "k6 load test": "generic_infra_unrelated",
    "prometheus metrics": "generic_infra_unrelated",
    "kafka broker": "generic_infra_unrelated",
    "opentelemetry collector": "generic_infra_unrelated"
}


class BRIMRelevanceGate:
    def __init__(self):
        self.identifier_index: Dict[str, Any] = {}
        self.identifier_set: Set[str] = set()
        self.index_hash: str = ""
        self.index_count: int = 0
        self.anchor_embeddings: Optional[np.ndarray] = None
        self.calibrated_threshold: float = settings.REPO_GATE_CALIBRATED_THRESHOLD
        self._load_identifier_index()
        self._init_anchor_embeddings()

    def _load_identifier_index(self):
        """Loads and verifies the 638-identifier index from corpus_identifier_index.json."""
        if not IDENTIFIER_INDEX_PATH.exists():
            logger.error(f"Identifier index file not found at {IDENTIFIER_INDEX_PATH}")
            return

        with open(IDENTIFIER_INDEX_PATH, "rb") as f:
            content = f.read()
            self.index_hash = hashlib.sha256(content).hexdigest()

        with open(IDENTIFIER_INDEX_PATH, "r", encoding="utf-8") as f:
            self.identifier_index = json.load(f)

        self.index_count = len(self.identifier_index)
        # Store uppercase normalized set for fast case-insensitive exact matching
        self.identifier_set = {k.upper() for k in self.identifier_index.keys()}
        logger.info(
            f"BRIM Relevance Gate initialized with {self.index_count} identifiers. "
            f"Index SHA256: {self.index_hash[:16]}..."
        )

    def _init_anchor_embeddings(self):
        """Embeds verified SAP BRIM anchor passages into the 384-dimensional space."""
        try:
            vectors = embedding_service.embed_batch(VERIFIED_BRIM_ANCHORS)
            arr = np.array(vectors, dtype=np.float32)
            # Ensure unit normalization for cosine similarity
            norms = np.linalg.norm(arr, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self.anchor_embeddings = arr / norms
            logger.info(f"Initialized {len(VERIFIED_BRIM_ANCHORS)} verified SAP BRIM anchor embeddings.")
        except Exception as e:
            logger.error(f"Failed to initialize anchor embeddings: {e}")
            self.anchor_embeddings = np.zeros((len(VERIFIED_BRIM_ANCHORS), settings.EMBEDDING_DIM), dtype=np.float32)

    def check_identifier_matches(self, text: str) -> List[str]:
        """
        Extracts candidate tokens and checks exact match against the 638-identifier index.
        Requires uppercase / exact technical identifier casing to avoid false-matching common code variables.
        """
        if not self.identifier_set:
            return []

        tokens = set(re.findall(r"\b(/[A-Z0-9_]{2,}/[A-Z0-9_]+|[A-Z][A-Z0-9_]{2,29})\b", text))
        matched = []
        for t in tokens:
            if t == "VALUE":
                continue
            if t in self.identifier_set:
                matched.append(t)
        return matched

    def check_contextual_keywords(self, text: str) -> Tuple[bool, List[str], Optional[str]]:
        """
        Evaluates contextual seed keywords with token boundaries and acronym disambiguation.
        Returns: (passes_keyword_check, matched_terms, false_positive_reason)
        """
        text_lower = text.lower()

        # Check explicit negative false positive indicators
        for neg_indicator, reason in FALSE_POSITIVE_INDICATORS.items():
            if neg_indicator in text_lower:
                return False, [], reason

        matched_terms = []

        # 1. High-confidence unambiguous multi-word phrases
        unambiguous_phrases = [
            "sap brim", "billing and revenue innovation management",
            "convergent charging", "convergent invoicing", "convergent mediation",
            "subscription order management", "subscription order",
            "provider contract", "provider order", "contract account",
            "billable item", "billable items", "consumption item", "consumption items",
            "contract accounts receivable and payable", "fi-ca", "fica",
            "charge plan", "allowance plan", "pricing logic"
        ]

        for phrase in unambiguous_phrases:
            pattern = r"\b" + re.escape(phrase) + r"\b"
            if re.search(pattern, text_lower):
                matched_terms.append(phrase)

        # 2. Contextual acronym checks (must be substantiated by nearby BRIM context)
        for acronym, contexts in ACRONYM_CONTEXTS.items():
            pattern = r"\b" + re.escape(acronym) + r"\b"
            if re.search(pattern, text_lower):
                has_context = any(ctx in text_lower for ctx in contexts)
                if has_context:
                    matched_terms.append(f"{acronym} (contextual)")

        # 3. Seed terms with token boundaries
        seed_single_terms = ["rating", "allowance"]
        for term in seed_single_terms:
            pattern = r"\b" + re.escape(term) + r"\b"
            if re.search(pattern, text_lower):
                # Ensure it appears with SAP or BRIM or charging context
                if any(k in text_lower for k in ["sap", "brim", "charge", "pricing", "billing", "invoice"]):
                    matched_terms.append(term)

        passes = len(matched_terms) > 0
        return passes, matched_terms, None

    def compute_anchor_similarity(self, text: str) -> float:
        """
        Computes maximum cosine similarity between candidate text embedding
        and the verified SAP BRIM anchor set in 384-dim space.
        """
        if self.anchor_embeddings is None or self.anchor_embeddings.shape[0] == 0:
            return 0.0

        vec = embedding_service.embed_text(text)
        vec_arr = np.array(vec, dtype=np.float32)
        norm = np.linalg.norm(vec_arr)
        if norm > 0:
            vec_arr = vec_arr / norm
        else:
            return 0.0

        sims = self.anchor_embeddings @ vec_arr
        max_sim = float(np.max(sims))
        return round(max(0.0, min(1.0, max_sim)), 4)

    def evaluate_chunk(
        self,
        chunk_text: str,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Evaluates candidate chunk against the non-negotiable rule:
        KEEP = (MATCHES_IDENTIFIER_INDEX or MATCHES_CONTEXTUAL_BRIM_KEYWORD_SET)
               and ANCHOR_SIMILARITY >= CALIBRATED_THRESHOLD
        """
        active_threshold = threshold if threshold is not None else self.calibrated_threshold

        # 1. Check identifier index
        matched_identifiers = self.check_identifier_matches(chunk_text)
        has_id_match = len(matched_identifiers) > 0

        # 2. Check contextual keywords
        has_kw_match, matched_kws, fp_reason = self.check_contextual_keywords(chunk_text)

        if fp_reason:
            return {
                "keep": False,
                "decision": "DROP",
                "reason": fp_reason,
                "rejection_reason": fp_reason,
                "anchor_similarity": 0.0,
                "matched_identifiers": [],
                "matched_keywords": [],
                "passes_keywords": False,
                "threshold": active_threshold
            }

        lexical_condition = has_id_match or has_kw_match
        if not lexical_condition:
            return {
                "keep": False,
                "decision": "DROP",
                "reason": "failed_both_keyword_and_identifier_index",
                "rejection_reason": "failed_both_keyword_and_identifier_index",
                "anchor_similarity": 0.0,
                "matched_identifiers": [],
                "matched_keywords": [],
                "passes_keywords": False,
                "threshold": active_threshold
            }

        # 3. Compute anchor similarity only if lexical condition passed
        anchor_sim = self.compute_anchor_similarity(chunk_text)
        similarity_condition = anchor_sim >= active_threshold

        # 4. Acceptance Rule
        keep = bool(lexical_condition and similarity_condition)

        # 5. Machine-readable rejection reason
        rejection_reason = None
        if not keep:
            rejection_reason = f"below_anchor_similarity_threshold ({anchor_sim:.4f} < {active_threshold:.4f})"

        decision = "KEEP" if keep else "DROP"
        return {
            "keep": keep,
            "decision": decision,
            "reason": rejection_reason,
            "rejection_reason": rejection_reason,
            "anchor_similarity": anchor_sim,
            "matched_identifiers": matched_identifiers,
            "matched_keywords": matched_kws,
            "passes_keywords": has_kw_match,
            "threshold": active_threshold
        }


brim_relevance_gate = BRIMRelevanceGate()
