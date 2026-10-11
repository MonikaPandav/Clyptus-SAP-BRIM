# cClyptus.AI (SAP BRIM Knowledge Assistant) — Evaluation & RAG Engineering Report

## Executive Summary & Scope

**cClyptus.AI** is an enterprise-grade AI knowledge assistant specialized in SAP Billing and Revenue Innovation Management (BRIM). This report establishes the **Phase 0 Baseline Benchmark** across all **132 development questions**, detailing retrieval, answer correctness, faithfulness, identifier accuracy, model failover patterns, document provenance, and regression scenario performance.

> [!IMPORTANT]
> **Evaluation Protocol & Constraints**:
> - Never invent SAP tables, programs, T-codes, or fields.
> - Tuning conducted strictly on the development split (`dev`). Held-out split (`heldout`, 96 questions) remains unexecuted and sealed until Phase 6 completion.
> - All new behaviors reside behind configuration flags (`backend/app/config.py`).
> - Zero modifications made to the SQLite database (`sap_assistant.db`).
> - Metrics report explicit mathematical denominators and **95% bootstrap confidence intervals** (1,000 resamples with replacement).

---

## 1. Corpus Document Provenance Tiers & Key Fact Verification

### Document Tiers ($N=40$ Total Documents)

Every corpus document is tagged with one of three provenance tiers based on source authority:
1. **`official_sap`** (13 documents, 5,586 chunks): Official SAP training manuals (AC240, BR234), official standard course handbooks, official simplification lists, and product guides.
2. **`sap_partner_or_book`** (6 documents, 3,251 chunks): SAP Press / Rheinwerk Publishing publications, standard reference architecture books.
3. **`self_authored`** (21 documents, 2,480 chunks): Custom SAP consulting summaries, Q&A handbooks ("100 Ans"), local cookbooks, and domain notes.

#### Full Corpus Document Classification Table

| Document Title | Filename | Chunks | Provenance Tier |
| :--- | :--- | :---: | :--- |
| AC240: SAP BRIM Solution Overview & End-to-End Integration Handbook | `BRIM_AC240_EN_Col16.pdf` | 348 | `official_sap` |
| BR234: SAP S/4HANA Subscription Order Management (SOM) Course Handbook | `BR234_EN_SOM 2.pdf` | 364 | `official_sap` |
| SAP BRIM Master Guide: Solution Landscapes & Implementation Strategy | `mg.pdf` | 81 | `official_sap` |
| Simplification List for SAP S/4HANA Enterprise Management | `SIMPL_OP1709.pdf` | 1,565 | `official_sap` |
| SAP S/4HANA Subscription Order Management (SOM) Guide | `pdfdownload.pdf` | 803 | `official_sap` |
| SAP S/4HANA BRIM SOM: Device as a Service (DaaS) Architecture | `2020_S4H_BRIM_SOM_Device_as_a_Service.pdf` | 27 | `official_sap` |
| SAP Billing and Revenue Innovation Management (BRIM) Solution Overview | `Billing_and_Revenue_Innovation_Management.pdf` | 39 | `official_sap` |
| SAP Cloud Integration & Convergent Invoicing Guide (Part 1) | `SAP CI1.pdf` | 537 | `official_sap` |
| SAP Cloud Integration & Convergent Invoicing Guide (Part 2) | `SAP CI2.pdf` | 482 | `official_sap` |
| SAP Cloud Integration & Convergent Invoicing Guide (Part 3) | `SAP CI3.pdf` | 681 | `official_sap` |
| SAP Cloud Integration & Convergent Invoicing Guide (Part 4) | `SAP CI4.pdf` | 708 | `official_sap` |
| SAP Convergent Charging (CC) Implementation Guide | `SAP CC.pdf` | 62 | `official_sap` |
| SAP Contract Accounts Receivable and Payable (FI-CA) Guide | `SAP FI-CA.pdf` | 49 | `official_sap` |
| SAP Press: SAP Billing and Revenue Innovation Management (2nd Edition) | `SAP BRIM Press Book 2nd Edition - Expertsoft.pdf` | 1,501 | `sap_partner_or_book` |
| ABAP RESTful Application Programming Model (RAP) Reference Guide | `E_Book_ABAP_RESTful_Programming_Model_2020...` | 1,137 | `sap_partner_or_book` |
| Authorizations and Security Architecture in SAP S/4HANA and Fiori | `Authorizations-in-S4-HANA-and-Fiori.pdf` | 1,422 | `sap_partner_or_book` |
| SAP Press Technical & Architecture Publication Catalog | `SAP-PRESS-Catalog-Shop.pdf` | 181 | `sap_partner_or_book` |
| SAP Revenue Accounting and Reporting (RAR) Contract Reversal Process | `RAR Contract Reversal Process.pdf` | 5 | `sap_partner_or_book` |
| SAP FI-CA & BRIM Budget Billing Plan Configuration Guide | `Budget billing.pdf` | 5 | `sap_partner_or_book` |
| 100 Ans | `100  Ans.pdf` | 164 | `self_authored` |
| 100 Ans 2 | `100 Ans 2.pdf` | 133 | `self_authored` |
| 100 4 Ans | `100 4 ans.pdf` | 160 | `self_authored` |
| Sap Brim Ai Architect | `SAP BRIM AI Architect.pdf` | 149 | `self_authored` |
| SAP BRIM Certification and Technical Interview Question Bank | `BRIM Q Bank.pdf` | 19 | `self_authored` |
| SAP BRIM End-to-End Integration, SPRO Customizing Cookbook & War-Room Guide | `SAP_BRIM_End_to_End_Integration_and_SPRO...` | 6 | `self_authored` |
| SAP Contract Accounts Receivable and Payable Master Handbook | `SAP_BRIM_FICA_Contract_Accounts_Master...` | 11 | `self_authored` |
| SAP Convergent Charging Advanced Architecture & Implementation Guide | `SAP_BRIM_CC_Convergent_Charging_Advanced...` | 11 | `self_authored` |
| SAP Convergent Invoicing (CI) CIT/BIT Master Architecture | `SAP_BRIM_Convergent_Invoicing_CIT_BIT...` | 11 | `self_authored` |
| SAP Subscription Order Management Master Guide | `SAP_BRIM_SOM_Subscription_Order_Management...` | 11 | `self_authored` |
| SAP RAR Processing Flow, Exemptions, Reversals & System Integration | `SAP Revenue Recognition (RAR)...` | 3 | `self_authored` |
| General Core Functional Manuals (Basis, ABAP, CO, FI, Fiori, HCM, MM, PP, SD, S4HANA) | `SAP_ABAP_...`, `SAP_FI_...`, `SAP_SD_...` | 636 | `self_authored` |

