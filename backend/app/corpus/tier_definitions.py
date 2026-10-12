"""
Corpus Tier and Domain Definitions for SAP BRIM Knowledge Base.
Contains exact mapping of all 40 indexed documents to authority tiers and domain status.
"""

from typing import Dict, Any, List

# Authority tiers:
# 1. official_sap: Official SAP course manuals, implementation guides, standard documentation, simplification lists
# 2. sap_partner_or_book: Published SAP PRESS books, partner books, catalogs
# 3. official_sap_domain: Official SAP web domains (help.sap.com, support.sap.com, learning.sap.com)
# 4. forum: Community blogs, forums, third-party writeups (community.sap.com, blogs.sap.com)
# 5. self_authored: AI-written summaries, 100 Ans files, Q-banks, local cookbooks & architecture summaries, consultant notes

DOCUMENT_TIER_MAPPING: Dict[str, Dict[str, Any]] = {
    # --- Official SAP Documents ---
    "2020_S4H_BRIM_SOM_Device_as_a_Service.pdf": {
        "tier": "official_sap",
        "is_off_domain": False,
        "category": "Official SAP Solution Guide",
        "reason": "Official SAP S/4HANA BRIM SOM Device as a Service publication"
    },
    "BR234_EN_SOM 2.pdf": {
        "tier": "official_sap",
        "is_off_domain": False,
        "category": "Official SAP Training Course",
        "reason": "Official SAP Education courseware BR234 (Subscription Order Management)"
    },
    "BRIM_AC240_EN_Col16.pdf": {
        "tier": "official_sap",
        "is_off_domain": False,
        "category": "Official SAP Training Course",
        "reason": "Official SAP Education courseware AC240 (Contract Accounts Receivable and Payable)"
    },
    "Billing_and_Revenue_Innovation_Management.pdf": {
        "tier": "official_sap",
        "is_off_domain": False,
        "category": "Official SAP Solution Overview",
        "reason": "Official SAP AG publication on Billing and Revenue Innovation Management"
    },
    "SAP CC.pdf": {
        "tier": "official_sap",
        "is_off_domain": False,
        "category": "Official SAP Product Guide",
        "reason": "Official SAP Convergent Charging 2025.1 Implementation Guide (Public)"
    },
    "SAP CI1.pdf": {
        "tier": "official_sap",
        "is_off_domain": True,
        "category": "Official SAP Documentation (Cloud Integration)",
        "reason": "SAP Cloud Integration (CPI) documentation - off-domain for SAP BRIM"
    },
    "SAP CI2.pdf": {
        "tier": "official_sap",
        "is_off_domain": True,
        "category": "Official SAP Documentation (Cloud Integration)",
        "reason": "SAP Cloud Integration (CPI) documentation - off-domain for SAP BRIM"
    },
    "SAP CI3.pdf": {
        "tier": "official_sap",
        "is_off_domain": True,
        "category": "Official SAP Documentation (Cloud Integration)",
        "reason": "SAP Cloud Integration (CPI) documentation - off-domain for SAP BRIM"
    },
    "SAP CI4.pdf": {
        "tier": "official_sap",
        "is_off_domain": True,
        "category": "Official SAP Documentation (Cloud Integration)",
        "reason": "SAP Cloud Integration (CPI) documentation - off-domain for SAP BRIM"
    },
    "mg.pdf": {
        "tier": "official_sap",
        "is_off_domain": False,
        "category": "Official SAP Product Guide",
        "reason": "Official SAP Convergent Charging 4.1 Master Guide (Public)"
    },
    "pdfdownload.pdf": {
        "tier": "official_sap",
        "is_off_domain": False,
        "category": "Official SAP Documentation",
        "reason": "Official SAP Help Portal Subscription Order Management guide"
    },
    "SIMPL_OP1709.pdf": {
        "tier": "official_sap",
        "is_off_domain": True,
        "category": "Official SAP White Paper",
        "reason": "S/4HANA Simplification List (General ERP / non-BRIM specific)"
    },

    # --- SAP Partner or Book ---
    "SAP BRIM Press Book 2nd Edition - Expertsoft.pdf": {
        "tier": "sap_partner_or_book",
        "is_off_domain": False,
        "category": "Published SAP PRESS Book",
        "reason": "SAP PRESS / Expertsoft 2nd Edition published handbook"
    },
    "Authorizations-in-S4-HANA-and-Fiori.pdf": {
        "tier": "sap_partner_or_book",
        "is_off_domain": True,
        "category": "Published Book",
        "reason": "Rheinwerk / SAP PRESS book on Fiori authorizations (off-domain)"
    },
    "E_Book_ABAP_RESTful_Programming_Model_2020_Rel_NW_wwwERPExamsCom.pdf": {
        "tier": "sap_partner_or_book",
        "is_off_domain": True,
        "category": "Published Book",
        "reason": "Rheinwerk book on ABAP RESTful Application Programming Model (off-domain RAP)"
    },
    "SAP-PRESS-Catalog-Shop.pdf": {
        "tier": "sap_partner_or_book",
        "is_off_domain": True,
        "category": "Catalog",
        "reason": "SAP PRESS publications catalog (off-domain)"
    },

    # --- Forum / Community ---
    "Budget billing.pdf": {
        "tier": "forum",
        "is_off_domain": False,
        "category": "Community Technical Guide",
        "reason": "Community procedure on Budget Billing Plan in BRIM/ISU by Vaidehi Rajaram"
    },

    # --- Self-Authored, AI-Written, Summaries, Cookbooks, Q-Banks ---
    "100  Ans.pdf": {
        "tier": "self_authored",
        "is_off_domain": False,
        "category": "AI Summary / Q&A",
        "reason": "Clyptus SAP BRIM Architect 100 Question Answer Book"
    },
    "100 4 ans.pdf": {
        "tier": "self_authored",
        "is_off_domain": False,
        "category": "AI Summary / Q&A",
        "reason": "SAP BRIM Expert Interview Answers 100 Questions"
    },
    "100 Ans 2.pdf": {
        "tier": "self_authored",
        "is_off_domain": False,
        "category": "AI Summary / Q&A",
        "reason": "Clyptus SAP BRIM Architect 100 Question Answer Book Vol 2"
    },
    "SAP BRIM AI Architect.pdf": {
        "tier": "self_authored",
        "is_off_domain": False,
        "category": "AI Summary / Reference Answers",
        "reason": "SAP BRIM AI Architect Reference Answers (AI-authored)"
    },
    "BRIM Q Bank.pdf": {
        "tier": "self_authored",
        "is_off_domain": False,
        "category": "Question Bank",
        "reason": "SAP BRIM Q-Bank collection"
    },
    "SAP_BRIM_End_to_End_Integration_and_SPRO_Cookbook.pdf": {
        "tier": "self_authored",
        "is_off_domain": False,
        "category": "Cookbook Summary",
        "reason": "Locally compiled BRIM SPRO Customizing Cookbook"
    },
    "SAP_BRIM_CC_Convergent_Charging_Advanced_Architecture.pdf": {
        "tier": "self_authored",
        "is_off_domain": False,
        "category": "Architecture Summary",
        "reason": "Locally compiled CC Advanced Architecture guide"
    },
    "SAP_BRIM_Convergent_Invoicing_CIT_BIT_Master_Architecture.pdf": {
        "tier": "self_authored",
        "is_off_domain": False,
        "category": "Architecture Summary",
        "reason": "Locally compiled CI CIT/BIT Architecture guide"
    },
    "SAP_BRIM_FICA_Contract_Accounts_Master_Handbook.pdf": {
        "tier": "self_authored",
        "is_off_domain": False,
        "category": "Architecture Summary",
        "reason": "Locally compiled FI-CA Master Handbook"
    },
    "SAP_BRIM_SOM_Subscription_Order_Management_Master_Guide.pdf": {
        "tier": "self_authored",
        "is_off_domain": False,
        "category": "Architecture Summary",
        "reason": "Locally compiled SOM Master Guide"
    },
    "SAP FI-CA.pdf": {
        "tier": "self_authored",
        "is_off_domain": False,
        "category": "Practitioner Notes",
        "reason": "Practitioner detailed explanation of FI-CA fundamentals"
    },
    "RAR Contract Reversal Process.pdf": {
        "tier": "self_authored",
        "is_off_domain": False,
        "category": "Practitioner Notes",
        "reason": "Practitioner thread/notes on RAR contract reversal process"
    },
    "SAP Revenue Recognition (RAR) Processing Flow, Exemptions, Reversals & System Integration.pdf": {
        "tier": "self_authored",
        "is_off_domain": False,
        "category": "Practitioner Notes",
        "reason": "Practitioner notes on RAR flow and reversals by Moorthy Esakky"
    },

    # --- Locally Generated Non-BRIM Reference Manuals (Off-Domain) ---
    "SAP_ABAP_Development_and_RAP_Standards.pdf": {
        "tier": "self_authored",
        "is_off_domain": True,
        "category": "Synthetic Reference Manual",
        "reason": "ABAP RAP Development standards (off-domain)"
    },
    "SAP_Basis_Administration_and_Security_Handbook.pdf": {
        "tier": "self_authored",
        "is_off_domain": True,
        "category": "Synthetic Reference Manual",
        "reason": "SAP Basis Administration (off-domain)"
    },
    "SAP_CO_Controlling_Configuration_Handbook.pdf": {
        "tier": "self_authored",
        "is_off_domain": True,
        "category": "Synthetic Reference Manual",
        "reason": "SAP CO Controlling (off-domain non-BRIM)"
    },
    "SAP_FI_Financial_Accounting_Guide.pdf": {
        "tier": "self_authored",
        "is_off_domain": True,
        "category": "Synthetic Reference Manual",
        "reason": "SAP General FI Financial Accounting (off-domain non-BRIM)"
    },
    "SAP_Fiori_Design_and_Deployment_Manual.pdf": {
        "tier": "self_authored",
        "is_off_domain": True,
        "category": "Synthetic Reference Manual",
        "reason": "SAP Fiori Design and Deployment (off-domain)"
    },
    "SAP_HCM_Human_Capital_Management_Guide.pdf": {
        "tier": "self_authored",
        "is_off_domain": True,
        "category": "Synthetic Reference Manual",
        "reason": "SAP HCM Human Capital Management (off-domain)"
    },
    "SAP_MM_Materials_Management_Manual.pdf": {
        "tier": "self_authored",
        "is_off_domain": True,
        "category": "Synthetic Reference Manual",
        "reason": "SAP MM Materials Management (off-domain non-BRIM)"
    },
    "SAP_PP_Production_Planning_Reference.pdf": {
        "tier": "self_authored",
        "is_off_domain": True,
        "category": "Synthetic Reference Manual",
        "reason": "SAP PP Production Planning (off-domain)"
    },
    "SAP_S4HANA_Architecture_and_Migration_Guide.pdf": {
        "tier": "self_authored",
        "is_off_domain": True,
        "category": "Synthetic Reference Manual",
        "reason": "General S/4HANA Migration guide (off-domain non-BRIM)"
    },
    "SAP_SD_Sales_and_Distribution_Handbook.pdf": {
        "tier": "self_authored",
        "is_off_domain": True,
        "category": "Synthetic Reference Manual",
        "reason": "SAP SD Sales and Distribution (off-domain non-BRIM)"
    }
}
