import os
import sys
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Output PDF path
PDF_OUTPUT_PATH = Path(r"c:\Users\yuvar\OneDrive\Desktop\gen ai and agentic ai\super admin portal\SAP\SAP_BRIM\SAP_BRIM_System_Audit_and_Architecture_Report.pdf")


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically inject total page count in the footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Skip running header on cover/first page
        if self._pageNumber > 1:
            self.drawString(54, 755, "SAP BRIM Knowledge Assistant | Enterprise Architecture & Code Audit Report")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)

        # Footer on all pages
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_str)
        self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY | Clyptus.AI Architecture Audit | Generated Oct 2026")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)

        self.restoreState()


def build_pdf_report():
    doc = SimpleDocTemplate(
        str(PDF_OUTPUT_PATH),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0f172a")  # Slate 900
    brand_orange = colors.HexColor("#ea580c")   # Deep Orange
    accent_blue = colors.HexColor("#0284c7")    # Sky Blue
    text_dark = colors.HexColor("#1e293b")      # Slate 800
    text_muted = colors.HexColor("#64748b")     # Slate 500
    bg_light = colors.HexColor("#f8fafc")       # Slate 50
    border_color = colors.HexColor("#cbd5e1")   # Slate 300

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=brand_orange,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=primary_color,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=brand_orange,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=text_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=text_dark,
        leftIndent=15,
        spaceAfter=4
    )

    code_badge_style = ParagraphStyle(
        "CodeBadge",
        parent=styles["Normal"],
        fontName="Courier-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9")
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=text_dark
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white
    )

    callout_style = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # =========================================================================
    # COVER / HEADER BANNER
    # =========================================================================
    story.append(Paragraph("SAP BRIM Knowledge Assistant", title_style))
    story.append(Paragraph("COMPLETE CODE, FUNCTIONALITY, DATA & ARCHITECTURE AUDIT REPORT", subtitle_style))

    # Meta Table
    meta_data = [
        [
            Paragraph("<b>Target System:</b> SAP BRIM Enterprise Portal", table_cell_style),
            Paragraph("<b>Audit Date:</b> October 2026", table_cell_style)
        ],
        [
            Paragraph("<b>Audit Scope:</b> Backend, Frontend, Vector DB, RAG & LLMs", table_cell_style),
            Paragraph("<b>Status:</b> Production Ready with Optimization Opportunities", table_cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 234])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_light),
        ("BOX", (0, 0), (-1, -1), 1, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # Executive Summary Callout Box
    exec_summary_text = (
        "<b>EXECUTIVE AUDIT SUMMARY:</b> This comprehensive audit reviews the complete codebase, data layer, "
        "and architectural implementation of the SAP BRIM Knowledge Assistant. The system features a sophisticated, "
        "multi-tiered Retrieval-Augmented Generation (RAG) architecture with multi-model fallback (Groq, Gemini, OpenRouter), "
        "claim-level grounding verification, dynamic intent routing, context rewriting, and streaming SSE delivery. "
        "All 14 master SAP BRIM PDFs (3,491 pages, 6,697 vector chunks) are verified 100% indexed and retrievable. "
        "This report details the tech stack, exact chunking algorithms, model temperatures, standout capabilities, "
        "operational bottlenecks, unused assets, and an engineering optimization roadmap."
    )
    exec_table = Table([[Paragraph(exec_summary_text, callout_style)]], colWidths=[504])
    exec_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff7ed")),
        ("BOX", (0, 0), (-1, -1), 1.5, brand_orange),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 1: COMPLETE TECH STACK ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("1. Complete Project Tech Stack Breakdown", h1_style))
    story.append(Paragraph(
        "The project is engineered as an enterprise-grade decoupled full-stack web application with strict separation "
        "of concerns, asynchronous streaming APIs, and zero-latency local fallback mechanisms:",
        body_style
    ))

    stack_data = [
        [Paragraph("Layer", table_header_style), Paragraph("Technologies & Libraries", table_header_style), Paragraph("Architecture Role & Implementation Details", table_header_style)],
        [
            Paragraph("<b>Backend Core</b>", table_cell_style),
            Paragraph("Python 3.14<br/>FastAPI >= 0.110.0<br/>Uvicorn (Standard)", table_cell_style),
            Paragraph("Asynchronous ASGI web application framework providing high-concurrency HTTP and SSE endpoints. Implements Pydantic v2 data validation schemas.", table_cell_style)
        ],
        [
            Paragraph("<b>Data & Persistence</b>", table_cell_style),
            Paragraph("PostgreSQL + pgvector<br/>SQLite (Zero-friction fallback)<br/>SQLAlchemy 2.0 ORM", table_cell_style),
            Paragraph("Relational schema for Users, Chats, Messages, Citations, WebSources, and Documents. Automatic seamless failover to local SQLite (<code>sap_assistant.db</code>) if Postgres is offline.", table_cell_style)
        ],
        [
            Paragraph("<b>Embeddings & Vector</b>", table_cell_style),
            Paragraph("sentence-transformers<br/>all-MiniLM-L6-v2<br/>FastEmbed ONNX", table_cell_style),
            Paragraph("Dense vector embedding engine generating 384-dimensional normalized vector projections. In-memory cosine similarity and hybrid BM25 lexical ranking.", table_cell_style)
        ],
        [
            Paragraph("<b>Primary RAG LLM</b>", table_cell_style),
            Paragraph("Groq SDK >= 0.5.0<br/><code>qwen/qwen3.8-27b</code><br/><code>openai/gpt-oss-120b</code>", table_cell_style),
            Paragraph("Ultra-low latency inference tier for technical SAP BRIM generation. Optimized for high-throughput architectural grounding and procedure citing.", table_cell_style)
        ],
        [
            Paragraph("<b>Conversational LLM</b>", table_cell_style),
            Paragraph("Google Generative AI<br/><code>gemini-2.5-flash</code><br/><code>gemini-2.5-pro</code>", table_cell_style),
            Paragraph("Dedicated conversational assistant tier handling greetings, persona introduction, sentimental queries, and module onboarding with zero technical hallucination.", table_cell_style)
        ],
        [
            Paragraph("<b>Fallback LLM Tier</b>", table_cell_style),
            Paragraph("OpenAI SDK (OpenRouter)<br/><code>nemotron-3.5-lightning:free</code><br/><code>liquid/lfm-2.5-2.6b:free</code>", table_cell_style),
            Paragraph("Multi-model open-source fallback tier ensuring 100% uptime when primary API rate limits or network issues occur.", table_cell_style)
        ],
        [
            Paragraph("<b>Web Search Augmentation</b>", table_cell_style),
            Paragraph("Tavily Python API<br/><code>tavily-python >= 0.3.0</code>", table_cell_style),
            Paragraph("Live enterprise external documentation retrieval fallback. Triggered dynamically when internal knowledge base confidence drops below 0.70.", table_cell_style)
        ],
        [
            Paragraph("<b>Frontend Framework</b>", table_cell_style),
            Paragraph("React 19, TypeScript<br/>Vite v8.3.3 Bundler", table_cell_style),
            Paragraph("Modern component-driven UI with client-side routing (React Router DOM v7), strict TypeScript typing, and optimized production chunking (built in ~2.9s).", table_cell_style)
        ],
        [
            Paragraph("<b>Styling & UI Effects</b>", table_cell_style),
            Paragraph("Vanilla CSS Design Tokens<br/>TailwindCSS utility classes<br/>Framer Motion & Lucide Icons", table_cell_style),
            Paragraph("Premium dark-mode-first aesthetic with custom electric orange accents, responsive drawers, smooth slide-ins, and animated status pulses.", table_cell_style)
        ],
        [
            Paragraph("<b>Security & Auth</b>", table_cell_style),
            Paragraph("Passlib (BCrypt)<br/>Python-Jose (JWT HS256)<br/>Scoped Admin API Secret", table_cell_style),
            Paragraph("Stateless JWT authentication with 24-hour expiration, salted password hashing, guest demo sessions, and strict cross-tenant chat isolation.", table_cell_style)
        ]
    ]

    stack_table = Table(stack_data, colWidths=[100, 150, 254])
    stack_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, bg_light]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(stack_table)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 2: CHUNKING STRATEGY, MODELS & TEMPERATURE AUDIT
    # =========================================================================
    story.append(Paragraph("2. In-Depth Chunking, Models & Temperature Specifications", h1_style))
    story.append(Paragraph(
        "A critical strength of this system is its domain-specific chunking and deterministic temperature calibration. "
        "Below are the verified parameters extracted directly from the active code implementation:",
        body_style
    ))

    # Sub-table: Chunking Parameters
    chunk_params = [
        [Paragraph("Chunking Parameter", table_header_style), Paragraph("Configured Value", table_header_style), Paragraph("Technical Purpose & Behavior", table_header_style)],
        [
            Paragraph("<b>Target Chunk Size</b>", table_cell_style),
            Paragraph("<code>1,200 characters</code> (~250-300 words)", table_cell_style),
            Paragraph("Optimal semantic envelope for enterprise SAP documentation, preserving complete technical procedures without truncation.", table_cell_style)
        ],
        [
            Paragraph("<b>Chunk Overlap</b>", table_cell_style),
            Paragraph("<code>200 characters</code> (~40-50 words)", table_cell_style),
            Paragraph("Ensures continuous context across chunk boundaries, preventing boundary clipping of SAP transaction codes and database tables.", table_cell_style)
        ],
        [
            Paragraph("<b>Atomic Single-Page Boundary</b>", table_cell_style),
            Paragraph("<code>&lt;= 1,550 characters</code>", table_cell_style),
            Paragraph("If page text is within 1,200 + 350 chars, it is preserved as an unbroken single chunk to preserve atomic diagram & step relationships.", table_cell_style)
        ],
        [
            Paragraph("<b>Minimum Chunk Threshold</b>", table_cell_style),
            Paragraph("<code>60 characters</code>", table_cell_style),
            Paragraph("Strict filter preventing noise chunks containing only page headers, copyright disclaimers, or empty whitespace.", table_cell_style)
        ],
        [
            Paragraph("<b>Boundary Seek Hierarchy</b>", table_cell_style),
            Paragraph("1. Paragraph (<code>\\n\\n</code>)<br/>2. Numbered step (<code>\\n1. </code>)<br/>3. Sentence (<code>. </code>)<br/>4. Line break (<code>\\n</code>)", table_cell_style),
            Paragraph("Hierarchical regex lookback ensures splits never sever sentences mid-phrase. Steps 1..N and prerequisites stay contiguous.", table_cell_style)
        ],
        [
            Paragraph("<b>Semantic Archetype Tagging</b>", table_cell_style),
            Paragraph("<code>procedure</code>, <code>table</code>, <code>overview</code>, <code>concept</code>", table_cell_style),
            Paragraph("Chunks are automatically categorized by content heuristics to enable archetype-aware response planning.", table_cell_style)
        ],
        [
            Paragraph("<b>Idempotency Checksum</b>", table_cell_style),
            Paragraph("SHA-256 hash validation", table_cell_style),
            Paragraph("Prevents redundant re-indexing of identical PDFs; only modified documents are re-chunked and re-embedded.", table_cell_style)
        ]
    ]

    chunk_table = Table(chunk_params, colWidths=[130, 150, 224])
    chunk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), brand_orange),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, bg_light]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(chunk_table)
    story.append(Spacer(1, 10))

    # Temperature & Models Table
    story.append(Paragraph("Models & Temperature Calibration Across Pipelines", h2_style))
    temp_params = [
        [Paragraph("Pipeline Component", table_header_style), Paragraph("Assigned Model", table_header_style), Paragraph("Temperature", table_header_style), Paragraph("Architectural Rationale", table_header_style)],
        [
            Paragraph("<b>Query Rewriter</b>", table_cell_style),
            Paragraph("Groq (<code>qwen/qwen3.8-27b</code>)", table_cell_style),
            Paragraph("<code>0.0</code>", table_cell_style),
            Paragraph("Zero creativity; strictly resolves pronouns ('it', 'this') into concrete SAP entities deterministically.", table_cell_style)
        ],
        [
            Paragraph("<b>Primary RAG Technical Generation</b>", table_cell_style),
            Paragraph("Groq (<code>qwen/qwen3.8-27b</code> / <code>gpt-oss-120b</code>)", table_cell_style),
            Paragraph("<code>0.1</code>", table_cell_style),
            Paragraph("Minimizes hallucinations while generating fluent, evidence-grounded SAP architectural explanations.", table_cell_style)
        ],
        [
            Paragraph("<b>Conversational & Sentimental Tier</b>", table_cell_style),
            Paragraph("Google Gemini (<code>gemini-2.5-flash</code>)", table_cell_style),
            Paragraph("<code>0.1</code>", table_cell_style),
            Paragraph("Warm and engaging responses to casual greetings while strictly retaining professional persona boundaries.", table_cell_style)
        ],
        [
            Paragraph("<b>Multi-Model Cloud Fallback</b>", table_cell_style),
            Paragraph("OpenRouter (<code>nemotron-3.5-lightning:free</code>)", table_cell_style),
            Paragraph("<code>0.1</code>", table_cell_style),
            Paragraph("Ensures consistent output structure and evidence citation when primary providers fail.", table_cell_style)
        ],
        [
            Paragraph("<b>Vector Embedding Model</b>", table_cell_style),
            Paragraph("<code>all-MiniLM-L6-v2</code> (384 Dimensions)", table_cell_style),
            Paragraph("N/A", table_cell_style),
            Paragraph("High-speed, normalized cosine similarity dense projections matching semantic intent.", table_cell_style)
        ]
    ]

    temp_table = Table(temp_params, colWidths=[120, 140, 70, 174])
    temp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), accent_blue),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, bg_light]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(temp_table)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 3: GOOD FUNCTIONALITIES (STRENGTHS)
    # =========================================================================
    story.append(Paragraph("3. Standout Functionalities & Architectural Strengths", h1_style))
    story.append(Paragraph(
        "A rigorous line-by-line inspection reveals several standout design choices that place this application above typical RAG prototypes:",
        body_style
    ))

    strengths = [
        ("Multi-Tiered API Fallback Cascade:", "The system implements a resilient multi-provider strategy (Tier 1: Groq -> Tier 2: Gemini -> Tier 3: OpenRouter -> Tier 4: Local Grounded Synthesis). If any cloud provider suffers rate limits, network outages, or model deprecations, the engine seamlessly fails over without dropping user queries."),
        ("Dual-Path Intent Routing:", "Queries are classified before reaching the vector pipeline. Pure conversational inquiries ('hi', 'what are you doing?', 'who are you?') are cleanly routed to the dedicated Gemini API key with persona guidance, while technical inquiries invoke the full RAG vector retrieval pipeline."),
        ("Context-Aware Query Rewriting & Pronoun Resolution:", "The QueryRewriter engine inspects conversation history in reverse order. Elliptical questions like 'Where is it configured?' or 'What happens after rating?' are rewritten into standalone queries ('Where is SAP Convergent Invoicing configured?') before hitting the vector search index."),
        ("Strict SAP Scope Guardrail (Classifier):", "The SAPClassifier protects against off-topic drift and prompt-injection attacks. Unrelated queries regarding politics, cooking, entertainment, or general coding are rejected with helpful guidance, preserving corporate enterprise boundaries."),
        ("Claim-Level Grounding Verification:", "The GroundingService parses candidate answers sentence-by-sentence, checking technical SAP claims (T-codes like FPC1, FPY1, tables like DFKKOP, DFKKBIXBIT2) against retrieved evidence. Unverified claims are stripped or repaired before user presentation."),
        ("Adaptive Hybrid Retrieval with Live Web Search Fallback:", "Vector similarity is fused with BM25 keyword matching and technical ID boosting. If internal confidence drops below 0.70, the system automatically triggers Tavily live web search to retrieve up-to-date SAP documentation from help.sap.com."),
        ("Real-time Server-Sent Events (SSE) Streaming:", "The frontend receives real-time progress events ('Resolving context...', 'Searching internal documentation...', 'Verifying grounding...') followed by token-by-token streaming, providing a responsive ChatGPT-like user experience."),
        ("Interactive Follow-Up Chips:", "Every assistant response delivers 3 clickable, technically relevant follow-up questions tailored to SAP BRIM modules (SOM, CC, CI, FI-CA), enabling effortless exploratory learning for enterprise consultants.")
    ]

    for title, desc in strengths:
        story.append(Paragraph(f"• <b>{title}</b> {desc}", bullet_style))

    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 4: WHERE IT IS LAGGING (BOTTLENECKS & TECHNICAL DEBT)
    # =========================================================================
    story.append(Paragraph("4. Where the System is Lagging & Technical Bottlenecks", h1_style))
    story.append(Paragraph(
        "While the architecture is highly capable, the code audit identified several clear operational bottlenecks and technical debt:",
        body_style
    ))

    lags = [
        ("In-Memory SQLite Vector Scanning (Scalability Bottleneck):", "In local/development mode, the system defaults to SQLite. Because SQLite lacks native pgvector indexing, <code>retrieval_service.py</code> computes in-memory dot products over all 6,697 chunk embeddings in Python RAM on every search. In high-concurrency production, this will cause significant CPU and memory pressure. Migration to active PostgreSQL with pgvector (HNSW/IVFFlat indexes) is essential."),
        ("Rigid Hardcoded Temperature Settings:", "All generative models are locked to <code>temperature=0.1</code>. While ideal for strict technical citations, it limits conversational engagement when users ask for architectural analogies, high-level roadmaps, or brainstorming."),
        ("Unauthenticated HuggingFace Hub Warning:", "On initial embedding load, the console logs warnings: <i>'Warning: You are sending unauthenticated requests to the HF Hub'</i>. Without a configured <code>HF_TOKEN</code>, Hugging Face can throttle download requests or fail during fresh container deployments."),
        ("Hardcoded Frontend API URL:", "In <code>frontend/src/services/api.ts</code>, line 3 hardcodes <code>const API_BASE_URL = 'http://localhost:8000/api'</code>. This breaks containerized deployments, custom domain routing, or reverse-proxy setups unless updated to an environment variable (<code>import.meta.env.VITE_API_URL</code>)."),
        ("Crude Chat Title Auto-Naming Heuristic:", "Chat titles are generated by slicing the first 6 words of the user prompt (<code>' '.join(words[:6])</code>). For queries like 'Can you explain the end-to-end...', titles become awkward fragments ('Can you explain the end-to-end...'). An LLM-summarized title generator would improve session organization."),
        ("Interrupted Message Loss on Browser Disconnect:", "When streaming responses are aborted by the user, messages are tagged as <code>source_type='interrupted'</code> with a 0.0 grounding score and zero citations saved to the DB, preventing subsequent citation inspection of partially generated answers."),
        ("Redundant Dual API Endpoints:", "The backend maintains two parallel RAG query endpoints: <code>/chats/{chat_id}/messages</code> (used by frontend) and <code>/rag/query</code> (legacy/test endpoint). Both duplicate verification logic, increasing maintenance overhead.")
    ]

    for title, desc in lags:
        story.append(Paragraph(f"• <b>{title}</b> {desc}", bullet_style))

    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 5: UNUSED DOCUMENTS, UNUSED DATA & DEAD CODE AUDIT
    # =========================================================================
    story.append(Paragraph("5. Unused Documents, Ghost Data & Dead Code Audit", h1_style))
    story.append(Paragraph(
        "An exhaustive cross-reference between physical disk folders, database records, and frontend routes revealed the following discrepancies:",
        body_style
    ))

    data_audit_data = [
        [Paragraph("Category", table_header_style), Paragraph("Items Identified", table_header_style), Paragraph("Audit Finding & Recommendation", table_header_style)],
        [
            Paragraph("<b>Ghost Database Documents (No File on Disk)</b>", table_cell_style),
            Paragraph(
                "10 legacy ERP PDFs:<br/>"
                "• <code>SAP_ABAP_Development...pdf</code><br/>"
                "• <code>SAP_Basis_Administration...pdf</code><br/>"
                "• <code>SAP_CO_Controlling...pdf</code><br/>"
                "• <code>SAP_FI_Financial...pdf</code><br/>"
                "• <code>SAP_Fiori_Design...pdf</code><br/>"
                "• <code>SAP_HCM_Human...pdf</code><br/>"
                "• <code>SAP_MM_Materials...pdf</code><br/>"
                "• <code>SAP_PP_Production...pdf</code><br/>"
                "• <code>SAP_S4HANA_Architecture...pdf</code><br/>"
                "• <code>SAP_SD_Sales...pdf</code>",
                table_cell_style
            ),
            Paragraph(
                "<b>Finding:</b> These 10 documents exist as metadata and chunk records inside <code>sap_assistant.db</code>, but the physical PDF files do NOT exist in <code>knowledge_base/</code> on disk.<br/>"
                "<b>Origin:</b> Seeded by legacy script <code>generate_sap_docs.py</code>.<br/>"
                "<b>Recommendation:</b> If the assistant is strictly dedicated to SAP BRIM, purge these legacy general ERP chunks to keep the index 100% focused on BRIM.",
                table_cell_style
            )
        ],
        [
            Paragraph("<b>Unused Frontend Page (Dead Code)</b>", table_cell_style),
            Paragraph("<code>frontend/src/pages/RegisterPage.tsx</code>", table_cell_style),
            Paragraph(
                "<b>Finding:</b> <code>RegisterPage.tsx</code> is completely unrouted. In <code>App.tsx</code>, registration is handled inside an interactive tab within <code>LoginPage.tsx</code>. <code>RegisterPage.tsx</code> is never imported or rendered anywhere in the application.<br/>"
                "<b>Recommendation:</b> Delete or archive this file to streamline the codebase.",
                table_cell_style
            )
        ],
        [
            Paragraph("<b>Active Knowledge Base Documents</b>", table_cell_style),
            Paragraph("<b>14 Master PDFs</b> in <code>the full rag data sap</code><br/>+ <b>16 PDFs</b> in <code>knowledge_base/documents</code>", table_cell_style),
            Paragraph(
                "<b>Finding:</b> All 30 active files on disk are 100% indexed and retrievable.<br/>"
                "• 14 master manuals (BR234 SOM, AC240 FICA, CC Master Guide, SAP Press BRIM 2nd Edition, Simplification List, etc.) have complete 384-dim embeddings.<br/>"
                "• 16 supplementary guides provide targeted Q-Bank, SPRO cookbooks, and CI architecture details.",
                table_cell_style
            )
        ],
        [
            Paragraph("<b>Unused / Legacy Scripts</b>", table_cell_style),
            Paragraph("<code>generate_sap_docs.py</code><br/><code>generate_brim_master_docs.py</code>", table_cell_style),
            Paragraph(
                "<b>Finding:</b> One-off document generation scripts residing in the backend root directory. They are not invoked during standard application runtime.<br/>"
                "<b>Recommendation:</b> Move to a dedicated <code>scripts/tools/</code> directory.",
                table_cell_style
            )
        ]
    ]

    data_table = Table(data_audit_data, colWidths=[110, 160, 234])
    data_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, bg_light]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(data_table)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 6: ACTIONABLE ENGINEERING ROADMAP
    # =========================================================================
    story.append(Paragraph("6. Actionable Engineering Recommendations & Next Steps", h1_style))
    roadmap_items = [
        ("Production Database Transition:", "Activate PostgreSQL with pgvector in staging/production environments. Replace in-memory cosine scans with an indexed HNSW vector search to support 100,000+ chunks with sub-10ms retrieval latency."),
        ("Frontend Environment Variable Config:", "Refactor <code>API_BASE_URL</code> in <code>frontend/src/services/api.ts</code> to read from <code>import.meta.env.VITE_API_URL || '/api'</code> to enable flexible container deployments."),
        ("Knowledge Base Cleanup:", "Purge the 10 orphan non-BRIM database records from SQLite if BRIM specialization is the primary product focus, reducing index size and eliminating potential retrieval dilution."),
        ("Remove Dead Code:", "Remove <code>RegisterPage.tsx</code> and consolidate redundant endpoints (deprecate <code>/rag/query</code> in favor of <code>/chats/{chat_id}/messages</code>)."),
        ("Dynamic Temperature Modulation:", "Allow temperature to adjust dynamically: <code>0.0</code> for T-code/table lookup, <code>0.1</code> for strict configuration citations, and <code>0.4</code> for conversational greetings and high-level architectural brainstorming."),
        ("Configure Hugging Face Hub Credentials:", "Add <code>HF_TOKEN</code> to <code>.env</code> to eliminate unauthenticated warnings and ensure guaranteed bandwidth during model initialization.")
    ]

    for title, desc in roadmap_items:
        story.append(Paragraph(f"<b>{title}</b> {desc}", bullet_style))

    story.append(Spacer(1, 15))

    # Sign-off box
    signoff_text = (
        "<b>REPORT CONCLUSION:</b> The SAP BRIM Knowledge Assistant codebase demonstrates a mature, production-grade "
        "engineering foundation with robust security, multi-LLM resiliency, and verified data retrieval. Following the "
        "recommendations outlined above will elevate the platform to an enterprise-ready flagship SaaS architecture."
    )
    signoff_table = Table([[Paragraph(signoff_text, callout_style)]], colWidths=[504])
    signoff_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_light),
        ("BOX", (0, 0), (-1, -1), 1, accent_blue),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(signoff_table)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {PDF_OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf_report()