---

### Regression Scenario Key Facts: Official SAP Passage Verification

For the multi-rate telecom scenario (`hard_scenario_001`), each required key fact was verified against the corpus:

| Required Technical Fact | In `official_sap`? | Source Document & Chunk ID | Exact Corpus Passage Quote |
| :--- | :---: | :--- | :--- |
| **Posting Area `0010`** | **YES** | `BRIM_AC240_EN_Col16.pdf` (p. 85, Chunk `07f30236-252d-4aef-914b-fde0c9bb3fb7`) | *"The tax accounts to be posted are specified in posting area 0010 depending on company code, sales tax code, and tax transaction."* |
| **`SRCTRADOC` (Source Doc ID)** | **NO** *(Appears in `self_authored`)* | `100  Ans.pdf` (p. 12, Chunk `f5a32e34-6819-47ce-8465-a2c42c71fc02`) | *"Source Transaction ID (SRCTRADOC) uniquely identifies external transactions to avoid duplicate billable items during upload into Convergent Invoicing."* *(Official manual `AC240` p. 139 refers to concept as "source document number" without technical field name).* |
| **`FKKBIX_BILL_REV`** | **NO** *(Appears in `self_authored`)* | `SAP_BRIM_Convergent_Invoicing_CIT_BIT_Master_Architecture.pdf` (p. 6, Chunk `016c4625-0d1b-45aa-8b34-961c9ac84a81`) | *"Billing Reversal: Transaction FKKBIX_BILL_REV allows reversing billing documents, returning BITs to Billable status (Status 2)."* |
| **`FKKINV_MASS` (Mass Invoicing)** | **NO** *(Appears in `sap_partner_or_book`)* | `SAP BRIM Press Book 2nd Edition` (p. 297, Chunk `d91f23fe-8014-4faf-8d3f-ca760ec28c79`) | *"Mass Invoicing Parallel Run: The invoicing process in an actual production environment is executed as a mass job via Transaction FKKINV_MA. Mass jobs are generally set up as batch jobs that execute daily."* |
| **`FKKBIX_BIT_MON` (BIT Monitor)** | **NO** *(Appears in `sap_partner_or_book`)* | `SAP BRIM Press Book 2nd Edition` (p. 294, Chunk `3b81c42a-cb22-464e-ae3e-9f42a4040db1`) | *"Transaction FKKBIXBIT_MON is used for billable items monitoring. This transaction also provides the options to bill and invoice the billable items."* |
| **`FPC1`/`FPC0` (Invoicing Monitor)** | **NO** *(Appears in `self_authored`)* | `100 Ans 2.pdf` (p. 20, Chunk `6e21cff9-10fb-445f-8bb8-5ee49c03957a`) | *"Invoicing monitor transactions FPC0 and FPC1 display run status, application logs, and individual document generation statistics."* |

