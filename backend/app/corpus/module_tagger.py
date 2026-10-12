"""
Module Classifier and Keyword Re-Tagger for SAP BRIM Chunks.
Tags chunks with one or more SAP BRIM modules:
- SOM (Subscription Order Management)
- CM (Convergent Mediation)
- CC (Convergent Charging)
- CI (Convergent Invoicing)
- FI-CA (Contract Accounts Receivable and Payable)
- RAR (Revenue Accounting and Reporting)
- General (Cross-module BRIM / Architecture / General SAP)
"""

import re
from typing import List, Dict, Any, Tuple, Set

# Compiled module recognition rules with weighted patterns
MODULE_RULES = {
    "SOM": [
        (re.compile(r"\bsubscription\s+order\s+management\b", re.I), 3.0),
        (re.compile(r"\bsubscription\s+(?:order|contract)\b", re.I), 2.5),
        (re.compile(r"\bprovider\s+(?:order|contract)\b", re.I), 2.0),
        (re.compile(r"\bsolution\s+quotation\b", re.I), 2.5),
        (re.compile(r"\border\s+distribution\s+infrastructure\b|\bodi\b", re.I), 2.5),
        (re.compile(r"\bmaster\s+agreement\b", re.I), 2.0),
        (re.compile(r"\btechnical\s+resource\b", re.I), 1.5),
        (re.compile(r"\bsom\b", re.I), 1.5),
        (re.compile(r"\bchange\s+process\b", re.I), 1.2),
        (re.compile(r"\bbr234\b", re.I), 2.5),
    ],
    "CM": [
        (re.compile(r"\bconvergent\s+mediation\b", re.I), 3.5),
        (re.compile(r"\bdigital\s*route\b", re.I), 3.0),
        (re.compile(r"\bcall\s+detail\s+records?\b|\bcdr\b", re.I), 2.5),
        (re.compile(r"\bmediation\s+(?:zone|engine|flow|node)\b", re.I), 2.5),
        (re.compile(r"\bmediation\b", re.I), 1.5),
        (re.compile(r"\bevent\s+(?:collection|deduplication|enrichment)\b", re.I), 2.0),
        (re.compile(r"\bcm\b", re.I), 1.0),
    ],
    "CC": [
        (re.compile(r"\bconvergent\s+charging\b", re.I), 3.5),
        (re.compile(r"\bcharge\s+plan\b|\bcharging\s+plan\b", re.I), 3.0),
        (re.compile(r"\bprice\s+plan\b|\brating\s+logic\b", re.I), 2.5),
        (re.compile(r"\bchargeable\s+item\b|\bcharged\s+item\b", re.I), 2.5),
        (re.compile(r"\brange\s+table\b|\bmapping\s+table\b|\btranslation\s+table\b", re.I), 2.0),
        (re.compile(r"\ballowance(?:\s+plan|\s+package)?\b", re.I), 2.5),
        (re.compile(r"\bsubscriber\s+account\b|\bprepaid\s+account\b", re.I), 2.0),
        (re.compile(r"\bcore\s+tool\b|\bhazelcast\b|\brater\b|\bguider\b|\bbulkloader\b", re.I), 2.5),
        (re.compile(r"\bcc\b", re.I), 1.0),
    ],
    "CI": [
        (re.compile(r"\bconvergent\s+invoicing\b", re.I), 3.5),
        (re.compile(r"\bbillable\s+item(?:\s+class)?\b", re.I), 3.0),
        (re.compile(r"\bconsumption\s+item(?:\s+class)?\b", re.I), 3.0),
        (re.compile(r"\bbit\b", re.I), 1.8),
        (re.compile(r"\bcit\b", re.I), 1.8),
        (re.compile(r"\bbilling\s+document\b|\binvoicing\s+document\b", re.I), 2.2),
        (re.compile(r"\bbilling\s+process\b|\binvoicing\s+process\b", re.I), 2.2),
        (re.compile(r"\bbilling\s+order\b|\bbilling\s+cycle\b", re.I), 2.0),
        (re.compile(r"\bdfkkbixbit\w*\b|\bdfkkbixcit\w*\b|\bfkkbix_\w+\b", re.I), 3.0),
        (re.compile(r"\bci\b", re.I), 1.0),
    ],
    "FI-CA": [
        (re.compile(r"\bcontract\s+accounts?\s+receivable(?:\s+and\s+payable)?\b", re.I), 3.5),
        (re.compile(r"\bfi[- ]?ca\b|\bfica\b", re.I), 3.0),
        (re.compile(r"\bcontract\s+account\b", re.I), 2.2),
        (re.compile(r"\bclearing\s+control\b", re.I), 2.5),
        (re.compile(r"\bopen\s+items?\b", re.I), 2.0),
        (re.compile(r"\bdunning(?:\s+procedure|\s+level|\s+notice)?\b", re.I), 2.5),
        (re.compile(r"\bpayment\s+lot\b|\breturns\s+lot\b", re.I), 2.5),
        (re.compile(r"\breconciliation\s+key\b", re.I), 2.5),
        (re.compile(r"\bdfkkop\b|\bdfkkko\b|\bdfkkcoll\b", re.I), 3.0),
        (re.compile(r"\bposting\s+area\s+\d+\b", re.I), 2.5),
        (re.compile(r"\bfpl9\b|\bfp05\b|\bfp35\b|\bfpg1\b|\bfp03d\b", re.I), 2.5),
        (re.compile(r"\bac240\b", re.I), 2.5),
    ],
    "RAR": [
        (re.compile(r"\brevenue\s+accounting\s+and\s+reporting\b", re.I), 3.5),
        (re.compile(r"\brevenue\s+recognition\b", re.I), 3.0),
        (re.compile(r"\bperformance\s+obligation\b|\bpob\b", re.I), 3.0),
        (re.compile(r"\bstandalone\s+selling\s+price\b|\bssp\b", re.I), 3.0),
        (re.compile(r"\brevenue\s+accounting\s+item\b|\brai\b", re.I), 3.0),
        (re.compile(r"\bifrs\s*15\b|\basc\s*606\b", re.I), 3.0),
        (re.compile(r"\bcontract\s+(?:liability|asset)\b", re.I), 2.5),
        (re.compile(r"\bfarr_rai_mon\b|\bfarr_rar_mon\b|\bfarr_\w+\b", re.I), 3.0),
        (re.compile(r"\brar\b", re.I), 2.0),
    ]
}

