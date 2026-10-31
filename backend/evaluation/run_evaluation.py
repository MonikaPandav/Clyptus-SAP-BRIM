import sys
import json
import time
import random
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict

# Ensure sys.path includes project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


from backend.app.database import SessionLocal, init_db
from backend.app.services.rag_service import rag_service
from backend.app.services.retrieval_service import retrieval_service
from backend.app.config import settings
from backend.evaluation.retrieval_evaluator import retrieval_evaluator
from backend.evaluation.grounding_evaluator import grounding_evaluator
from backend.evaluation.citation_evaluator import citation_evaluator
from backend.evaluation.followup_evaluator import followup_evaluator
from backend.evaluation.answer_quality_evaluator import answer_quality_evaluator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("evaluation")

DATASET_DIR = Path(__file__).resolve().parent / "datasets"
RESULTS_PATH = Path(__file__).resolve().parent / "evaluation_results.json"
BASELINE_PATH = Path(__file__).resolve().parent / "baseline_evaluation_results.json"


def load_dataset(split: str = "dev") -> List[Dict[str, Any]]:
    if split == "dev":
        path = DATASET_DIR / "dev_questions.jsonl"
    elif split == "heldout":
        path = DATASET_DIR / "heldout_questions.jsonl"
    else:
        path = DATASET_DIR / "sap_brim_questions.jsonl"

    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items


def bootstrap_ci(values: List[float], n_resamples: int = 1000, alpha: float = 0.05) -> Tuple[float, float, float]:
    """
    Computes 95% bootstrap confidence interval (mean, lower_ci, upper_ci)
    using 1,000 percentile resamples with replacement.
    """
    if not values:
        return 0.0, 0.0, 0.0
    if len(values) == 1:
        v = round(values[0], 4)
        return v, v, v

    mean_val = sum(values) / len(values)
    resample_means = []
    k = len(values)
    for _ in range(n_resamples):
        sample = random.choices(values, k=k)
        resample_means.append(sum(sample) / k)

    resample_means.sort()
    lower_idx = int((alpha / 2.0) * n_resamples)
    upper_idx = int((1.0 - (alpha / 2.0)) * n_resamples) - 1

    lower_ci = resample_means[max(0, lower_idx)]
    upper_ci = resample_means[min(len(resample_means) - 1, upper_idx)]

    return round(mean_val, 4), round(lower_ci, 4), round(upper_ci, 4)