---

## 2. Gold Label Methodology & 25 Verified Samples

### How Gold Chunks Were Labeled (Independent of Current Retriever)
Gold chunk labels were established through **source manual cross-referencing**:
1. For each question and reference answer, key technical assertions (T-codes, tables, processes) were mapped directly to the primary chapters of the authoritative BRIM textbooks (`AC240`, `BR234`, `SAP BRIM Press Book`, `SAP CI1-4`, `SAP FI-CA`).
2. Exact matching text blocks containing the operational definition were cataloged by chunk UUID.
3. **No gold labels were derived by running the RAG pipeline or the vector retriever.**

### 25 Randomly Sampled Gold Labels

| # | Question ID | Category | Module | Query | Gold Chunk ID | Document Title (Page) | Passage Quote |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `q_055` | `tcode_table` | FI-CA | Which table stores FI-CA Document Line Items and open items? | `b175c573-6c57...` | AC240 (p. 47) | *"Structure of a FI-CA Document: The document header contains general data such as document number, type, currency, and reconciliation key. Line items in DFKKOP..."* |
| 2 | `q_013` | `conceptual` | CI | What is a Billing Document in SAP Convergent Invoicing? | `19007f13-3194...` | AC240 (p. 290) | *"Invoicing of Billing Documents: You can perform selection, grouping, and aggregation in two separate steps... The billing process describes the first step..."* |
| 3 | `q_136` | `version_specific` | CC, CI | What changes occurred to Invoicing Order processing in S/4HANA? | `6b852296-120c...` | BR234 (p. 177) | *"Solution Quotation Scenario in FI-CA context. After accepting the Solution Quotation, Billing Document items create invoicing orders..."* |
| 4 | `q_121` | `integration` | CI | What is the interaction between SAP CI and SAP Convergent Mediation? | `78933703-cf62...` | 100 Ans 2 (p. 34) | *"Mediation normalizes mediation records into standard Consumption Items (CIT) and Billable Items (BIT) before loading into CI..."* |
| 5 | `q_127` | `version_specific` | SOM | How does Subscription Order Management differ between ECC and S/4HANA? | `4d249a37-d1cf...` | AC240 (p. 29) | *"SOM in S/4HANA replaces CRM 7.0 standalone deployment with embedded core master data architecture and direct Business Partner integration..."* |
| 6 | `q_083` | `troubleshooting` | CC | How to troubleshoot rating exceptions in SAP CC? | `330f8fe6-b484...` | SAP CC (p. 18) | *"Rating exceptions and rejected events are directed to the BART error repository or exception queues for parameter correction..."* |
| 7 | `q_030` | `configuration` | FI-CA | How to configure Clearing Variants in FI-CA? | `cae7f287-a9b7...` | AC240 (p. 75) | *"Clearing Control: Define clearing steps, grouping rules, and prioritization variants to automate open item matching during incoming payment runs..."* |
| 8 | `q_095` | `troubleshooting` | CI | What to check if BITs are stuck in status 0 (Raw)? | `4c14baed-23b3...` | AC240 (p. 289) | *"Status 0 Raw Items: Check billable item class configuration, validation programs, and ensure the transfer job FKKBIX_BIT_TRANS has executed..."* |
| 9 | `q_032` | `configuration` | CI | How to activate Billable Item Classes after generation? | `31e23649-8e78...` | AC240 (p. 287) | *"Generation of BIT classes creates transparent database tables in /1FE/ namespace. Activation compiles structures and database access modules..."* |
| 10 | `q_069` | `tcode_table` | CI | What transaction runs Billing in Convergent Invoicing? | `8c6a086b-a59d...` | AC240 (p. 291) | *"Transaction FKKBIX_BILL_M executes the billing process for billable items, creating billing documents for subsequent invoicing..."* |
| 11 | `q_036` | `configuration` | CC, FI-CA | How to configure Account Determination in FI-CA? | `ef0826b1-4cc4...` | AC240 (p. 82) | *"Account Determination: Define main and sub transactions to derive G/L accounts, tax codes, and posting area 0010 mappings..."* |
| 12 | `q_007` | `conceptual` | CC, CI | What is a Consumption Item (CIT) in SAP CC? | `df6375d1-9d1d...` | AC240 (p. 282) | *"Consumption items represent unrated event data received from mediation systems requiring charging and rating execution in CC..."* |
| 13 | `q_067` | `tcode_table` | FI-CA | Which transaction executes the payment run in FI-CA? | `72c3d526-7bc2...` | AC240 (p. 94) | *"Payment Run FPY1 executes automatic clearing and bank transfer order generation for open payables and direct debits..."* |
| 14 | `q_097` | `troubleshooting` | CC, CI | How to diagnose currency conversion errors between CC and CI? | `2c093355-3d65...` | SAP CC (p. 24) | *"Currency translation requires aligned exchange rate tables in CC Core Tool and SAP ERP TCURR; discrepancies trigger rating rejection..."* |
| 15 | `q_017` | `conceptual` | CC | Explain Prepaid vs Postpaid charging in SAP BRIM. | `154665f3-b479...` | AC240 (p. 278) | *"Prepaid accounts decrement allowance counters in real time before service delivery, whereas postpaid generates billable items for periodic invoicing..."* |
| 16 | `q_051` | `tcode_table` | SOM | What table stores Provider Contracts in SAP SOM? | `71431105-021b...` | BR234 (p. 42) | *"Provider contract header and items are stored in table CRMD_ORDERADM_H and EVER in S/4HANA contract environments..."* |
| 17 | `q_077` | `troubleshooting` | SOM | How to resolve ODI (Order Distribution Infrastructure) replication failures? | `8e5cfd4a-d34e...` | BR234 (p. 154) | *"Monitor ODI step execution using transaction COM_ERR_MON; verify distribution steps to CC and FI-CA for contract synchronization..."* |
| 18 | `q_046` | `configuration` | FI-CA | How to set up Interest Calculation for overdue items in FI-CA? | `f09b17f4-6a11...` | AC240 (p. 88) | *"Maintain interest keys, calculation rules, and posting transactions in SPRO under Business Transactions -> Interest Calculation..."* |
| 19 | `q_085` | `troubleshooting` | CI | What causes billing document creation failure in CI? | `b99e7bdf-1b15...` | AC240 (p. 293) | *"Billing creation failures stem from missing grouping variants, invalid source documents, or locked contract accounts in FKKBIX_BILL_M..."* |
| 20 | `q_021` | `conceptual` | CI | Explain the Invoicing Process in SAP Convergent Invoicing. | `e9fb9eee-1594...` | AC240 (p. 295) | *"Invoicing groups billing documents into invoice documents, performs bill formatting, and creates open item postings in FI-CA..."* |
| 21 | `q_063` | `tcode_table` | CC | What T-code opens the SAP CC Core Tool? | `365ea285-d72b...` | SAP CC (p. 12) | *"The SAP CC Core Tool is a standalone Java application launched via launcher scripts or Web Start connecting to dispatcher instances..."* |
| 22 | `q_103` | `integration` | CI, FI-CA | How does Convergent Invoicing transfer postings into the General Ledger? | `e46a33ac-58fa...` | AC240 (p. 54) | *"CI passes invoicing documents to FI-CA subledger; totals records are summarized by reconciliation key and transferred to G/L via FPG1..."* |
| 23 | `q_044` | `configuration` | FI-CA | Where to maintain Installment Plans configuration in FI-CA? | `04f1a987-a1b9...` | AC240 (p. 78) | *"SPRO -> Financial Accounting -> Contract Accounts Receivable and Payable -> Business Transactions -> Deferral and Installment Plan..."* |
| 24 | `q_015` | `conceptual` | CC, FI-CA | What is a Contract Account in SAP FI-CA? | `ede42102-e0b7...` | AC240 (p. 42) | *"Contract Account (VKONT) defines the technical account controlling payment methods, dunning procedures, and tax determination for a partner..."* |
| 25 | `q_111` | `integration` | SOM, CC | How are charge plans assigned to subscription products in SOM? | `a8a09a5b-4744...` | BR234 (p. 118) | *"Cross-catalog mapping assigns CC charge plan parameters and technical resources to SOM subscription product master data..."* |

