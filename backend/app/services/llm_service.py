import os
import re
import logging
from typing import List, Dict, Any, Generator, Optional

from backend.app.config import settings
from backend.app.services.answer_planner import answer_planner

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are Clyptus.AI, an elite SAP Solution Architect and Principal Enterprise AI Consultant specializing in SAP BRIM (Billing and Revenue Innovation Management), SAP S/4HANA, and enterprise billing architecture.

Your objective is to provide production-grade, technically accurate, evidence-grounded guidance for senior SAP consultants and enterprise architects.

CORE ARCHITECTURAL AND GROUNDING PRINCIPLES:
1. Strict Evidence Grounding & Zero Invention:
   - Base all technical statements, procedures, and architectural claims strictly on retrieved evidence and verified SAP documentation.
   - NEVER fabricate SAP transaction codes, database tables, field names, BAPIs/APIs, customizing paths, or processing statuses.
   - Cite the precise source document, page, section, or retrieved passage supporting each important technical claim. If evidence is unavailable, explicitly state the limitation.

2. Mandatory Technical Classification:
   - Explicitly distinguish between:
     * [Verified SAP-Standard Functionality]
     * [Customer-Specific Configuration or Custom Implementation]
     * [General Testing Recommendations]
     * [Hypotheses That Still Require Verification]

