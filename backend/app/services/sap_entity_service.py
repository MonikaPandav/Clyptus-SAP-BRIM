import re
from typing import Dict, Any, Optional, List

# Curated reference registry of verified SAP BRIM & S/4HANA technical entities
SAP_TECHNICAL_ENTITIES: Dict[str, Dict[str, Any]] = {
    # SAP Convergent Invoicing (CI) T-Codes & Tables
    "/1fe/": {
        "name": "/1FE/ (Class Prefix)",
        "type": "tcode_prefix",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Standard generated transaction code and table prefix for Billable Item (BIT) Classes in SAP Convergent Invoicing.",
        "verified_objects": ["/1FE/BIT_CREATE", "/1FE/BIT_MONITOR", "/1FE/BIT_DISPLAY"]
    },
    "fpc1": {
        "name": "FPC1",
        "type": "tcode",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Create Invoicing Order / Individual Invoicing Run in Convergent Invoicing.",
        "standard_use": "Executes billing and invoicing for selected contract accounts or business partners."
    },
    "fpc2": {
        "name": "FPC2",
        "type": "tcode",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Mass Invoicing Run in Convergent Invoicing.",
        "standard_use": "Executes mass batch processing of billable items into invoicing documents."
    },
    "fpc0": {
        "name": "FPC0",
        "type": "tcode",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Display Invoicing Document in Convergent Invoicing.",
        "standard_use": "Inspects invoicing document headers, items, and linked billing documents."
    },
    "dfkkbict": {
        "name": "DFKKBICT",
        "type": "table",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Billable Items: Control Data and Item Status Table.",
        "key_fields": ["MANDT", "BITCAT", "BITSTATUS", "SRCTYPE"]
    },
    "dfkkbict_it": {
        "name": "DFKKBICT_IT",
        "type": "table",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Billable Item Main Items (IT) Table.",
        "key_fields": ["MANDT", "BITNUMBER", "BITSTATUS", "VKONT", "GPART"]
    },
    "dfkkbict_py": {
        "name": "DFKKBICT_PY",
        "type": "table",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Billable Item Payment Data (PY) Table.",
        "key_fields": ["MANDT", "BITNUMBER", "PY_AMOUNT", "WAERS"]
    },
    "dfkkbict_tx": {
        "name": "DFKKBICT_TX",
        "type": "table",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Billable Item Tax Data (TX) Table.",
        "key_fields": ["MANDT", "BITNUMBER", "TAX_AMOUNT", "TAX_DATE"]
    },
    "fkkbi_class": {
        "name": "FKKBI_CLASS",
        "type": "tcode",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Maintain and Generate Billable Item Classes.",
        "standard_use": "Configures and generates technical structures and database tables for BIT classes."
    },
    "fkkbix_class": {
        "name": "FKKBIX_CLASS",
        "type": "tcode",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Billable Item Class Configuration and Generation.",
        "standard_use": "Central transaction to create, edit, activate, and generate BIT classes in CI."
    },
    "fkkbix_conf": {
        "name": "FKKBIX_CONF",
        "type": "tcode",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Display Configuration of Billable Item Classes.",
        "standard_use": "Inspects generated tables, fields, and interfaces for active BIT classes."
    },
    "fkkbix_bit_mon": {
        "name": "FKKBIX_BIT_MON",
        "type": "tcode",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Billable Item Monitor.",
        "standard_use": "Monitors raw, billable, billed, and excepted billable items across statuses."
    },
    "fkkbix_cit_mon": {
        "name": "FKKBIX_CIT_MON",
        "type": "tcode",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Consumption Item Monitor.",
        "standard_use": "Monitors unrated and rated consumption items received from mediation or Convergent Charging."
    },
    "fkkbix_rate": {
        "name": "FKKBIX_RATE",
        "type": "tcode",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Execute Mass Rating in Convergent Invoicing.",
        "standard_use": "Performs rating runs on consumption items within CI."
    },
    "fkkbix_bill": {
        "name": "FKKBIX_BILL",
        "type": "tcode",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Execute Billing in Convergent Invoicing.",
        "standard_use": "Aggregates billable items into billing documents."
    },
    "fkkbix_inv": {
        "name": "FKKBIX_INV",
        "type": "tcode",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Execute Invoicing in Convergent Invoicing.",
        "standard_use": "Processes invoicing orders and posts legal invoices to FI-CA."
    },
    "fkkbix_bit_disp": {
        "name": "FKKBIX_BIT_DISP",
        "type": "tcode",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Display Single Billable Items.",
        "standard_use": "Displays individual BIT records with all custom and standard fields."
    },
    "dfkkbixbit0": {
        "name": "DFKKBIXBIT0",
        "type": "table",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Billable Items: Raw Status Table (Status 0).",
        "key_fields": ["MANDT", "BITCAT", "BITSTATUS", "BITNUMBER"]
    },
    "dfkkbixbit2": {
        "name": "DFKKBIXBIT2",
        "type": "table",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Billable Items: Billable Status Table (Status 2).",
        "key_fields": ["MANDT", "BITCAT", "BITSTATUS", "BITNUMBER", "VKONT", "GPART"]
    },
    "dfkkbixbit4": {
        "name": "DFKKBIXBIT4",
        "type": "table",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Billable Items: Billed/Invoiced Status Table (Status 4).",
        "key_fields": ["MANDT", "BITCAT", "BITSTATUS", "BITNUMBER", "INVDOCNO"]
    },
    "dfkkbixcit0": {
        "name": "DFKKBIXCIT0",
        "type": "table",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Consumption Items: Raw / Unrated Table.",
        "key_fields": ["MANDT", "CITCAT", "CITSTATUS", "CITNUMBER"]
    },
    "dfkkbixcit1": {
        "name": "DFKKBIXCIT1",
        "type": "table",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Consumption Items: Rated Table.",
        "key_fields": ["MANDT", "CITCAT", "CITSTATUS", "CITNUMBER"]
    },
    "dfkkinv_ord": {
        "name": "DFKKINV_ORD",
        "type": "table",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Invoicing Orders Trigger Table.",
        "key_fields": ["MANDT", "SRCDOCTYPE", "SRCDOCNO"]
    },
    "dfkkinv_doc": {
        "name": "DFKKINV_DOC",
        "type": "table",
        "component": "SAP Convergent Invoicing (CI)",
        "description": "Invoicing Document Master Table.",
        "key_fields": ["MANDT", "INVDOCNO", "VKONT", "GPART"]
    },

    # SAP FI-CA (Contract Accounts Receivable and Payable)
    "fpl9": {
        "name": "FPL9",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Account Balance Display (Contract Account Overview).",
        "standard_use": "Central 360-degree transaction displaying all open items, cleared items, invoices, and payments for a contract account."
    },
    "fpma": {
        "name": "FPMA",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Automatic Clearing Run in FI-CA.",
        "standard_use": "Mass batch clearing of open debits and credits based on configured clearing variants."
    },
    "fprel": {
        "name": "FPREL",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Release Open Items for Dunning / Payment.",
        "standard_use": "Releases payment or dunning locks on open receivables."
    },
    "fpci": {
        "name": "FPCI",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Clarification Processing in FI-CA.",
        "standard_use": "Investigates payment lots or invoicing exceptions in clarification worklists."
    },
    "fpg1": {
        "name": "FPG1",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Transfer to General Ledger (FI-CA to FI-GL).",
        "standard_use": "Posts closed reconciliation keys as summary postings to general ledger accounts."
    },
    "fpg4": {
        "name": "FPG4",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Reconciliation Key Display and Processing.",
        "standard_use": "Inspects status, totals, and G/L transfer status of FI-CA reconciliation keys."
    },
    "fp08": {
        "name": "FP08",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Reverse Document in FI-CA.",
        "standard_use": "Reverses individual FI-CA accounting documents and restores cleared items."
    },
    "fpcopara": {
        "name": "FPCOPARA",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Correspondence Run in FI-CA.",
        "standard_use": "Mass output processing for invoices, account statements, and dunning letters."
    },
    "fpe1": {
        "name": "FPE1",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Post Document in FI-CA.",
        "standard_use": "Manual posting of financial documents into contract accounts."
    },
    "fpe2": {
        "name": "FPE2",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Change Document in FI-CA.",
        "standard_use": "Modifies open item line item attributes (e.g. payment terms, dunning locks)."
    },
    "fpe3": {
        "name": "FPE3",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Display Document in FI-CA.",
        "standard_use": "Inspects document header (DFKKKO) and line items (DFKKOP)."
    },
    "fp05": {
        "name": "FP05",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Payment Lot Processing in FI-CA.",
        "standard_use": "Processes incoming customer bank payments and clearing of open items."
    },
    "fpva": {
        "name": "FPVA",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Dunning Proposal Run in FI-CA.",
        "standard_use": "Evaluates overdue open items and proposes dunning levels."
    },
    "fpvb": {
        "name": "FPVB",
        "type": "tcode",
        "component": "SAP FI-CA",
        "description": "Dunning Activity Run in FI-CA.",
        "standard_use": "Executes dunning actions, generates dunning fees, interest, and letters."
    },
    "dfkkko": {
        "name": "DFKKKO",
        "type": "table",
        "component": "SAP FI-CA",
        "description": "FI-CA Document Header Table.",
        "key_fields": ["MANDT", "OPBEL", "FIKEY", "BLDAT", "BUDAT"]
    },
    "dfkkop": {
        "name": "DFKKOP",
        "type": "table",
        "component": "SAP FI-CA",
        "description": "FI-CA Contract Account Document: Line Item Table (Open Items).",
        "key_fields": ["MANDT", "OPBEL", "OPUPK", "OPUPW", "OPUPZ", "VKONT", "GPART", "BETRW"]
    },
    "dfkkopk": {
        "name": "DFKKOPK",
        "type": "table",
        "component": "SAP FI-CA",
        "description": "FI-CA Document: General Ledger Items.",
        "key_fields": ["MANDT", "OPBEL", "OPUPK", "HKONT", "BETRW"]
    },
    "erdk": {
        "name": "ERDK",
        "type": "table",
        "component": "SAP Invoicing",
        "description": "Print Document Header Table.",
        "key_fields": ["MANDT", "OPBEL", "PRINTDOCNO"]
    },
    "erch": {
        "name": "ERCH",
        "type": "table",
        "component": "SAP Billing",
        "description": "Billing Document Lines / Master Table.",
        "key_fields": ["MANDT", "BELNR", "BUKRS"]
    },

    # SOM & Subscription Management
    "crmd_order": {
        "name": "CRMD_ORDER",
        "type": "tcode",
        "component": "SAP Subscription Order Management (SOM)",
        "description": "Maintain Business Transactions / Provider Orders.",
        "standard_use": "Creates and maintains subscription provider orders and provider contracts in SOM."
    },
    "com_product": {
        "name": "COM_PRODUCT",
        "type": "tcode",
        "component": "SAP SOM",
        "description": "Product Master Maintenance.",
        "standard_use": "Maintains subscription products, bundles, and cross-catalog mapping to CC charge plans."
    },
    "wty_claim": {
        "name": "WTY_CLAIM",
        "type": "tcode",
        "component": "SAP SOM / Warranty",
        "description": "Warranty and Allowance Claims Processing.",
        "standard_use": "Processes allowance adjustments and usage warranty claims."
    },

    # RAR & S/4HANA Revenue Accounting
    "farr_rai_mon": {
        "name": "FARR_RAI_MON",
        "type": "tcode",
        "component": "SAP RAR",
        "description": "Revenue Accounting Item (RAI) Monitor.",
        "standard_use": "Monitors order, invoice, and fulfillment RAIs for IFRS 15 revenue recognition."
    },

    # Basis & Administration
    "slg1": {
        "name": "SLG1",
        "type": "tcode",
        "component": "SAP Basis",
        "description": "Application Log: Display Logs.",
        "standard_use": "Inspects execution logs, billing errors, and batch job diagnostics across BRIM components."
    },
    "sm59": {
        "name": "SM59",
        "type": "tcode",
        "component": "SAP Basis",
        "description": "RFC Destinations (Display and Maintain).",
        "standard_use": "Configures TCP/IP and ABAP RFC connections between S/4HANA, Convergent Charging, and mediation."
    },
    "we02": {
        "name": "WE02",
        "type": "tcode",
        "component": "SAP Basis",
        "description": "IDoc List / Monitor.",
        "standard_use": "Inspects status of inbound and outbound IDocs in integration scenarios."
    },
    "st05": {
        "name": "ST05",
        "type": "tcode",
        "component": "SAP Basis",
        "description": "Performance Analysis / SQL Trace.",
        "standard_use": "Traces database accesses, buffer hits, and SQL performance for high-volume billing runs."
    },
    "st22": {
        "name": "ST22",
        "type": "tcode",
        "component": "SAP Basis",
        "description": "ABAP Dump Analysis.",
        "standard_use": "Inspects short dumps and runtime exceptions in custom BAdIs or standard billing programs."
    },
    "f110": {
        "name": "F110",
        "type": "tcode",
        "component": "SAP Financial Accounting",
        "description": "Automatic Payment Program.",
        "standard_use": "Executes mass payment runs for standard accounts payable and receivable."
    },

    # Master Data Entities
    "but000": {
        "name": "BUT000",
        "type": "table",
        "component": "SAP Master Data (BP)",
        "description": "Business Partner General Data Table (Central Header).",
        "key_fields": ["CLIENT", "PARTNER", "TYPE", "NAME_FIRST", "NAME_LAST"]
    },
    "but020": {
        "name": "BUT020",
        "type": "table",
        "component": "SAP Master Data (BP)",
        "description": "Business Partner Addresses Table.",
        "key_fields": ["CLIENT", "PARTNER", "ADDRNUMBER"]
    },
    "fkkvkp": {
        "name": "FKKVKP",
        "type": "table",
        "component": "SAP FI-CA",
        "description": "Contract Account Header and Partner-Specific Data.",
        "key_fields": ["MANDT", "VKONT", "GPART"]
    },

    # Core ERP Transactions
    "me21n": {
        "name": "ME21N",
        "type": "tcode",
        "component": "SAP MM",
        "description": "Create Purchase Order.",
        "standard_use": "Purchasing transaction for procurement orders in SAP ERP / S/4HANA."
    },
    "migo": {
        "name": "MIGO",
        "type": "tcode",
        "component": "SAP MM",
        "description": "Goods Movement (Goods Receipt / Issue).",
        "standard_use": "Processes inventory movements and posts warehouse receipts."
    },
    "miro": {
        "name": "MIRO",
        "type": "tcode",
        "component": "SAP MM / FI",
        "description": "Enter Incoming Invoice (Logistics Invoice Verification).",
        "standard_use": "Performs 3-Way Match validation against Purchase Order and Goods Receipt."
    },
    "sm30": {
        "name": "SM30",
        "type": "tcode",
        "component": "SAP Basis / Customizing",
        "description": "Call View Maintenance.",
        "standard_use": "Maintains configuration tables and views defined in ABAP Dictionary."
    },
    "sm37": {
        "name": "SM37",
        "type": "tcode",
        "component": "SAP Basis",
        "description": "Overview of Background Jobs.",
        "standard_use": "Monitors and schedules batch background jobs for billing, invoicing, and clearing."
    },
    "se16": {
        "name": "SE16",
        "type": "tcode",
        "component": "SAP Basis",
        "description": "Data Browser.",
        "standard_use": "Displays database table contents and records."
    },
    "se16n": {
        "name": "SE16N",
        "type": "tcode",
        "component": "SAP Basis",
        "description": "General Table Display.",
        "standard_use": "Interactive browser for ABAP database tables."
    },
    "spro": {
        "name": "SPRO",
        "type": "tcode",
        "component": "SAP Customizing",
        "description": "Customizing - Edit Project / SAP Reference IMG.",
        "standard_use": "Central entry transaction for all SAP configuration and IMG paths."
    }
}


class SAPEntityService:
    """Provides entity lookups for documented SAP T-codes, tables, and BRIM components."""

    @staticmethod
    def lookup_entity(identifier: str) -> Optional[Dict[str, Any]]:
        clean_id = identifier.lower().strip()
        # Direct match
        if clean_id in SAP_TECHNICAL_ENTITIES:
            return SAP_TECHNICAL_ENTITIES[clean_id]
        # Prefix match (e.g. for /1FE/ classes)
        for key, entry in SAP_TECHNICAL_ENTITIES.items():
            if clean_id.startswith(key):
                return entry
        return None

    @staticmethod
    def is_known_sap_identifier(identifier: str) -> bool:
        clean_id = identifier.lower().strip()
        if clean_id in SAP_TECHNICAL_ENTITIES:
            return True
        for key in SAP_TECHNICAL_ENTITIES:
            if clean_id.startswith(key):
                return True
        return False


sap_entity_service = SAPEntityService()