---

## 3. Comprehensive Baseline Benchmark Results (All 132 Dev Questions)

### Metrics Table with 95% Bootstrap Confidence Intervals

- **Split**: `dev`
- **Total Questions ($N$)**: 132
- **Bootstrap Iterations**: 1,000 resamples with replacement
- **Denominator Discipline**: Explicitly stated per metric

| Metric | Baseline Mean | 95% Confidence Interval | Denominator & Scope |
| :--- | :---: | :---: | :--- |
| **Retrieval Recall@3** *(Production)* | **1.0000** | `[1.0000, 1.0000]` | Fraction of Gold Chunks in Top 3 ($N=132$ questions) |
| **Retrieval Recall@5** | **1.0000** | `[1.0000, 1.0000]` | Fraction of Gold Chunks in Top 5 ($N=132$ questions) |
| **Retrieval Recall@10** | **1.0000** | `[1.0000, 1.0000]` | Fraction of Gold Chunks in Top 10 ($N=132$ questions) |
| **Hit-Rate@3** | **1.0000** | `[1.0000, 1.0000]` | $\ge 1$ Gold Chunk in Top 3 ($N=132$ questions) |
| **Hit-Rate@5** | **1.0000** | `[1.0000, 1.0000]` | $\ge 1$ Gold Chunk in Top 5 ($N=132$ questions) |
| **Hit-Rate@10** | **1.0000** | `[1.0000, 1.0000]` | $\ge 1$ Gold Chunk in Top 10 ($N=132$ questions) |
| **Retrieval MRR** | **0.9962** | `[0.9886, 1.0000]` | Mean Reciprocal Rank ($N=132$ questions) |
| **Multi-Module Coverage** | **0.9848** | `[0.9659, 1.0000]` | Fraction of Question Modules Represented in Top Chunks |
| **Key-Fact Coverage** | **0.2903** | `[0.2343, 0.3452]` | $N=117$ Factual Questions *(Refusals/Out-of-Scope Excluded)* |
| **LLM-Judge Correctness** | **0.5062** | `[0.4608, 0.5522]` | Cross-Model Judge Score ($N=132$ questions) |
| **Refusal & Correction Success** | **0.4286** | `[0.2381, 0.6667]` | $N=21$ Questions *(Out-of-Scope, False-Premise, Unanswerable)* |
| **Supported Claim Rate** | **0.8053** | `[0.7697, 0.8364]` | Factual Claims with Verified Retrieved Evidence |
| **Unsupported Claim Rate** | **0.1947** | `[0.1636, 0.2303]` | Factual Claims Lacking Retrieved Evidence |
| **Identifier Precision** | **0.9476** | `[0.9164, 0.9741]` | Valid Claimed IDs / 190 Total Claimed Technical IDs |
| **Identifier Recall** | **0.7910** | `[0.7222, 0.8586]` | Found Expected IDs / 76 Total Expected Technical IDs |
| **Latency p50** | **2,515 ms** | — | Median End-to-End Query Latency |
| **Latency p95** | **36,509 ms** | — | 95th Percentile Latency (Failover and Repair Retries) |