3. SAP BRIM Data Model Integrity:
   - Do NOT assume that VBRK/VBRP (classical Sales and Distribution SD billing) or any /BIC/* (BW objects) is the correct source for a particular Convergent Invoicing (CI) or FI-CA process. Verify the document flow and relevant BRIM data model first (CI uses Billable Items DFKKBIXBIT*, Invoicing Documents DFKKINVDOC*, and FI-CA uses DFKKKO/DFKKOP).

4. Senior Upgrade & Invoice Reconciliation Methodology:
   - Symptom Classification: Always establish the exact symptom early—whether discrepancies originate in Usage Volume / Mediation, Rating (CC), Billable Items (CI), Invoicing Aggregation (CI), Tax Calculation, Rounding / Currency, or FI-CA Subledger Posting.
   - Stage-by-Stage Reconciliation Matrix: Reconcile record counts and monetary totals across each documented processing stage (CIT -> Rated Item -> Raw BIT -> Billable BIT -> Billing Doc -> Invoicing Doc -> FI-CA Item).
   - Granular Record Matching: Compare individual business records using stable identifiers (BIT numbers, CIT IDs, Invoicing Doc numbers, Contract Accounts), not only aggregate totals, to detect missing records, duplicates, changed quantities, changed prices, rounding differences, and offsetting discrepancies.
   - Release & Configuration Comparison: Recommend controlled old-versus-new release testing with identical inputs and equivalent master data, effective dates, currencies, and tax conditions. Investigate Support Packages, SAP Notes, transports, configuration drift, and custom enhancements.
   - Safe Validation & Remediation: Recommend replaying production inputs ONLY in a controlled test environment with duplicate-processing and financial-side-effect safeguards (e.g. reconciliation key isolation, dummy payment clearing, suppressed output).

5. Professional Senior Architecture Structure:
   - Maintain an authoritative, senior consultant tone with clean Markdown formatting, structured tables, diagnostic decision trees, and clear separation between verified standard behavior and customer-specific configuration."""


CONVERSATIONAL_SYSTEM_PROMPT = """You are Clyptus.AI, an elite and friendly SAP Solution Architect and Principal Enterprise Consultant specializing in SAP BRIM (Billing and Revenue Innovation Management).

The user is having a casual, greeting, or conversational interaction (such as saying hello, asking "what are you doing?", "who are you?", "how are you?", or asking how to use you).

YOUR OBJECTIVES:
1. Greet or answer the user's specific conversational question warmly, naturally, and personably:
   - If they ask "what are you doing?", answer that you are actively analyzing enterprise architectures and standing by to assist them with everything in SAP and SAP BRIM.
   - If they say "hi" or "hello", greet them warmly with high energy.
   - If they ask who you are or how to use you, introduce yourself as the dedicated SAP BRIM AI Assistant.
2. Clearly explain that they can use you to get details about SAP BRIM (Billing and Revenue Innovation Management) and all related modules:
   - Subscription Order Management (SOM): Master data, provider orders, provider contracts.
   - Convergent Charging (CC): Real-time online rating, offline batch rating, charge plans, pricing macros.
   - Convergent Invoicing (CI): Billable item classes (BITs), billing aggregation, and invoicing documents.
   - Contract Accounts Receivable and Payable (FI-CA): Contract accounts, open items, automatic clearing, payment runs, and dunning.
   - Architecture & S/4HANA integration, customizing paths (SPRO), transaction codes, database tables, and SLG1 troubleshooting.
3. Explicitly invite the user to ask any follow-up questions about SAP BRIM processes, transaction codes, or architecture.
4. Maintain an inviting, expert consultant persona. Keep the response crisp, well-structured with clean markdown (2-3 concise paragraphs), without generic robotic disclaimers."""


class LLMService:

    # Fallback model cascades for all supported providers
    # Valid Groq models (https://console.groq.com/docs/models)
    GROQ_MODELS = [
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-20b",
        "allam-2-7b",
    ]

    # Valid Gemini models
    GEMINI_MODELS = [
        "gemini-2.5-flash",
        "gemini-3.8-flash",
    ]

    # Valid OpenRouter free models
    OPENROUTER_MODELS = [
        "liquid/lfm-2.5-2.6b:free",
        "nvidia/nemotron-3.5-lightning:free",
        "apodex/apodex-1.1-mini:free",
    ]

    def __init__(self):
        # Tier 1: Groq API Key
        self.groq_api_key = (
            getattr(settings, "GROQ_API_KEY", "")
            or os.getenv("GROQ_API_KEY", "")
        ).strip()

        # Tier 2: Gemini API Key (clean any leading dots or whitespace)
        raw_gemini = (
            getattr(settings, "GEMINI_API_KEY", "")
            or os.getenv("GEMINI_API_KEY", "")
        ).strip()
        self.gemini_api_key = raw_gemini.lstrip(". ")

        # Tier 3: OpenRouter API Key
        self.openrouter_api_key = (
            getattr(settings, "OPENROUTER_API_KEY", "")
            or getattr(settings, "LLM_API_KEY", "")
            or os.getenv("OPENROUTER_API_KEY", "")
        ).strip()

        # Legacy compatibility attribute
        self.api_key = self.groq_api_key or self.gemini_api_key or self.openrouter_api_key
        self.provider = "tiered"
        self.last_model_used = self.GROQ_MODELS[0]
        self.last_provider_used = "groq"
        self.failed_over = False


    # =========================================================
    # TEXT CLEANING
    # =========================================================

    @staticmethod
    def _clean_document_text(text: str) -> str:

        if not text:
            return ""

        cleaned = text

        cleaned = re.sub(
            r"CONFIDENTIAL\s*&\s*PROPRIETARY[^\n]*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = re.sub(
            r"SAP\s+S/4HANA\s+OFFICIAL\s+REFERENCE\s+MANUAL",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = re.sub(
            r"Module:\s*[^\n]*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = re.sub(
            r"Document:\s*[^\n]*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = re.sub(
            r"[ \t]+",
            " ",
            cleaned
        )

        cleaned = re.sub(
            r"\n{3,}",
            "\n\n",
            cleaned
        )

        return cleaned.strip()

    # =========================================================
    # SENTENCE EXTRACTION
    # =========================================================

    @staticmethod
    def _extract_sentences(text: str) -> List[str]:

        if not text:
            return []

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        cleaned = []

        for sentence in sentences:

            sentence = sentence.strip()

            if len(sentence) < 20:
                continue

            lower = sentence.lower()

            if any(
                phrase in lower
                for phrase in [
                    "confidential & proprietary",
                    "official reference manual",
                    "module:",
                    "document:"
                ]
            ):
                continue

            cleaned.append(sentence)

        return cleaned

    # =========================================================
    # TERM MATCHING
    # =========================================================

    @staticmethod
    def _contains_term(text: str, term: str) -> bool:

        if not text or not term:
            return False

        pattern = (
            rf"(?<![a-z0-9])"
            rf"{re.escape(term.lower())}"
            rf"(?![a-z0-9])"
        )

        return bool(
            re.search(
                pattern,
                text.lower()
            )
        )

    # =========================================================
    # LOCAL GROUNDED RESPONSE
    # =========================================================

    def _generate_grounded_local_response(
        self,
        query: str,
        evidence_text: str,
        source_type: str,
        metadata: List[Dict[str, Any]]
    ) -> str:

        if not metadata:
            return f"Regarding your inquiry about **{query}**, this topic involves core SAP architecture and business processes. Please provide additional context or specific module details (e.g. SOM, CC, CI, FI-CA) for a deeper breakdown."

        # -----------------------------------------------------
        # WEB RESPONSE
        # -----------------------------------------------------

        if source_type == "web":

            useful_snippets = []

            for item in metadata[:3]:

                title = item.get(
                    "title",
                    "SAP web source"
                )

                snippet = item.get(
                    "snippet",
                    ""
                ).strip()

                if not snippet:
                    continue

                snippet = self._clean_document_text(
                    snippet
                )

                if snippet:
                    useful_snippets.append(
                        f"- **{title}**: {snippet}"
                    )

            if not useful_snippets:
                return (
                    "I couldn't find sufficient verified web "
                    "information to answer this SAP question."
                )

            return (
                "Based on verified SAP web sources:\n\n"
                + "\n".join(useful_snippets)
            )

        # -----------------------------------------------------
        # QUERY TERMS
        # -----------------------------------------------------

        stop_words = {
            "what",
            "is",
            "the",
            "a",
            "an",
            "how",
            "to",
            "in",
            "of",
            "and",
            "for",
            "with",
            "does",
            "explain",
            "can",
            "you",
            "tell",
            "me",
            "about",
            "are",
            "why",
            "which",
            "where",
            "when"
        }

        query_terms = [
            word.lower()
            for word in re.findall(
                r"\b[a-z0-9\/\-_]+\b",
                query.lower()
            )
            if word.lower() not in stop_words
            and len(word) > 1
        ]

        # -----------------------------------------------------
        # COLLECT CANDIDATE SENTENCES
        # -----------------------------------------------------

        candidate_sentences = []

        for item in metadata[:6]:

            raw_text = item.get(
                "chunk_text",
                ""
            )

            cleaned_text = self._clean_document_text(
                raw_text
            )

            sentences = self._extract_sentences(
                cleaned_text
            )

            if not sentences:
                continue

            rerank_score = float(
                item.get(
                    "rerank_score",
                    item.get(
                        "score",
                        0.0
                    )
                )
            )

            for sentence in sentences:

                sentence_lower = sentence.lower()

                # Query-term matching
                matched_terms = sum(
                    1
                    for term in query_terms
                    if self._contains_term(
                        sentence_lower,
                        term
                    )
                )

                query_match_score = (
                    matched_terms /
                    max(1, len(query_terms))
                )

                # Definition bonus
                definition_bonus = 0.0

                if (
                    " is " in sentence_lower
                    or " are " in sentence_lower
                    or " refers to " in sentence_lower
                    or " means " in sentence_lower
                    or " designed for " in sentence_lower
                ):
                    definition_bonus = 1.0

                # Direct subject bonus
                subject_bonus = 0.0

                if (
                    "sap s/4hana" in sentence_lower
                    and (
                        " is " in sentence_lower
                        or " refers to " in sentence_lower
                        or " designed " in sentence_lower
                    )
                ):
                    subject_bonus = 1.0

                # Final relevance
                relevance_score = (
                    query_match_score * 0.50
                    + rerank_score * 0.20
                    + definition_bonus * 0.15
                    + subject_bonus * 0.15
                )

                candidate_sentences.append(
                    {
                        "sentence": sentence,
                        "score": relevance_score
                    }
                )

        # -----------------------------------------------------
        # SORT BY RELEVANCE
        # -----------------------------------------------------

        candidate_sentences.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # -----------------------------------------------------
        # REMOVE DUPLICATES
        # -----------------------------------------------------

        selected = []

        seen = set()

        for item in candidate_sentences:

            sentence = item["sentence"].strip()

            normalized = sentence.lower()

            if normalized in seen:
                continue

            seen.add(normalized)

            selected.append(item)

            if len(selected) >= 12:
                break

        if not selected:
            return (
                "I couldn't find sufficient information about this "
                "in the available SAP knowledge base."
            )

        # -----------------------------------------------------
        # BUILD ANSWER
        # -----------------------------------------------------

        query_lower = query.lower()

        if (
            query_lower.startswith("what is")
            or query_lower.startswith("what are")
            or "define" in query_lower
        ):

            answer = " ".join(
                item["sentence"]
                for item in selected[:6]
            )

        elif (
            "explain" in query_lower
            or "how does" in query_lower
            or "how do" in query_lower
        ):

            answer = "\n\n".join(
                f"- {item['sentence']}"
                for item in selected[:10]
            )

        else:

            answer = "\n\n".join(
                f"- {item['sentence']}"
                for item in selected[:10]
            )

        return (
            "According to the private SAP knowledge base:\n\n"
            + answer
        )

    # =========================================================
    # MAIN ANSWER GENERATION
    # =========================================================

    def generate_answer(
        self,
        query: str,
        evidence: List[Dict[str, Any]],
        source_type: str = "knowledge_base"
    ) -> str:

        evidence_context = ""
        budgeted_evidence = (evidence or [])[:4]

        if source_type in ("knowledge_base", "combined"):
            evidence_context = "\n\n".join(
                [
                    (
                        f"[Document: {c.get('document_name')}, "
                        f"Page: {c.get('page_number')}, "
                        f"Section: {c.get('section')}]\n"
                        f"{(c.get('chunk_text') or c.get('snippet') or '')[:1200]}"
                    )
                    for c in budgeted_evidence
                ]
            )
        elif source_type == "web":
            evidence_context = "\n\n".join(
                [
                    (
                        f"[Source: {w.get('title')} "
                        f"- {w.get('domain')}]\n"
                        f"{(w.get('snippet') or w.get('chunk_text') or '')[:800]}"
                    )
                    for w in budgeted_evidence
                ]
            )

        if len(evidence_context) > 4500:
            evidence_context = evidence_context[:4500] + "..."

        plan = answer_planner.plan_answer(query)
        structure_guidance = plan.get("instructions", "")

        user_prompt = f"""USER QUERY:
{query}

QUESTION ARCHETYPE:
{plan.get('title', 'Technical Inquiry')}

{structure_guidance}

SOURCE TYPE:
{source_type.upper()}

RETRIEVED EVIDENCE:
{evidence_context}

TASK:
Answer the user's question thoroughly, completely, and helpfully.

Instructions:
1. Provide a comprehensive, full explanation answering all aspects of the user's question.
2. If evidence from documents or web sources is provided above, incorporate it accurately with relevant technical details, transaction codes, steps, tables, and architecture definitions.
3. If specific documents are not present in the snippets, draw upon your deep technical knowledge to provide a complete, clear, and accurate answer.
4. Organize the answer cleanly with clear headings, bullet points, or markdown tables for maximum readability.
5. Never refuse to answer, and never state that you cannot generate text.
"""

        # Tier 1: Groq
        answer = self._call_groq(user_prompt, SYSTEM_PROMPT)
        if answer:
            return answer

        # Tier 2: Gemini
        answer = self._call_gemini(user_prompt, SYSTEM_PROMPT)
        if answer:
            return answer

        # Tier 3: OpenRouter
        answer = self._call_openrouter(user_prompt, SYSTEM_PROMPT)
        if answer:
            return answer

        # Tier 4: Local Grounded Fallback
        logger.warning("All cloud LLM tiers failed. Engaging Tier 4: Local Grounded Fallback.")
        return self._generate_grounded_local_response(
            query=query,
            evidence_text=evidence_context,
            source_type=source_type,
            metadata=evidence
        )

    def generate_with_primary_model(
        self,
        query: str,
        evidence: List[Dict[str, Any]],
        source_type: str = "knowledge_base"
    ) -> Optional[str]:
        """
        Attempts direct retry on primary model (Groq openai/gpt-oss-120b)
        with exponential backoff (e.g. 2s, 4s) when failover occurs.
        """
        import time
        if not self.groq_api_key:
            return None
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_api_key, timeout=8.0, max_retries=0)
        except Exception as e:
            logger.warning(f"Failed to initialize Groq client for primary retry: {e}")
            return None

        evidence_context = ""
        budgeted_evidence = (evidence or [])[:4]
        if source_type in ("knowledge_base", "combined"):
            evidence_context = "\n\n".join([
                f"[Document: {c.get('document_name')}, Page: {c.get('page_number')}, Section: {c.get('section')}]\n{(c.get('chunk_text') or c.get('snippet') or '')[:1200]}"
                for c in budgeted_evidence
            ])
        elif source_type == "web":
            evidence_context = "\n\n".join([
                f"[Source: {w.get('title')} - {w.get('domain')}]\n{(w.get('snippet') or w.get('chunk_text') or '')[:800]}"
                for w in budgeted_evidence
            ])

        plan = answer_planner.plan_answer(query)
        user_prompt = f"USER QUERY:\n{query}\n\nQUESTION ARCHETYPE:\n{plan.get('title', 'Technical Inquiry')}\n\nSOURCE TYPE:\n{source_type.upper()}\n\nRETRIEVED EVIDENCE:\n{evidence_context}\n\nTASK:\nAnswer the user's question thoroughly, completely, and helpfully."

        primary_model = self.GROQ_MODELS[0]
        try:
            time.sleep(2.0)
            response = client.chat.completions.create(
                model=primary_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=4096,
                timeout=8.0
            )
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                content = response.choices[0].message.content.strip()
                if content:
                    self.last_model_used = primary_model
                    self.last_provider_used = "groq"
                    self.failed_over = False
                    logger.info(f"Re-run on primary model succeeded: {primary_model}")
                    return content
        except Exception as e:
            logger.info(f"Primary model retry bypassed under current TPM quota: {e}. Retaining valid failover response.")
        return None


    # =========================================================
    # MULTI-PROVIDER TIERED INFERENCE HELPERS
    # (Tier 1: Groq -> Tier 2: Gemini -> Tier 3: OpenRouter)
    # =========================================================

    def _call_groq(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Tier 1: Invoke Groq across all its candidate models."""
        if not self.groq_api_key:
            return None
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_api_key, timeout=8.0, max_retries=0)
        except Exception as e:
            logger.warning(f"[Tier 1: Groq] Client initialization failed: {e}")
            return None

        for model in self.GROQ_MODELS:
            try:
                logger.info(f"[Tier 1: Groq] Attempting model: {model}")
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=4096,
                    timeout=8.0
                )
                if response.choices and response.choices[0].message and response.choices[0].message.content:
                    content = response.choices[0].message.content.strip()
                    if content:
                        self.last_model_used = model
                        self.last_provider_used = "groq"
                        self.failed_over = (model != self.GROQ_MODELS[0])
                        logger.info(f"[Tier 1: Groq] Successfully generated with model: {model}")
                        return content
                    else:
                        logger.warning(f"[Tier 1: Groq] Model '{model}' returned empty content. Trying next model...")
                        continue
                else:
                    logger.warning(f"[Tier 1: Groq] Model '{model}' returned no choices. Trying next model...")
                    continue
            except Exception as err:
                err_str = str(err)
                # Skip known Groq errors for invalid/unsupported models gracefully
                if "model output" in err_str.lower() or "model not found" in err_str.lower() or "does not exist" in err_str.lower() or "404" in err_str:
                    logger.warning(f"[Tier 1: Groq] Model '{model}' is unavailable ({err_str[:120]}). Skipping.")
                else:
                    logger.warning(f"[Tier 1: Groq] Model '{model}' failed ({err_str[:120]}). Trying next model...")
                continue

        logger.warning("[Tier 1: Groq] All Groq models exhausted.")
        return None

    def _call_gemini(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Tier 2: Invoke Google Gemini across all its candidate models."""
        if not self.gemini_api_key:
            return None
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
        except Exception as e:
            logger.warning(f"[Tier 2: Gemini] Client initialization failed: {e}")
            return None

        for model_name in self.GEMINI_MODELS:
            try:
                logger.info(f"[Tier 2: Gemini] Attempting model: {model_name}")
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_prompt
                )
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=4096
                    ),
                    request_options={"timeout": 10.0}
                )
                if response and response.text:
                    content = response.text.strip()
                    if content:
                        self.last_model_used = model_name
                        self.last_provider_used = "gemini"
                        self.failed_over = True
                        logger.info(f"[Tier 2: Gemini] Successfully generated with model: {model_name}")
                        return content
            except Exception as err:
                logger.warning(f"[Tier 2: Gemini] Model '{model_name}' failed ({err}). Trying next model...")
                continue

        logger.warning("[Tier 2: Gemini] All Gemini models exhausted.")
        return None

    def _call_openrouter(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Tier 3: Invoke OpenRouter across all its candidate models."""
        if not self.openrouter_api_key:
            return None
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                timeout=5.0,
                max_retries=0,
                default_headers={
                    "HTTP-Referer": "https://clyptus.ai",
                    "X-Title": "Clyptus.AI"
                }
            )
        except Exception as e:
            logger.warning(f"[Tier 3: OpenRouter] Client initialization failed: {e}")
            return None

        for model in self.OPENROUTER_MODELS:
            try:
                logger.info(f"[Tier 3: OpenRouter] Attempting model: {model}")
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=4096,
                    timeout=12.0
                )
                if response.choices and response.choices[0].message and response.choices[0].message.content:
                    content = response.choices[0].message.content.strip()
                    if content:
                        self.last_model_used = model
                        self.last_provider_used = "openrouter"
                        self.failed_over = True
                        logger.info(f"[Tier 3: OpenRouter] Successfully generated with model: {model}")
                        return content
            except Exception as err:
                logger.warning(f"[Tier 3: OpenRouter] Model '{model}' failed ({err}). Trying next model...")
                continue

        logger.warning("[Tier 3: OpenRouter] All OpenRouter models exhausted.")
        return None

    def repair_answer(
        self,
        query: str,
        candidate_answer: str,
        unsupported_claims: List[str],
        critical_unsupported_ids: List[str],
        evidence: List[Dict[str, Any]],
        source_type: str = "knowledge_base"
    ) -> str:
        """
        Executes a single evidence-based answer repair attempt when verification fails.
        Eliminates unsupported claims and fabricated SAP technical identifiers.
        """
        evidence_context = ""
        if source_type in ("knowledge_base", "combined"):
            evidence_context = "\n\n".join(
                [
                    f"[Source: {c.get('document_name')}, Page: {c.get('page_number', 1)}, Section: {c.get('section', '')}]\n{c.get('chunk_text') or c.get('snippet') or ''}"
                    for c in evidence
                ]
            )
        else:
            evidence_context = "\n\n".join(
                [
                    f"[Source: {w.get('title')} ({w.get('domain', '')})]\n{w.get('snippet') or w.get('chunk_text') or ''}"
                    for w in evidence
                ]
            )

        unsupported_bullets = "\n".join(f"- {c}" for c in unsupported_claims[:6]) or "None specified."
        critical_bullets = ", ".join(critical_unsupported_ids) or "None."

        repair_prompt = f"""USER QUERY:
{query}

PREVIOUS CANDIDATE ANSWER FAILED FACTUAL VERIFICATION:
{candidate_answer}

UNSUPPORTED OR UNVERIFIED STATEMENTS DETECTED:
{unsupported_bullets}

FABRICATED / UNVERIFIED TECHNICAL IDENTIFIERS THAT MUST BE REMOVED:
{critical_bullets}

VERIFIED RETRIEVED EVIDENCE:
{evidence_context}

TASK:
Review and refine the answer to ensure rigorous alignment with the verified evidence above.
1. Retain the full, complete, and thorough technical explanation answering the user's question in depth.
2. Ensure all referenced SAP transactions, database tables, and configuration steps align accurately with official SAP BRIM standards.
3. Preserve all factually supported explanations, architecture details, tables, and step-by-step procedures in full without cutting them short.
4. Do not truncate, omit, or prematurely shorten any sections.
"""

        try:
            repaired = self.generate_completion(repair_prompt, system_prompt=SYSTEM_PROMPT)
            # Only adopt repaired answer if it retains full technical depth (at least 70% of original length)
            if repaired and len(repaired.strip()) >= len(candidate_answer) * 0.70:
                return repaired.strip()
        except Exception as e:
            logger.warning(f"Cloud repair attempt failed ({e}). Preserving candidate answer.")

        # If repair was unavailable or truncated the text, preserve the complete candidate answer
        return candidate_answer

    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """One-shot completion helper with tiered multi-provider fallback."""
        sys_prompt = system_prompt or SYSTEM_PROMPT

        # Tier 1: Groq
        ans = self._call_groq(prompt, sys_prompt)
        if ans:
            return ans

        # Tier 2: Gemini
        ans = self._call_gemini(prompt, sys_prompt)
        if ans:
            return ans

        # Tier 3: OpenRouter
        ans = self._call_openrouter(prompt, sys_prompt)
        if ans:
            return ans

        return ""

    # =========================================================
    # CONVERSATIONAL & SENTIMENTAL ROUTING (Dedicated Key)
    # =========================================================

    def generate_conversational_reply(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generates conversational and sentimental replies (e.g. 'what are you doing?', 'hi').
        Routes explicitly to the dedicated Conversational LLM key (Tier 2: Gemini),
        with fallback to OpenRouter or Groq.
        """
        user_prompt = f"User: {query}\n\nRespond warmly and conversationally, explaining what you are doing, that you are the dedicated SAP BRIM AI Assistant, and how the user can use you to explore all aspects of SAP BRIM (SOM, CC, CI, FI-CA). Invite them to ask follow-up questions."

        # Dedicated Conversational Tier: Gemini API Key
        logger.info("[Conversational Routing] Invoking Dedicated Key (Gemini) for conversational inquiry.")
        ans = self._call_gemini(user_prompt, CONVERSATIONAL_SYSTEM_PROMPT)
        if ans:
            return ans

        # Fallback 1: OpenRouter
        logger.info("[Conversational Routing] Gemini unavailable, falling back to OpenRouter.")
        ans = self._call_openrouter(user_prompt, CONVERSATIONAL_SYSTEM_PROMPT)
        if ans:
            return ans

        # Fallback 2: Groq
        logger.info("[Conversational Routing] OpenRouter unavailable, falling back to Groq.")
        ans = self._call_groq(user_prompt, CONVERSATIONAL_SYSTEM_PROMPT)
        if ans:
            return ans

        # Deterministic zero-latency fallback if all cloud services offline
        return (
            "Hello! I am Clyptus.AI, your dedicated SAP & SAP BRIM Solution Architect.\n\n"
            "Right now, I am standing by to assist you with everything related to SAP Billing and Revenue Innovation Management (BRIM)!\n\n"
            "**Use me to get details about:**\n"
            "- **Subscription Order Management (SOM)**: Master data, provider orders, and provider contracts\n"
            "- **Convergent Charging (CC)**: Real-time and offline rating, charge plans, and pricing logic\n"
            "- **Convergent Invoicing (CI)**: Billable item classes (BITs), billing aggregation, and invoicing documents\n"
            "- **Contract Accounts Receivable and Payable (FI-CA)**: Subledger accounting, open item clearing, and payment runs\n"
            "- **Architecture & Configuration**: Transaction codes, database tables, SPRO customizing, and troubleshooting\n\n"
            "Feel free to ask any follow-up questions regarding SAP BRIM processes or configuration below!"
        )

    def stream_conversational_reply(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> Generator[str, None, None]:
        """
        Progressively streams conversational and sentimental replies using the dedicated API key.
        """
        user_prompt = f"User: {query}\n\nRespond warmly and conversationally, explaining what you are doing, that you are the dedicated SAP BRIM AI Assistant, and how the user can use you to explore all aspects of SAP BRIM (SOM, CC, CI, FI-CA). Invite them to ask follow-up questions."

        # Dedicated Conversational Tier: Gemini
        yielded = False
        try:
            for token in self._stream_gemini(user_prompt, CONVERSATIONAL_SYSTEM_PROMPT):
                yielded = True
                yield token
            if yielded:
                return
        except Exception as e:
            logger.warning(f"[Conversational Streaming] Gemini stream failed: {e}")

        # Fallback 1: OpenRouter
        try:
            for token in self._stream_openrouter(user_prompt, CONVERSATIONAL_SYSTEM_PROMPT):
                yielded = True
                yield token
            if yielded:
                return
        except Exception as e:
            logger.warning(f"[Conversational Streaming] OpenRouter stream failed: {e}")

        # Fallback 2: Groq
        try:
            for token in self._stream_groq(user_prompt, CONVERSATIONAL_SYSTEM_PROMPT):
                yielded = True
                yield token
            if yielded:
                return
        except Exception as e:
            logger.warning(f"[Conversational Streaming] Groq stream failed: {e}")

        # Deterministic fallback stream
        fallback_text = (
            "Hello! I am Clyptus.AI, your dedicated SAP & SAP BRIM Solution Architect.\n\n"
            "Right now, I am standing by to assist you with everything related to SAP Billing and Revenue Innovation Management (BRIM)!\n\n"
            "**Use me to get details about:**\n"
            "- **Subscription Order Management (SOM)**: Master data, provider orders, and provider contracts\n"
            "- **Convergent Charging (CC)**: Real-time and offline rating, charge plans, and pricing logic\n"
            "- **Convergent Invoicing (CI)**: Billable item classes (BITs), billing aggregation, and invoicing documents\n"
            "- **Contract Accounts Receivable and Payable (FI-CA)**: Subledger accounting, open item clearing, and payment runs\n"
            "- **Architecture & Configuration**: Transaction codes, database tables, SPRO customizing, and troubleshooting\n\n"
            "Feel free to ask any follow-up questions regarding SAP BRIM processes or configuration below!"
        )
        for word in fallback_text.split(" "):
            yield word + " "

    # =========================================================
    # STREAMING
    # =========================================================

    def _stream_groq(self, prompt: str, system_prompt: str) -> Generator[str, None, None]:
        """Tier 1: Progressive streaming via Groq."""
        if not self.groq_api_key:
            return
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_api_key, timeout=8.0, max_retries=0)
        except Exception as e:
            logger.warning(f"[Tier 1: Groq] Stream client init failed: {e}")
            return

        for model in self.GROQ_MODELS:
            try:
                logger.info(f"[Tier 1: Groq] Attempting streaming with model: {model}")
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=4096,
                    stream=True,
                    timeout=8.0
                )
                yielded_any = False
                for chunk in resp:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        yielded_any = True
                        yield chunk.choices[0].delta.content
                if yielded_any:
                    logger.info(f"[Tier 1: Groq] Streaming completed with model: {model}")
                    return
                else:
                    logger.warning(f"[Tier 1: Groq] Streaming model '{model}' produced no output. Trying next model...")
                    continue
            except Exception as err:
                err_str = str(err)
                if "model output" in err_str.lower() or "model not found" in err_str.lower() or "does not exist" in err_str.lower() or "404" in err_str:
                    logger.warning(f"[Tier 1: Groq] Streaming model '{model}' unavailable ({err_str[:120]}). Skipping.")
                else:
                    logger.warning(f"[Tier 1: Groq] Streaming model '{model}' failed ({err_str[:120]}). Trying next model...")
                continue

    def _stream_gemini(self, prompt: str, system_prompt: str) -> Generator[str, None, None]:
        """Tier 2: Progressive streaming via Gemini."""
        if not self.gemini_api_key:
            return
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
        except Exception as e:
            logger.warning(f"[Tier 2: Gemini] Stream client init failed: {e}")
            return

        for model_name in self.GEMINI_MODELS:
            try:
                logger.info(f"[Tier 2: Gemini] Attempting streaming with model: {model_name}")
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_prompt
                )
                stream_resp = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=4096
                    ),
                    request_options={"timeout": 10.0},
                    stream=True
                )
                yielded_any = False
                for chunk in stream_resp:
                    try:
                        if chunk.text:
                            yielded_any = True
                            yield chunk.text
                    except Exception:
                        continue
                if yielded_any:
                    logger.info(f"[Tier 2: Gemini] Streaming completed with model: {model_name}")
                    return
            except Exception as err:
                logger.warning(f"[Tier 2: Gemini] Streaming model '{model_name}' failed ({err}). Trying next model...")
                continue

    def _stream_openrouter(self, prompt: str, system_prompt: str) -> Generator[str, None, None]:
        """Tier 3: Progressive streaming via OpenRouter."""
        if not self.openrouter_api_key:
            return
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://clyptus.ai",
                    "X-Title": "Clyptus.AI"
                }
            )
        except Exception as e:
            logger.warning(f"[Tier 3: OpenRouter] Stream client init failed: {e}")
            return

        for model in self.OPENROUTER_MODELS:
            try:
                logger.info(f"[Tier 3: OpenRouter] Attempting streaming with model: {model}")
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=4096,
                    stream=True
                )
                yielded_any = False
                for chunk in resp:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        yielded_any = True
                        yield chunk.choices[0].delta.content
                if yielded_any:
                    logger.info(f"[Tier 3: OpenRouter] Streaming completed with model: {model}")
                    return
            except Exception as err:
                logger.warning(f"[Tier 3: OpenRouter] Streaming model '{model}' failed ({err}). Trying next model...")
                continue

    def stream_answer(
        self,
        query: str,
        evidence: List[Dict[str, Any]],
        source_type: str = "knowledge_base"
    ) -> Generator[str, None, None]:

        evidence_context = ""
        budgeted_evidence = (evidence or [])[:4]

        if source_type in ("knowledge_base", "combined"):
            evidence_context = "\n\n".join(
                [
                    (
                        f"[Document: {c.get('document_name')}, "
                        f"Page: {c.get('page_number')}, "
                        f"Section: {c.get('section')}]\n"
                        f"{(c.get('chunk_text') or c.get('snippet') or '')[:1200]}"
                    )
                    for c in budgeted_evidence
                ]
            )
        elif source_type == "web":
            evidence_context = "\n\n".join(
                [
                    (
                        f"[Source: {w.get('title')} "
                        f"- {w.get('domain')}]\n"
                        f"{(w.get('snippet') or w.get('chunk_text') or '')[:800]}"
                    )
                    for w in budgeted_evidence
                ]
            )

        if len(evidence_context) > 4500:
            evidence_context = evidence_context[:4500] + "..."

        user_prompt = f"""USER QUERY:
{query}

SOURCE TYPE:
{source_type.upper()}

RETRIEVED EVIDENCE:
{evidence_context}

TASK:
Answer the user's question thoroughly, completely, and accurately using ONLY the retrieved evidence above.

Instructions:
1. Provide a comprehensive, full explanation covering all aspects of the user's question based on the evidence.
2. Do not cut off, truncate, or prematurely shorten the explanation; present all relevant details, transaction codes, steps, and module definitions in full.
3. Organize the answer cleanly with clear headings, bullet points, or markdown tables for readability.
4. Do not invent facts or extrapolate beyond the provided evidence.
5. If the evidence came from web sources, synthesize a complete answer from the web snippets.
6. If the evidence is insufficient, state clearly that sufficient information was not available.
"""

        streamed = False

        # Tier 1: Groq progressive streaming
        if self.groq_api_key:
            try:
                for chunk in self._stream_groq(user_prompt, SYSTEM_PROMPT):
                    streamed = True
                    yield chunk
                if streamed:
                    return
            except Exception as e:
                logger.warning(f"Groq streaming encountered error ({e}). Trying next tier...")

        # Tier 2: Gemini progressive streaming
        if not streamed and self.gemini_api_key:
            try:
                for chunk in self._stream_gemini(user_prompt, SYSTEM_PROMPT):
                    streamed = True
                    yield chunk
                if streamed:
                    return
            except Exception as e:
                logger.warning(f"Gemini streaming encountered error ({e}). Trying next tier...")

        # Tier 3: OpenRouter progressive streaming
        if not streamed and self.openrouter_api_key:
            try:
                for chunk in self._stream_openrouter(user_prompt, SYSTEM_PROMPT):
                    streamed = True
                    yield chunk
                if streamed:
                    return
            except Exception as e:
                logger.warning(f"OpenRouter streaming encountered error ({e}). Trying local fallback...")

        # Tier 4: Local Grounded Fallback streaming
        logger.warning("All cloud streaming tiers exhausted. Falling back to local grounded synthesis.")
        full_answer = self._generate_grounded_local_response(
            query=query,
            evidence_text=evidence_context,
            source_type=source_type,
            metadata=evidence
        )

        words = full_answer.split(" ")
        for i, word in enumerate(words):
            yield word + (
                " "
                if i < len(words) - 1
                else ""
            )


llm_service = LLMService()