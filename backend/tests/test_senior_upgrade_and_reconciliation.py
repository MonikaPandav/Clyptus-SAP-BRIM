"""
Tests for Senior-Level SAP BRIM Upgrade and Invoice Reconciliation Response Quality.
Verifies archetype planning, diagnostic reasoning requirements, data model integrity,
safeguards, and technical classification rules.
"""

import pytest
from backend.app.services.answer_planner import answer_planner
from backend.app.services.llm_service import SYSTEM_PROMPT
from backend.app.services.grounding_service import grounding_service, VERIFIED_STANDARD_SAP_OBJECTS


# ==============================================================================
# 1. ARCHETYPE PLANNING & QUERY DETECTION TESTS
# ==============================================================================

def test_invoice_reconciliation_query_triggers_dedicated_archetype():
    """Verify invoice reconciliation questions trigger the dedicated senior archetype."""
    queries = [
        "How do we perform end-to-end invoice reconciliation in SAP BRIM after an upgrade?",
        "We are seeing billing discrepancies and invoice variances between our old and new release.",
        "A customer upgrade resulted in an invoice mismatch; how do we build a stage-by-stage reconciliation matrix?",
        "Explain how to diagnose billing difference and invoice amount variances across CI and FI-CA.",
        "What are the steps to reconcile billable items and invoicing documents after a Support Package upgrade?"
    ]
    for q in queries:
        plan = answer_planner.plan_answer(q)
        assert plan["question_type"] == "upgrade_invoice_reconciliation"
        assert "Senior SAP BRIM Upgrade & Invoice Reconciliation" in plan["title"]


def test_reconciliation_archetype_mandates_all_required_sections():
    """Verify the archetype instructions explicitly mandate all 7 required sections."""
    plan = answer_planner.plan_answer("Explain invoice reconciliation across CI and FI-CA during an upgrade")
    instructions = plan["instructions"]

    required_sections = [
        "Executive Summary",
        "Symptom Classification",
        "Stage-by-Stage Reconciliation Matrix",
        "Release and Configuration Comparison",
        "Root-Cause Decision Tree",
        "Safe Validation and Remediation",
        "Evidence-Based Conclusion"
    ]
    for sec in required_sections:
        assert sec in instructions, f"Mandatory section '{sec}' missing from archetype instructions"


def test_symptom_classification_covers_all_seven_stages():
    """Verify symptom classification establishes divergence across all 7 documented stages."""
    plan = answer_planner.plan_answer("Invoice reconciliation discrepancy between old and new releases")
    instructions = plan["instructions"]

    assert "Usage Volume" in instructions
    assert "Rating" in instructions
    assert "Billable Items" in instructions
    assert "Invoicing Aggregation" in instructions
    assert "Tax Calculation" in instructions
    assert "Rounding" in instructions
    assert "FI-CA Subledger Posting" in instructions


def test_reconciliation_matrix_format_and_stable_identifier_matching():
    """Verify stage-by-stage matrix and granular stable-identifier record matching are required."""
    plan = answer_planner.plan_answer("Perform invoice reconciliation for upgraded provider contracts")
    instructions = plan["instructions"]

    # Matrix table structure
    assert "Reconciliation Matrix" in instructions
    assert "Processing Stage" in instructions
    assert "Input Records" in instructions
    assert "Output Records" in instructions

    # Stable identifier matching vs aggregate totals
    assert "stable identifiers" in instructions.lower()
    assert "not only aggregate totals" in instructions.lower()
    assert "offsetting discrepancies" in instructions.lower()


def test_sd_and_bw_data_model_safeguard():
    """Verify data model safeguard forbids assuming VBRK/VBRP or /BIC/* for CI or FI-CA."""
    plan = answer_planner.plan_answer("Invoice variance between S/4HANA releases in BRIM billing")
    instructions = plan["instructions"]

    assert "VBRK/VBRP" in instructions
    assert "/BIC/*" in instructions
    assert "DFKKBIXBIT*" in instructions
    assert "DFKKINVDOC*" in instructions