# Document title/name priors for module hint
DOCUMENT_MODULE_PRIORS = {
    "BR234_EN_SOM 2.pdf": "SOM",
    "pdfdownload.pdf": "SOM",
    "2020_S4H_BRIM_SOM_Device_as_a_Service.pdf": "SOM",
    "SAP_BRIM_SOM_Subscription_Order_Management_Master_Guide.pdf": "SOM",
    "SAP CC.pdf": "CC",
    "mg.pdf": "CC",
    "SAP_BRIM_CC_Convergent_Charging_Advanced_Architecture.pdf": "CC",
    "SAP_BRIM_Convergent_Invoicing_CIT_BIT_Master_Architecture.pdf": "CI",
    "BRIM_AC240_EN_Col16.pdf": "FI-CA",
    "SAP FI-CA.pdf": "FI-CA",
    "Budget billing.pdf": "FI-CA",
    "SAP_BRIM_FICA_Contract_Accounts_Master_Handbook.pdf": "FI-CA",
    "RAR Contract Reversal Process.pdf": "RAR",
    "SAP Revenue Recognition (RAR) Processing Flow, Exemptions, Reversals & System Integration.pdf": "RAR",
}


def score_chunk_modules(chunk_text: str, document_name: str = "") -> Dict[str, float]:
    """Computes evidence scores for each SAP BRIM module for a given chunk."""
    scores = {mod: 0.0 for mod in MODULE_RULES}

    # Document-level prior (soft signal +1.0)
    prior_mod = DOCUMENT_MODULE_PRIORS.get(document_name)
    if prior_mod and prior_mod in scores:
        scores[prior_mod] += 1.0

    # Rule-based scoring with exact regex matches
    for mod, rules in MODULE_RULES.items():
        for pattern, weight in rules:
            matches = len(pattern.findall(chunk_text))
            if matches > 0:
                # Diminishing returns for multiple matches of the same term
                effective_weight = weight * (1.0 + 0.3 * min(matches - 1, 4))
                scores[mod] += effective_weight

    return scores


def tag_chunk_modules(chunk_text: str, document_name: str = "", score_threshold: float = 2.0) -> Tuple[List[str], str]:
    """
    Tags chunk with one or more modules.
    Returns:
        (modules_list, primary_module)
    """
    scores = score_chunk_modules(chunk_text, document_name)

    # Modules exceeding score threshold
    active_modules = [mod for mod, score in scores.items() if score >= score_threshold]

    # Sort active modules by score descending
    active_modules.sort(key=lambda m: scores[m], reverse=True)

    # If no specialized module reached threshold, or if text is broad end-to-end overview
    if not active_modules:
        # Check if the highest score is at least 1.0
        max_mod = max(scores, key=scores.get)
        if scores[max_mod] >= 1.0:
            active_modules = [max_mod]
            primary = max_mod
        else:
            # Check for general SAP BRIM / architecture keywords
            if re.search(r"\b(sap\s+billing\s+and\s+revenue\s+innovation\s+management|sap\s+brim|\bbrim\b|order-to-cash|quote-to-cash|solution\s+overview|solution\s+in\s+detail|master\s+data|integration\s+architecture)\b", chunk_text, re.I):
                active_modules = ["General"]
                primary = "General"
            else:
                active_modules = ["unknown"]
                primary = "unknown"
    else:
        # If 4 or more modules are tagged with comparable high scores, mark as General as well
        if len(active_modules) >= 4 and all(scores[m] >= 2.5 for m in active_modules[:4]):
            if "General" not in active_modules:
                active_modules.append("General")
        primary = active_modules[0]

    return active_modules, primary