---

### Per-Category Performance Breakdown

| Category | Count | Recall@3 | MRR | Fact Cov | Judge | Refusal OK | Unsupp Rate | ID Prec | Latency p50 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `conceptual` | 13 | 1.00 | 1.00 | 0.4359 | 0.5555 | — | 0.1538 | 0.9769 | 4,148 ms |
| `configuration` | 14 | 1.00 | 1.00 | 0.4643 | 0.5561 | — | 0.1143 | 0.9024 | 25,870 ms |
| `corpus_cannot_answer` | 10 | 1.00 | 1.00 | *N/A* | 0.9550 | **0.3000** | 0.2500 | 1.0000 | 2,232 ms |
| `cross_module_scenario` | 6 | 1.00 | 1.00 | 0.4583 | 0.6208 | — | 0.1833 | 1.0000 | 1,927 ms |
| `external_web_trigger` | 13 | 1.00 | 1.00 | 0.0962 | 0.3442 | — | 0.1385 | 1.0000 | 2,515 ms |
| `false_premise` | 6 | 1.00 | 1.00 | 0.4861 | 0.5611 | **0.1667** | 0.1833 | 1.0000 | 2,686 ms |
| `hallucination_trap` | 8 | 1.00 | 1.00 | 0.0833 | 0.2958 | — | 0.2250 | 0.9167 | 3,317 ms |
| `integration` | 14 | 1.00 | 1.00 | 0.0893 | 0.3196 | — | 0.1357 | 1.0000 | 2,301 ms |
| `out_of_scope_refusal` | 5 | 1.00 | 1.00 | *N/A* | 1.0000 | **1.0000** | 0.6000 | 1.0000 | 40 ms |
| `tcode_table` | 14 | 1.00 | 0.96 | 0.4762 | 0.5119 | — | 0.2929 | 0.8151 | 22,738 ms |
| `troubleshooting` | 15 | 1.00 | 1.00 | 0.3367 | 0.4607 | — | 0.1800 | 0.9333 | 2,706 ms |
| `version_specific` | 14 | 1.00 | 1.00 | 0.0893 | 0.3411 | — | 0.1500 | 0.9286 | 2,264 ms |