def test_controlled_testing_and_replay_safeguards():
    """Verify controlled old-vs-new testing and duplicate-processing safeguards are mandated."""
    plan = answer_planner.plan_answer("Reconciliation of billing differences across releases")
    instructions = plan["instructions"]

    assert "old-versus-new release testing" in instructions
    assert "identical inputs" in instructions
    assert "financial-side-effect safeguards" in instructions


def test_four_tier_technical_classification_mandated():
    """Verify archetype instructions enforce the four-tier technical classification."""
    plan = answer_planner.plan_answer("Reconcile billing discrepancies after upgrade")
    instructions = plan["instructions"]

    assert "[Verified SAP-Standard Functionality]" in instructions
    assert "[Customer-Specific Configuration or Custom Implementation]" in instructions
    assert "[General Testing Recommendations]" in instructions
    assert "[Hypotheses That Still Require Verification]" in instructions


# ==============================================================================
# 2. SYSTEM_PROMPT SENIOR GUIDELINES INTEGRITY TESTS
# ==============================================================================

def test_system_prompt_contains_senior_reconciliation_principles():
    """Verify system prompt in llm_service contains senior diagnostic & reconciliation methodology."""
    assert "Senior Upgrade & Invoice Reconciliation Methodology" in SYSTEM_PROMPT
    assert "Symptom Classification" in SYSTEM_PROMPT
    assert "Stage-by-Stage Reconciliation Matrix" in SYSTEM_PROMPT
    assert "Granular Record Matching" in SYSTEM_PROMPT
    assert "VBRK/VBRP" in SYSTEM_PROMPT
    assert "/BIC/*" in SYSTEM_PROMPT
    assert "financial-side-effect safeguards" in SYSTEM_PROMPT


def test_system_prompt_mandates_four_tier_classification():
    """Verify system prompt mandates the exact 4-tier classification."""
    assert "[Verified SAP-Standard Functionality]" in SYSTEM_PROMPT
    assert "[Customer-Specific Configuration or Custom Implementation]" in SYSTEM_PROMPT
    assert "[General Testing Recommendations]" in SYSTEM_PROMPT
    assert "[Hypotheses That Still Require Verification]" in SYSTEM_PROMPT


# ==============================================================================
# 3. GROUNDING GATE RECONCILIATION OBJECT VERIFICATION TESTS
# ==============================================================================

def test_grounding_service_recognizes_standard_ci_and_fica_reconciliation_objects():
    """Verify standard CI and FI-CA tables and transactions pass technical verification."""
    standard_objects = [
        "fkkbix_bill_m",
        "fkkbix_inv_m",
        "fpc1",
        "fpc0",
        "dfkkinvdoc_h",
        "dfkkbilldoc_h",
        "dfkkbixbit0",
        "dfkkko",
        "dfkkop"
    ]
    for obj in standard_objects:
        assert obj in VERIFIED_STANDARD_SAP_OBJECTS, f"Object {obj} should be in verified standard SAP objects"


def test_grounding_service_rejects_fabricated_reconciliation_table():
    """Verify fabricated tables (e.g. DFKKBILLRATE_X) fail the technical identifier audit."""
    assert "dfkkbillrate_x" not in VERIFIED_STANDARD_SAP_OBJECTS
    res = grounding_service.verify_answer(
        query="Explain table DFKKBILLRATE_X",
        answer="Table DFKKBILLRATE_X stores billing rate variances between old and new releases.",
        evidence_passages=[{"chunk_text": "SAP Convergent Invoicing processes billable items."}],
        source_type="knowledge_base"
    )
    assert res["passes_grounding_gate"] is False
    assert "dfkkbillrate_x" in res["critical_unsupported_claims"] or len(res["unsupported_claims"]) > 0
