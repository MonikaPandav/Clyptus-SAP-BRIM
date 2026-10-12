"""
Corpus Identifier Indexer for SAP BRIM.
Builds an exact-string identifier index from chunks:
- identifier: Exact string as authored (no normalization)
- type: tcode, table, report_or_fm, technical_object
- module: Primary SAP BRIM module
- tier: Highest tier where the identifier appears
- chunk_ids: Exact list of chunk IDs containing the identifier
"""

import re
from typing import Dict, Any, List, Set, Tuple

# Patterns for extracting candidate identifiers (exact case preserved)
TCODE_CANDIDATE_REGEX = re.compile(r"\b([A-Z][A-Z0-9_]{2,19})\b")
TABLE_CANDIDATE_REGEX = re.compile(r"\b([A-Z][A-Z0-9_]{3,19})\b")

# Known SAP prefixes and patterns for high precision
KNOWN_TABLE_PREFIXES = ("DFKK", "FKK", "ERDK", "ERCH", "BUT", "TFK", "ACDOCA", "BSEG", "BKPF", "MARA", "VBAK", "VBAP", "EKKO", "EKPO", "FARR")
KNOWN_TCODE_PREFIXES = ("FP", "FKK", "FARR", "SPRO", "SM", "SE", "VA", "ME", "MI", "XK", "FK", "OB")
KNOWN_FM_PREFIXES = ("BAPI_", "RFKK", "FKK_")

# Negative blacklist for common uppercase English/SAP acronyms that are NOT identifiers
EXCLUDED_STRINGS = {
    "SAP", "BRIM", "SOM", "CC", "CI", "FICA", "FI-CA", "RAR", "RAP", "BTP",
    "ERP", "CRM", "HTTP", "HTTPS", "JSON", "XML", "REST", "SOAP", "RFC",
    "HTML", "ODATA", "ABAP", "FIORI", "GUI", "API", "URL", "PDF", "SQL",
    "HANA", "PUBLIC", "PRIVATE", "PAGE", "UNIT", "LESSON", "FIGURE", "TABLE",
    "SECTION", "DOCUMENT", "VERSION", "COPYRIGHT", "RIGHTS", "RESERVED",
    "TOTAL", "DATE", "TIME", "STATUS", "ERROR", "ACTIVE", "INACTIVE", "ITEM",
    "ITEMS", "NUMBER", "CODE", "TYPE", "DATA", "TEXT", "POSTING", "PAYMENT",
    "ACCOUNT", "ORDER", "CONTRACT", "INVOICE", "BILLING", "CLEARING", "PARTNER",
    "COMPANY", "GENERAL", "MASTER", "SYSTEM", "CLIENT", "SERVER", "LOG",
    "STEP", "CASE", "TRUE", "FALSE", "NULL", "NONE", "NOTE", "WARNING", "TIP",
    "INFO", "OUTPUT", "INPUT", "CONFIG", "SPRO", "CUSTOMIZING" # SPRO is handled specifically as tcode
}
# Keep SPRO as tcode
EXCLUDED_STRINGS.remove("SPRO")

# Tiers ranked by authority
TIER_AUTHORITY_RANK = {
    "official_sap": 5,
    "sap_partner_or_book": 4,
    "official_sap_domain": 3,
    "forum": 2,
    "self_authored": 1
}


def classify_identifier_type(ident: str) -> str:
    """Classifies candidate exact string into type."""
    if ident.startswith(KNOWN_FM_PREFIXES) or "BAPI" in ident:
        return "report_or_fm"
    if any(ident.startswith(p) for p in KNOWN_TABLE_PREFIXES):
        return "table"
    if any(ident.startswith(p) for p in KNOWN_TCODE_PREFIXES):
        return "tcode"
    if ident in {"ODI", "UTI", "CM_OBJECT_KEY", "IFRS15", "ASC606"}:
        return "technical_object"
    if "_" in ident and ident.isupper():
        return "technical_object"
    return "tcode" if (len(ident) <= 5 and any(c.isdigit() for c in ident)) else "technical_object"


def extract_chunk_identifiers(chunk_text: str) -> List[Tuple[str, str]]:
    """
    Extracts exact-string technical identifiers from chunk text.
    Returns: List of (identifier, type)
    """
    found: List[Tuple[str, str]] = []
    seen: Set[str] = set()

    # 1. Database tables
    for m in TABLE_CANDIDATE_REGEX.finditer(chunk_text):
        token = m.group(1)
        if token in seen or token in EXCLUDED_STRINGS or len(token) < 4:
            continue
        if any(token.startswith(p) for p in KNOWN_TABLE_PREFIXES):
            seen.add(token)
            found.append((token, "table"))

    # 2. Transaction codes
    for m in TCODE_CANDIDATE_REGEX.finditer(chunk_text):
        token = m.group(1)
        if token in seen or token in EXCLUDED_STRINGS:
            continue
        if any(token.startswith(p) for p in KNOWN_TCODE_PREFIXES):
            # Exclude tokens like "FP" or "SE" that are just 2 letters without digits or subnames
            if len(token) >= 3 or any(c.isdigit() for c in token) or token == "SPRO":
                seen.add(token)
                found.append((token, "tcode"))

    # 3. Reports and Function Modules
    for m in re.finditer(r"\b(BAPI_[A-Z0-9_]+|RFKK[A-Z0-9_]+|FKK_[A-Z0-9_]+)\b", chunk_text):
        token = m.group(1)
        if token not in seen:
            seen.add(token)
            found.append((token, "report_or_fm"))

    # 4. Known BRIM Technical Objects
    for token in ["ODI", "UTI", "CM_OBJECT_KEY", "DFKKBIXBIT_SIM"]:
        if token in chunk_text and token not in seen:
            seen.add(token)
            found.append((token, "technical_object"))

    return found


def assign_identifier_module(identifier: str, type_: str) -> str:
    """Infers primary module of an identifier."""
    ident = identifier.upper()
    if ident.startswith(("DFKKBIXBIT", "DFKKBIXCIT", "FKKBIX")):
        return "CI"
    if ident.startswith(("DFKKOP", "DFKKKO", "DFKKCOLL", "FP", "TFK", "RFKK", "FKK_")):
        return "FI-CA"
    if ident.startswith(("FARR", "RAI", "POB", "SSP")):
        return "RAR"
    if ident in {"UTI", "CHARGING_CONTRACT", "CHARGE_PLAN"}:
        return "CC"
    if ident in {"ODI", "SUBSCRIPTION_ORDER", "PRVO", "PRVC"}:
        return "SOM"
    if ident in {"SPRO", "SM59", "SE80", "SICF", "ACDOCA", "BSEG", "BKPF", "BUT000"}:
        return "General"
    return "General"
