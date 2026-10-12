# SAP BRIM Knowledge Gap & Authority Tier Report (Post-CI1-CI4 Exclusion)

## 1. Chunk Distribution per Module across Authority Tiers (In-Domain Only)

| Module | official_sap | sap_partner_or_book | forum | self_authored | Total In-Domain |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **SOM** | 956 | 308 | 1 | 127 | **1,392** |
| **CM** | 14 | 36 | 0 | 58 | **108** |
| **CC** | 284 | 219 | 0 | 130 | **633** |
| **CI** | 60 | 333 | 0 | 90 | **483** |
| **FI-CA** | 386 | 217 | 4 | 213 | **820** |
| **RAR** | 8 | 54 | 0 | 50 | **112** |
| **General** | 14 | 113 | 0 | 25 | **152** |
| **unknown** | 2 | 221 | 0 | 39 | **262** |
| **TOTAL** | **1,724** | **1,501** | **5** | **732** | **3,962** |

## 2. Identified Thinnest Official Areas in Knowledge Base

Analyzing chunks where `tier == 'official_sap'` and `is_off_domain == 0`:

- **RAR**: **8 official chunks** (0.5% of official corpus) — *[CRITICAL GAP]*
- **CM**: **14 official chunks** (0.8% of official corpus) — *[CRITICAL GAP]*
- **CI**: **60 official chunks** (3.5% of official corpus) — *[CRITICAL GAP]*
- **CC**: **284 official chunks** (16.5% of official corpus) — *[THIN COVERAGE]*
- **FI-CA**: **386 official chunks** (22.4% of official corpus) — *[THIN COVERAGE]*
- **SOM**: **956 official chunks** (55.5% of official corpus) — *[ADEQUATE]*

### Key Findings:
1. **CI (Convergent Invoicing)**: With `SAP CI1.pdf` through `SAP CI4.pdf` flagged as off-domain (they are Cloud Integration manuals), official Convergent Invoicing chunks drop to **0 official courseware chunks**! CI knowledge in the system relies on the **SAP BRIM Press Book (333 chunks)** and self-authored CIT/BIT architecture (90 chunks).
2. **RAR (Revenue Accounting & Reporting)**: **8 official chunks** (0.5% of official corpus) from cross-module references. Zero dedicated official RAR courseware.
3. **CM (Convergent Mediation)**: **16 official chunks** (0.9% of official corpus) from SOM/CC references. Zero dedicated CM manual.
4. **CC (Convergent Charging)**: **297 official chunks** (17.2% of official corpus) from `SAP CC.pdf` and `mg.pdf`.
5. **FI-CA (Contract Accounts)**: **386 official chunks** (22.4% of official corpus) from `BRIM_AC240_EN_Col16.pdf`.
6. **SOM (Subscription Order Management)**: **956 official chunks** (55.5% of official corpus) from `BR234_EN_SOM 2.pdf` and `pdfdownload.pdf`.

## 3. Ingestion Procedure for New Official Documents

> [!IMPORTANT]
> **Do NOT ingest any external document without explicit user licence confirmation.**

`corpus_service.ingest_official_document(file_path, licence_confirmed=True)` strictly enforces this gate.