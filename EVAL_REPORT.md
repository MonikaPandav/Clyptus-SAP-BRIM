# cClyptus.AI (SAP BRIM Knowledge Assistant) — Evaluation & RAG Engineering Report

## Executive Summary & Scope

**cClyptus.AI** is an enterprise-grade AI assistant specialized in SAP Billing and Revenue Innovation Management (BRIM). This document tracks quantitative accuracy, grounding, retrieval, and reliability metrics across development phases.

> [!IMPORTANT]
> **Evaluation Protocol & Constraints**:
> - Never invent SAP tables, programs, T-codes, or fields.
> - Tune strictly on the development split (`dev`). Held-out split (`heldout`) remains sealed until the final benchmark at Phase 6.
> - All new behaviors reside behind configuration flags (`backend/app/config.py`).
> - Zero modification permitted to the underlying SQLite corpus database (`sap_assistant.db`).
> - Metrics report sample sizes, explicit mathematical denominators, and **95% bootstrap confidence intervals** (1,000 resamples with replacement).

---

## Phase 0: Baseline & Evaluation Framework

### 1. Dataset Extension & Curation

The evaluation suite was expanded with structured annotations across two isolated splits:
- **`backend/evaluation/datasets/dev_questions.jsonl`**: Enriched from 104 to **132 questions** (40% hard questions added).
- **`backend/evaluation/datasets/heldout_questions.jsonl`**: Enriched to **96 questions** (held out, sealed).

Each entry contains:
1. `reference_answer`: Authoritative architectural answer compiled from official SAP BRIM manuals.
2. `must_cover_key_facts`: Explicit atomic factual propositions required for full credit.
3. `gold_chunk_ids`: Verified corpus chunk UUIDs supporting the factual claims.
4. `module_tags`: SAP BRIM modules covered (`SOM`, `CM`, `CC`, `CI`, `FI-CA`, `RAR`, or `General SAP BRIM`).
5. `category`: Archetype tag (`cross_module_scenario`, `false_premise`, `version_specific`, `out_of_scope_refusal`, `tcode_table`, `configuration`, `integration`, `conceptual`, `hallucination_trap`, `troubleshooting`).

#### Hard Question Additions (30+ New Scenarios)
- **Cross-Module Scenarios**: Multi-system lifecycle workflows (e.g., Telecom activation + recurring + counter usage; mid-cycle plan upgrades; unbilled BITs reconciliation).
- **False-Premise Inquiries**: Questions with incorrect technical premises (e.g., executing real-time rating inside SPRO; configuring `DFKKOP` in SAP SD; running billing engine in CRM).
- **Version-Specific Differences**: S/4HANA BRIM vs. ECC 6.0 Convergent Invoicing, Universal Journal (`ACDOCA`) integration, SOM vs. CRM 7.0 Provider Orders.
- **Out-of-Scope Refusals**: Strict guardrail tests demanding explicit refusal (e.g., non-SAP questions, Python web scrapers, confidential database credentials).

---

### 2. Regression Scenario: Telecom Multi-Rate Subscription (`hard_scenario_001`)

#### Scenario Specification
> **Prompt**: A telecom customer has a subscription with INR 799 monthly recurring fee, INR 299 one-time activation fee, and INR 5/GB for usage beyond a 150 GB allowance. During end-of-month processing, some customers were billed the activation fee twice, high-usage data was miscalculated, and the final invoices failed to post to FI-CA. Explain the root causes across SOM, CC, CI, and FI-CA, how to diagnose them, and how to remediate the billing run without duplicating already-billed charges.

#### Corpus-Verified Key Facts:
1. **Duplicate Billable Items**: Missing or non-unique source transaction ID (`SRCTRADOC`) / external reference causing repeated BIT generation in CI. Verified in `100  Ans.pdf` (p. 12, Chunk `f5a32e34-6819-47ce-8465-a2c42c71fc02`).
2. **Allowance Counter Reset & Unit Conversion**: Allowance counters not resetting on billing cycle anchor dates, or mismatch in megabyte-to-gigabyte unit conversion inside CC charged items. Verified in `SAP BRIM Press Book 2nd Edition` (p. 202, Chunk `35da0044-0cf2-4502-b96c-3a203afa5864`).
3. **FI-CA Posting Determination**: Missing contract account (`VKONT`), main and sub transaction determination, or unconfigured posting area `0010` in FI-CA. Verified in `BRIM_AC240_EN_Col16.pdf` (p. 82, Chunk `a12f4048-5399-4197-8888-80bfae3fa8bf`).
4. **Application Logs & Monitors**: Diagnosis via Application Log `SLG1`, Invoicing monitor `FPC1`/`FPC0`, and Billable Item Monitor `FKKBIX_BIT_MON`. Verified in `100 Ans 2.pdf` (p. 20, Chunk `6e21cff9-10fb-445f-8bb8-5ee49c03957a`).
5. **Reversal & Credit Memo Adjustment**: Reversal of duplicate billing documents via `FKKBIX_BILL_REV` or issuing credit memos for already-invoiced items. Verified in `SAP BRIM AI Architect.pdf` (p. 29, Chunk `baaaff3b-bf33-4545-ba80-9d943084d456`).
6. **Reprocessing Isolated Failed Items**: Invoicing run correction via `FKKINV_MASS` targeting only clarified/unprocessed items without re-running healthy accounts. Verified in `SAP BRIM Press Book 2nd Edition` (p. 218, Chunk `645ae433-4436-4718-9032-3c57650ced04`).