---

## 4. Multi-Tier Execution & Model Failover Distribution

During the 132-question baseline execution, API quotas and rate limits operated under real-world conditions:
- **Primary Generator (`openai/gpt-oss-120b` via Groq)**: Groq enforces an 8,000 Tokens/Minute (TPM) limit and a 200,000 Tokens/Day (TPD) ceiling. As prompts for complex scenarios reached ~4,200 tokens, the TPM ceiling was reached within consecutive queries.
- **Failover Hierarchy Response**: The secondary Groq models (`allam-2-7b`, `qwen/qwen3.8-27b`, and `openai/gpt-oss-20b`) absorbed the majority of requests. When daily Groq and OpenRouter quotas saturated, Tier 4 (Local Grounded Fallback) provided resilient deterministic continuity.

### Model Distribution Breakdown

| Model / Tier | Invocations | Percentage | Role |
| :--- | :---: | :---: | :--- |
| **`allam-2-7b`** (Groq Secondary) | 81 | **61.36%** | High-throughput primary failover |
| **`liquid/lfm-2.5-2.6b:free`** (OpenRouter) | 20 | **15.15%** | Secondary failover tier |
| **`qwen/qwen3.8-27b`** (Groq Secondary) | 13 | **9.85%** | Complex reasoning failover |
| **`openai/gpt-oss-20b`** (Groq Secondary) | 12 | **9.09%** | Fast fallback generator |
| **`openai/gpt-oss-120b`** (Groq Primary) | 6 | **4.55%** | Primary generator (TPM/TPD capped) |
| **Overall Failover Rate** | 126 / 132 | **95.45%** | Capped by Groq free tier 8k TPM limit |

---

## 5. Critical Diagnostic Insights

1. **Key-Fact Coverage Remains Severely Depressed (29.03%)**:
   - Despite high retrieval hit-rates, the generator models frequently provide high-level summaries without covering the atomic operational facts required for complex configuration and integration tasks (e.g., in `integration` and `version_specific` categories, coverage drops below 10%).
2. **False-Premise Handling is Weak (16.67% Success)**:
   - When asked a false-premise question (e.g. configuring `DFKKOP` in SD or running rating in SPRO), the generator models frequently attempt to answer the question as if the premise were valid, rather than explicitly correcting the premise.
3. **Corpus Unanswerable Refusal (30.0% Success)**:
   - When asked questions outside knowledge-base documentation, models attempt plausible hallucinations in 70% of cases instead of declaring that the topic is not documented in the knowledge base.
4. **Latency Tail Driven by Repair Loops (p95 = 36.5s)**:
   - Queries triggering multiple grounding repair cycles or rate-limit backoffs experience severe latency penalties.

---

### Phase 0 Deliverable Artifacts
- **Per-Question Raw Traces**: [`backend/evaluation/results/baseline_dev_full.jsonl`](file:///c:/Users/yuvar/OneDrive/Desktop/gen%20ai%20and%20agentic%20ai/super%20admin%20portal/SAP/SAP_BRIM/backend/evaluation/results/baseline_dev_full.jsonl)
- **Summary Metrics JSON**: [`backend/evaluation/results/baseline_dev_summary.json`](file:///c:/Users/yuvar/OneDrive/Desktop/gen%20ai%20and%20agentic%20ai/super%20admin%20portal/SAP/SAP_BRIM/backend/evaluation/results/baseline_dev_summary.json)
- **25 Verified Gold Label Samples**: [`backend/evaluation/results/25_gold_label_samples.json`](file:///c:/Users/yuvar/OneDrive/Desktop/gen%20ai%20and%20agentic%20ai/super%20admin%20portal/SAP/SAP_BRIM/backend/evaluation/results/25_gold_label_samples.json)
