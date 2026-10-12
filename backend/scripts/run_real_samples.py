import json
import time
import logging
from pathlib import Path

from backend.app.database import SessionLocal, init_db
from backend.app.services.retrieval_service import retrieval_service
from backend.app.services.context_packing_service import context_packing_service
from backend.app.services.grounded_generator_service import grounded_generator_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QUESTIONS = [
    {
        "key": "a_hard_scenario_001",
        "label": "a) hard_scenario_001 (telecom activation fee / usage / FI-CA)",
        "query": "A telecom customer has a subscription with INR 799 monthly recurring fee, INR 299 one-time activation fee, and INR 5/GB for usage beyond a 150 GB allowance. During end-of-month processing, some customers were billed the activation fee twice, high-usage data was miscalculated, and the final invoices failed to post to FI-CA. Explain the root causes across SOM, CC, CI, and FI-CA, how to diagnose them, and how to remediate the billing run without duplicating already-billed charges."
    },
    {
        "key": "b_mid_cycle_upgrade",
        "label": "b) Mid-Cycle Upgrade Contract Synchronization",
        "query": "A customer upgrades their subscription plan mid-cycle from Basic (50GB) to Enterprise (500GB). Walk through the end-to-end data flow and contract synchronization across SOM, CC, and CI."
    },
    {
        "key": "c_false_premise_cc_to_fica",
        "label": "c) False Premise: CC posts usage directly to FI-CA",
        "query": "Explain how CC posts usage directly to FI-CA so CI isn't needed."
    },
    {
        "key": "d_fabricated_table",
        "label": "d) Fabricated Table: DFKKBILLRATE_X",
        "query": "What does table DFKKBILLRATE_X store?"
    },
    {
        "key": "e_rar_smartphone_bundle",
        "label": "e) Smartphone bundle RAR allocation (IFRS 15)",
        "query": "A customer purchases a smartphone bundle consisting of a device (standalone selling price INR 30,000, sold for INR 6,000 upfront) and a 24-month subscription service (INR 999/month, standalone selling price INR 1,299/month). Explain how SAP RAR allocates the transaction price across performance obligations under IFRS 15, and calculate the allocated revenue for the device and service."
    }
]


def execute_samples():
    init_db()
    db = SessionLocal()

    results = []

    for q_meta in QUESTIONS:
        key = q_meta["key"]
        label = q_meta["label"]
        query = q_meta["query"]

        logger.info(f"Processing query: {label}")
        start_t = time.time()

        # 1. Real Retrieval
        raw_chunks = retrieval_service.hybrid_search(db, query, top_k=15)

        retrieved_summary = []
        for c in raw_chunks:
            retrieved_summary.append({
                "chunk_id": str(c.get("chunk_id")),
                "tier": context_packing_service.infer_chunk_tier(c),
                "module": context_packing_service.infer_chunk_module(c),
                "document": c.get("document_name"),
                "page": c.get("page_number"),
                "relevance_score": round(float(c.get("score") or c.get("rerank_score") or 0.0), 4)
            })

        # 2. Context Packing
        packing = context_packing_service.pack_context(query, raw_chunks)

        # 3. Grounded Generator
        gen_res = grounded_generator_service.generate_grounded_answer(query, packing)
        total_time_ms = round((time.time() - start_t) * 1000, 2)

        results.append({
            "key": key,
            "label": label,
            "query": query,
            "latency_ms": total_time_ms,
            "model_name": gen_res.get("model_used"),
            "status": gen_res.get("status"),
            "token_count": gen_res.get("token_count"),
            "computed_modules_covered": gen_res.get("computed_modules_covered"),
            "retrieved_chunks": retrieved_summary[:6],
            "packed_chunks_count": len(packing.packed_chunks),
            "packed_context": packing.packed_text,
            "raw_json": gen_res.get("raw_json"),
            "answer_response": gen_res.get("answer_response").model_dump()
        })

    db.close()

    out_file = Path(__file__).resolve().parent.parent / "evaluation" / "results" / "real_sample_executions.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    logger.info(f"Results written to: {out_file}")
    return results


if __name__ == "__main__":
    execute_samples()