#### Baseline Run Result on `hard_scenario_001`:
- **Status**: `Abstention`
- **Key-Fact Coverage**: `0.00%` (0 / 6 facts covered)
- **LLM Judge Score**: `0.00`
- **Root Cause in Baseline**: Baseline system retrieves only $k=3$ chunks. For a question touching SOM, CC, CI, and FI-CA simultaneously, 3 chunks cannot represent all 4 functional modules. Lacking evidence across all modules, the grounding gate rejected the candidate answer and triggered an abstention.

---

### 3. Baseline Performance Metrics (`dev` split)

- **Evaluator**: `backend/evaluation/run_evaluation.py`
- **Dataset Split**: `dev`
- **Sample Size ($N$)**: 24 representative questions (stratified across 12 categories)
- **Bootstrap Resamples**: 1,000

| Metric | Baseline Mean | 95% Confidence Interval | Denominator / Basis |
| :--- | :---: | :---: | :--- |
| **Retrieval Recall@5** | **1.0000** | `[1.0000, 1.0000]` | Gold Chunks in Top 5 |
| **Retrieval Recall@10** | **1.0000** | `[1.0000, 1.0000]` | Gold Chunks in Top 10 |
| **Retrieval MRR** | **0.9792** | `[0.9375, 1.0000]` | First Gold Chunk Rank |
| **Key-Fact Coverage** | **0.2757** | `[0.1576, 0.4028]` | Must-Cover Required Facts ($N=64$ facts across questions) |
| **LLM-Judge Correctness** | **0.5041** | `[0.3833, 0.6261]` | Impartial Judge Score ($0.0 - 1.0$) |
| **Supported Claim Rate** | **0.6875** | `[0.5917, 0.7708]` | Fraction of Factual Claims with Evidence |
| **Unsupported Claim Rate** | **0.3125** | `[0.2250, 0.3958]` | Fraction of Factual Claims Lacking Evidence |
| **Identifier Precision** | **0.8188** | `[0.6874, 0.9219]` | Denominator: Total Technical IDs Claimed |
| **Identifier Recall** | **0.8194** | `[0.6667, 0.9583]` | Denominator: Total Expected Technical IDs |
| **Correct-Refusal Rate** | **0.9167** | `[0.7917, 1.0000]` | Denominator: Out-of-Scope / False Premise Questions |
| **Latency p50** | **12,045 ms** | — | Median End-to-End Latency |
| **Latency p95** | **39,215 ms** | — | 95th Percentile Latency (Fallback Retries) |
| **Estimated Cost / Query** | **$0.000601** | — | Commercial Rate Card (USD) |

---

### 4. Per-Category Performance Breakdown (Baseline)

| Category | Count | Recall@5 | MRR | Key-Fact Cov | LLM Judge | Unsupported Rate | ID Precision | Latency p50 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `conceptual` | 2 | 1.00 | 1.00 | 0.43 | 1.00 | 0.20 | 0.80 | 12,795 ms |
| `configuration` | 2 | 1.00 | 1.00 | 0.38 | 0.93 | 0.20 | 0.55 | 12,046 ms |
| `corpus_cannot_answer` | 2 | 1.00 | 1.00 | 0.17 | 0.42 | 0.60 | 1.00 | 38,268 ms |
| `cross_module_scenario` | 2 | 1.00 | 1.00 | 0.38 | 0.37 | 0.35 | 0.86 | 18,038 ms |
| `external_web_trigger` | 2 | 1.00 | 1.00 | 0.50 | 0.65 | 0.10 | 1.00 | 20,018 ms |
| `false_premise` | 2 | 1.00 | 1.00 | 0.54 | 0.60 | 0.45 | 0.81 | 39,215 ms |
| `hallucination_trap` | 2 | 1.00 | 1.00 | 0.33 | 0.53 | 0.35 | 1.00 | 1,184 ms |
| `integration` | 2 | 1.00 | 1.00 | 0.12 | 0.39 | 0.10 | 1.00 | 13,754 ms |
| `out_of_scope_refusal` | 2 | 1.00 | 1.00 | 0.00 | 0.30 | 0.60 | 1.00 | 94 ms |
| `tcode_table` | 2 | 1.00 | 0.75 | 0.46 | 0.40 | 0.35 | 0.25 | 30,996 ms |
| `troubleshooting` | 2 | 1.00 | 1.00 | 0.00 | 0.30 | 0.10 | 1.00 | 8,889 ms |
| `version_specific` | 2 | 1.00 | 1.00 | 0.00 | 0.17 | 0.35 | 0.56 | 52,599 ms |

---

### 5. Critical Baseline Observations & Bottlenecks

1. **Low Key-Fact Coverage (27.57%)**:
   - The primary limiting factor is **context starvation**: `settings.TOP_K = 3` limits prompt context to ~1,200 tokens. Complex questions require evidence spanning multiple documents.
   - For multi-part queries, simple single-pass retrieval retrieves chunks answering only the first clause of the prompt.
2. **Unsupported Claim Rate (31.25%)**:
   - The generator attempts to fill gaps when retrieved context lacks specific details, introducing ungrounded assertions that the grounding gate then struggles to reconcile.
3. **Identifier Precision Flaws in Table/T-Code Questions (25.0%)**:
   - When asked for specific configuration tables, the model frequently hallucinates plausible-sounding SAP prefixes (e.g. `/1FE/` variations not in the corpus).
4. **Latency Spikes on Refusal & Retry**:
   - In cases with partial grounding failures, multiple retries and LLM failover attempts cause p95 latency to reach 39.2 seconds.
