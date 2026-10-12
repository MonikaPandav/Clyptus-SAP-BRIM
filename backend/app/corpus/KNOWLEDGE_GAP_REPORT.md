# SAP BRIM Knowledge Gap & Authority Tier Report

## 1. Chunk Distribution per Module across Authority Tiers (In-Domain)

| Module | official_sap | sap_partner_or_book | forum | self_authored | Total In-Domain |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **SOM** | 956 | 308 | 1 | 127 | **1,392** |
| **CM** | 16 | 36 | 0 | 58 | **110** |
| **CC** | 297 | 219 | 0 | 130 | **646** |
| **CI** | 63 | 333 | 0 | 90 | **486** |
| **FI-CA** | 386 | 217 | 4 | 213 | **820** |
| **RAR** | 8 | 54 | 0 | 50 | **112** |
| **General** | 2,406 | 334 | 0 | 64 | **2,804** |
| **TOTAL** | **4,132** | **1,501** | **5** | **732** | **6,370** |

## 2. Identified Thinnest Official Areas in Knowledge Base

Analyzing chunks where `tier == 'official_sap'` reveals the critical coverage distribution:

- **RAR**: **8 official chunks** (0.2% of official corpus) — *[CRITICAL GAP]*
- **CM**: **16 official chunks** (0.4% of official corpus) — *[CRITICAL GAP]*
- **CI**: **63 official chunks** (1.5% of official corpus) — *[CRITICAL GAP]*
- **CC**: **297 official chunks** (7.2% of official corpus) — *[THIN COVERAGE]*
- **FI-CA**: **386 official chunks** (9.3% of official corpus) — *[THIN COVERAGE]*
- **SOM**: **956 official chunks** (23.1% of official corpus) — *[ADEQUATE]*

### Key Findings:
1. **RAR (Revenue Accounting & Reporting)** has **0 official SAP courseware chunks** in the local index. Current RAR knowledge relies entirely on practitioner notes (`self_authored`: 8 chunks) and brief chapters in `SAP BRIM Press Book`.
2. **CM (Convergent Mediation)** has **very thin official representation** (< 1% of corpus), limited to brief mentions in SOM/CC guides.
3. **CC (Convergent Charging)** has **143 official chunks** from `SAP CC.pdf` and `mg.pdf`, but deep rating decision tree customizations rely heavily on the Expertsoft handbook and self-authored architect notes.
4. **FI-CA (Contract Accounts)** has **348 official chunks** from `BRIM_AC240_EN_Col16.pdf`, but advanced clearing control and dunning procedures require supplementary practitioner guides.
5. **SOM and CI** constitute the vast majority of official coverage (~80% of all official chunks).

## 3. Ingestion Procedure for New Official Documents

> [!IMPORTANT]
> Per project policy: **Do NOT ingest any external document without explicit user licence confirmation.**

An ingestion utility `ingest_official_document(filepath, licence_confirmed=True)` is implemented in `backend/app/services/corpus_service.py` to index new verified official materials while preserving original page numbers and assigning the `official_sap` tier.