def run_benchmark(sample_size: int = 30, split: str = "dev", save_as_baseline: bool = False) -> Dict[str, Any]:
    """
    Executes benchmark evaluation against the reviewed SAP BRIM dataset.
    Evaluates:
    - Retrieval: Recall@5, Recall@10, MRR
    - Answer Quality: Key-Fact Coverage, Cross-Model LLM-Judge Correctness
    - Faithfulness: Supported, Unsupported, Contradicted claim rates
    - Technical Identifiers: Precision and Recall with explicit denominators stated
    - Correct Refusal Rate: Out-of-scope, false-premise, and unanswerable questions
    - Latency: p50 and p95 in ms
    - Cost: Estimated USD cost per query
    - Statistics: 95% Bootstrap Confidence Intervals across all metrics
    """
    init_db()
    db = SessionLocal()
    dataset = load_dataset(split=split)

    # Prioritize the telecom scenario if in dev split
    telecom_case = next((it for it in dataset if it.get("id") == "hard_scenario_001"), None)

    # Stratified selection across categories
    categories = defaultdict(list)
    for item in dataset:
        cat = item.get("category", "general")
        categories[cat].append(item)

    selected_test_cases = []
    if telecom_case and split == "dev":
        selected_test_cases.append(telecom_case)

    per_cat = max(2, sample_size // len(categories))
    for cat, items in categories.items():
        for item in items:
            if item.get("id") == "hard_scenario_001":
                continue  # already added
            if sum(1 for c in selected_test_cases if c.get("category") == cat) < per_cat:
                selected_test_cases.append(item)

    # Limit to sample_size
    selected_test_cases = selected_test_cases[:max(len(categories), sample_size)]

    logger.info(f"Running evaluation benchmark on {len(selected_test_cases)} representative SAP questions ({split} split)...")

    # Metric lists for aggregation
    rec_at_5_list = []
    rec_at_10_list = []
    mrr_list = []
    key_fact_cov_list = []
    llm_judge_list = []
    supported_rate_list = []
    unsupported_rate_list = []
    contradicted_rate_list = []
    id_precision_list = []
    id_recall_list = []
    refusal_rate_list = []
    latencies = []
    cost_list = []

    # Per-category accumulators
    cat_metrics = defaultdict(lambda: {
        "recall_at_5": [],
        "mrr": [],
        "key_fact_cov": [],
        "llm_judge": [],
        "unsupported_rate": [],
        "id_precision": [],
        "latency_ms": [],
        "count": 0
    })

    evaluated_cases = []

    for idx, case in enumerate(selected_test_cases, 1):
        case_id = case.get("id", f"q_{idx:03d}")
        query = case["query"]
        category = case.get("category", "general")
        kws = case.get("keywords", [])
        gold_chunks = case.get("gold_chunk_ids", [])
        must_cover_facts = case.get("must_cover_key_facts", [])
        ref_answer = case.get("reference_answer", "")
        expected_ids = case.get("expected_identifiers", [])
        is_refusal_exp = case.get("is_refusal_expected", False)

        logger.info(f"[{idx}/{len(selected_test_cases)}] Evaluating [{category}] ({case_id}): '{query[:50]}'...")

        try:
            t0 = time.perf_counter()

            # 1. Retrieval Evaluation
            kb_candidates = retrieval_service.hybrid_search(db, query, top_k=settings.TOP_K)
            ret_res = retrieval_evaluator.evaluate(
                query=query,
                retrieved_chunks=kb_candidates,
                expected_keywords=kws,
                gold_chunk_ids=gold_chunks
            )
            rec_at_5_list.append(ret_res["recall_at_5"])
            rec_at_10_list.append(ret_res["recall_at_10"])
            mrr_list.append(ret_res["mrr"])

            # 2. End-to-end RAG Execution
            rag_resp = rag_service.process_query(db, query)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            latencies.append(elapsed_ms)

            candidate_answer = rag_resp.get("answer", "")
            verification_status = rag_resp.get("verification_status", "verified")

            # 3. Key-Fact Coverage
            cov_res = answer_quality_evaluator.evaluate_key_fact_coverage(
                answer=candidate_answer,
                must_cover_key_facts=must_cover_facts
            )
            key_fact_cov_list.append(cov_res["key_fact_coverage"])

            # 4. LLM Judge Correctness (uses cross-model judge)
            generator_model = rag_resp.get("model_used", "groq")
            judge_res = answer_quality_evaluator.evaluate_llm_judge_correctness(
                query=query,
                reference_answer=ref_answer,
                must_cover_key_facts=must_cover_facts,
                candidate_answer=candidate_answer,
                generator_model=generator_model
            )
            llm_judge_list.append(judge_res["llm_judge_score"])

            # 5. Faithfulness (Supported / Unsupported / Contradicted claim rates)
            faith_res = answer_quality_evaluator.evaluate_faithfulness(rag_resp)
            supported_rate_list.append(faith_res["supported_claim_rate"])
            unsupported_rate_list.append(faith_res["unsupported_claim_rate"])
            contradicted_rate_list.append(faith_res["contradicted_claim_rate"])

            # 6. Technical Identifier Precision & Recall with denominators
            evidence_text = " ".join(
                c.get("snippet", "") + " " + c.get("document", "")
                for c in rag_resp.get("citations", [])
            )
            id_res = answer_quality_evaluator.evaluate_identifiers(
                answer=candidate_answer,
                expected_ids=expected_ids,
                evidence_text=evidence_text
            )
            id_precision_list.append(id_res["identifier_precision"])
            id_recall_list.append(id_res["identifier_recall"])

            # 7. Correct Refusal Rate
            ref_score = answer_quality_evaluator.evaluate_correct_refusal(
                category=category,
                answer=candidate_answer,
                verification_status=verification_status,
                is_refusal_expected=is_refusal_exp
            )
            refusal_rate_list.append(ref_score)

            # 8. Query Cost
            cost = answer_quality_evaluator.estimate_cost(query, candidate_answer, generator_model)
            cost_list.append(cost)

            # Update per-category metrics
            cat_metrics[category]["recall_at_5"].append(ret_res["recall_at_5"])
            cat_metrics[category]["mrr"].append(ret_res["mrr"])
            cat_metrics[category]["key_fact_cov"].append(cov_res["key_fact_coverage"])
            cat_metrics[category]["llm_judge"].append(judge_res["llm_judge_score"])
            cat_metrics[category]["unsupported_rate"].append(faith_res["unsupported_claim_rate"])
            cat_metrics[category]["id_precision"].append(id_res["identifier_precision"])
            cat_metrics[category]["latency_ms"].append(elapsed_ms)
            cat_metrics[category]["count"] += 1

            evaluated_cases.append({
                "id": case_id,
                "category": category,
                "module_tags": case.get("module_tags", []),
                "query": query,
                "latency_ms": round(elapsed_ms, 2),
                "recall_at_5": ret_res["recall_at_5"],
                "recall_at_10": ret_res["recall_at_10"],
                "mrr": ret_res["mrr"],
                "key_fact_coverage": cov_res["key_fact_coverage"],
                "llm_judge_score": judge_res["llm_judge_score"],
                "supported_claim_rate": faith_res["supported_claim_rate"],
                "unsupported_claim_rate": faith_res["unsupported_claim_rate"],
                "identifier_precision": id_res["identifier_precision"],
                "id_precision_den": id_res["identifier_precision_denominator"],
                "identifier_recall": id_res["identifier_recall"],
                "id_recall_den": id_res["identifier_recall_denominator"],
                "correct_refusal": ref_score,
                "cost_usd": cost,
                "source_type": rag_resp.get("source_type"),
                "verification_status": verification_status
            })

            # Polite delay to prevent API token bursts
            time.sleep(1.0)

        except Exception as err:
            logger.error(f"Error evaluating '{query}': {err}", exc_info=True)

    db.close()

    # Aggregate Bootstrap Metrics
    r5_mean, r5_low, r5_high = bootstrap_ci(rec_at_5_list)
    r10_mean, r10_low, r10_high = bootstrap_ci(rec_at_10_list)
    mrr_mean, mrr_low, mrr_high = bootstrap_ci(mrr_list)
    fact_mean, fact_low, fact_high = bootstrap_ci(key_fact_cov_list)
    judge_mean, judge_low, judge_high = bootstrap_ci(llm_judge_list)
    supp_mean, supp_low, supp_high = bootstrap_ci(supported_rate_list)
    unsup_mean, unsup_low, unsup_high = bootstrap_ci(unsupported_rate_list)
    id_p_mean, id_p_low, id_p_high = bootstrap_ci(id_precision_list)
    id_r_mean, id_r_low, id_r_high = bootstrap_ci(id_recall_list)
    ref_mean, ref_low, ref_high = bootstrap_ci(refusal_rate_list)

    latencies_sorted = sorted(latencies)
    p50_lat = latencies_sorted[len(latencies_sorted) // 2] if latencies_sorted else 0.0
    p95_lat = latencies_sorted[int(len(latencies_sorted) * 0.95)] if latencies_sorted else 0.0
    cost_total = sum(cost_list)
    cost_avg = round(cost_total / len(cost_list), 6) if cost_list else 0.0

    final_metrics = {
        "1_Retrieval_Recall_at_5": {"mean": r5_mean, "ci_95": [r5_low, r5_high]},
        "2_Retrieval_Recall_at_10": {"mean": r10_mean, "ci_95": [r10_low, r10_high]},
        "3_Retrieval_MRR": {"mean": mrr_mean, "ci_95": [mrr_low, mrr_high]},
        "4_Key_Fact_Coverage": {"mean": fact_mean, "ci_95": [fact_low, fact_high]},
        "5_LLM_Judge_Correctness": {"mean": judge_mean, "ci_95": [judge_low, judge_high]},
        "6_Supported_Claim_Rate": {"mean": supp_mean, "ci_95": [supp_low, supp_high]},
        "7_Unsupported_Claim_Rate": {"mean": unsup_mean, "ci_95": [unsup_low, unsup_high]},
        "8_Identifier_Precision": {"mean": id_p_mean, "ci_95": [id_p_low, id_p_high], "denominator": "total identifiers in answer"},
        "9_Identifier_Recall": {"mean": id_r_mean, "ci_95": [id_r_low, id_r_high], "denominator": "total expected identifiers"},
        "10_Correct_Refusal_Rate": {"mean": ref_mean, "ci_95": [ref_low, ref_high]},
        "11_Latency_p50_ms": round(p50_lat, 2),
        "12_Latency_p95_ms": round(p95_lat, 2),
        "13_Cost_Per_Query_USD": cost_avg,
        "sample_size": len(selected_test_cases),
        "dataset_split": split
    }

    # Per-Category breakdown
    category_summary = {}
    for cat, d in cat_metrics.items():
        cnt = d["count"]
        if cnt > 0:
            category_summary[cat] = {
                "count": cnt,
                "recall_at_5": round(sum(d["recall_at_5"]) / cnt, 4),
                "mrr": round(sum(d["mrr"]) / cnt, 4),
                "key_fact_coverage": round(sum(d["key_fact_cov"]) / cnt, 4),
                "llm_judge_score": round(sum(d["llm_judge"]) / cnt, 4),
                "unsupported_rate": round(sum(d["unsupported_rate"]) / cnt, 4),
                "id_precision": round(sum(d["id_precision"]) / cnt, 4),
                "latency_p50_ms": round(sorted(d["latency_ms"])[cnt // 2], 2)
            }

    output_payload = {
        "metrics": final_metrics,
        "categories": category_summary,
        "cases": evaluated_cases
    }

    # Save to JSON
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)

    if save_as_baseline or split == "dev":
        with open(BASELINE_PATH, "w", encoding="utf-8") as f:
            json.dump(output_payload, f, indent=2)
        logger.info(f"Saved baseline results to {BASELINE_PATH}")

    # Generate Markdown Table Output
    md_table = generate_markdown_report(final_metrics, category_summary)
    print("\n" + md_table)

    return output_payload


def generate_markdown_report(metrics: Dict[str, Any], categories: Dict[str, Any]) -> str:
    lines = []
    lines.append("### PHASE 0 EVALUATION RESULTS TABLE")
    lines.append(f"**Split:** `{metrics.get('dataset_split')}` | **Sample Size:** {metrics.get('sample_size')} questions | **Bootstrap Iterations:** 1,000")
    lines.append("")
    lines.append("| Metric | Mean | 95% Confidence Interval | Denominator / Basis |")
    lines.append("| :--- | :--- | :--- | :--- |")
    
    ci_fmt = lambda k: f"[{metrics[k]['ci_95'][0]:.4f}, {metrics[k]['ci_95'][1]:.4f}]" if isinstance(metrics.get(k), dict) and "ci_95" in metrics[k] else "-"
    mean_fmt = lambda k: f"{metrics[k]['mean']:.4f}" if isinstance(metrics.get(k), dict) and "mean" in metrics[k] else str(metrics.get(k, "-"))

    lines.append(f"| **Retrieval Recall@5** | `{mean_fmt('1_Retrieval_Recall_at_5')}` | `{ci_fmt('1_Retrieval_Recall_at_5')}` | Gold Chunks in Top 5 |")
    lines.append(f"| **Retrieval Recall@10** | `{mean_fmt('2_Retrieval_Recall_at_10')}` | `{ci_fmt('2_Retrieval_Recall_at_10')}` | Gold Chunks in Top 10 |")
    lines.append(f"| **Retrieval MRR** | `{mean_fmt('3_Retrieval_MRR')}` | `{ci_fmt('3_Retrieval_MRR')}` | First Gold Chunk Rank |")
    lines.append(f"| **Key-Fact Coverage** | `{mean_fmt('4_Key_Fact_Coverage')}` | `{ci_fmt('4_Key_Fact_Coverage')}` | Must-Cover Required Facts |")
    lines.append(f"| **LLM-Judge Correctness** | `{mean_fmt('5_LLM_Judge_Correctness')}` | `{ci_fmt('5_LLM_Judge_Correctness')}` | Cross-Model Judge Score (0-1) |")
    lines.append(f"| **Supported Claim Rate** | `{mean_fmt('6_Supported_Claim_Rate')}` | `{ci_fmt('6_Supported_Claim_Rate')}` | Total Factual Claims |")
    lines.append(f"| **Unsupported Claim Rate** | `{mean_fmt('7_Unsupported_Claim_Rate')}` | `{ci_fmt('7_Unsupported_Claim_Rate')}` | Total Factual Claims |")
    lines.append(f"| **Identifier Precision** | `{mean_fmt('8_Identifier_Precision')}` | `{ci_fmt('8_Identifier_Precision')}` | Total Technical IDs Mentioned |")
    lines.append(f"| **Identifier Recall** | `{mean_fmt('9_Identifier_Recall')}` | `{ci_fmt('9_Identifier_Recall')}` | Total Expected Technical IDs |")
    lines.append(f"| **Correct-Refusal Rate** | `{mean_fmt('10_Correct_Refusal_Rate')}` | `{ci_fmt('10_Correct_Refusal_Rate')}` | Out-of-Scope / False Premise |")
    lines.append(f"| **Latency p50** | `{metrics.get('11_Latency_p50_ms')} ms` | - | Median Response Latency |")
    lines.append(f"| **Latency p95** | `{metrics.get('12_Latency_p95_ms')} ms` | - | 95th Percentile Latency |")
    lines.append(f"| **Cost per Query** | `${metrics.get('13_Cost_Per_Query_USD'):.6f}` | - | API Token Rate Card |")
    lines.append("")
    lines.append("#### Per-Category Performance Breakdown")
    lines.append("")
    lines.append("| Category | Count | Recall@5 | MRR | Key-Fact Cov | LLM Judge | Unsupported Rate | ID Precision | Latency p50 |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for cat, cdata in sorted(categories.items()):
        lines.append(
            f"| `{cat}` | {cdata['count']} | {cdata['recall_at_5']:.2f} | {cdata['mrr']:.2f} | "
            f"{cdata['key_fact_coverage']:.2f} | {cdata['llm_judge_score']:.2f} | "
            f"{cdata['unsupported_rate']:.2f} | {cdata['id_precision']:.2f} | {cdata['latency_p50_ms']:.0f} ms |"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    split_arg = "dev"
    sample_arg = 20
    is_base = False
    if "--split" in sys.argv:
        idx = sys.argv.index("--split")
        if idx + 1 < len(sys.argv):
            split_arg = sys.argv[idx + 1]
    if "--samples" in sys.argv:
        idx = sys.argv.index("--samples")
        if idx + 1 < len(sys.argv):
            sample_arg = int(sys.argv[idx + 1])
    if "--save-baseline" in sys.argv:
        is_base = True

    run_benchmark(sample_size=sample_arg, split=split_arg, save_as_baseline=is_base)
