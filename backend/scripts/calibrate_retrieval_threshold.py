import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

from backend.app.database import SessionLocal, init_db
from backend.app.services.retrieval_service import retrieval_service
from backend.app.services.reranking_service import reranking_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_threshold_calibration() -> Dict[str, Any]:
    """
    Evaluates retrieval score distributions across the dev split (answerable vs unanswerable)
    and computes the optimal calibrated retrieval threshold.
    """
    init_db()
    db = SessionLocal()

    dataset_path = Path(__file__).resolve().parent.parent / "evaluation" / "datasets" / "dev_questions.jsonl"
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dev dataset not found at: {dataset_path}")

    answerable_scores: List[float] = []
    unanswerable_scores: List[float] = []

    answerable_items = []
    unanswerable_items = []

    logger.info("Reading dev split questions...")
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            cat = item.get("category", "")
            is_unanswerable = (
                cat in ("corpus_cannot_answer", "hallucination_trap", "out_of_scope_refusal")
                or item.get("is_refusal_expected", False)
            )

            query = item["query"]
            chunks = retrieval_service.hybrid_search(db, query, top_k=20)
            top_score = 0.0
            if chunks:
                top_score = float(chunks[0].get("score") or chunks[0].get("rerank_score") or chunks[0].get("similarity") or 0.0)

            if is_unanswerable:
                unanswerable_scores.append(top_score)
                unanswerable_items.append({"id": item.get("id"), "query": query, "top_score": top_score, "category": cat})
            else:
                answerable_scores.append(top_score)
                answerable_items.append({"id": item.get("id"), "query": query, "top_score": top_score, "category": cat})

    db.close()

    ans_arr = np.array(answerable_scores)
    unans_arr = np.array(unanswerable_scores)

    def stats(arr: np.ndarray) -> Dict[str, float]:
        if len(arr) == 0:
            return {}
        return {
            "count": int(len(arr)),
            "mean": float(np.round(np.mean(arr), 4)),
            "std": float(np.round(np.std(arr), 4)),
            "min": float(np.round(np.min(arr), 4)),
            "p10": float(np.round(np.percentile(arr, 10), 4)),
            "p25": float(np.round(np.percentile(arr, 25), 4)),
            "median": float(np.round(np.median(arr), 4)),
            "p75": float(np.round(np.percentile(arr, 75), 4)),
            "p90": float(np.round(np.percentile(arr, 90), 4)),
            "max": float(np.round(np.max(arr), 4))
        }

    ans_stats = stats(ans_arr)
    unans_stats = stats(unans_arr)

    # Threshold sweep from min observed to max observed
    all_scores = np.concatenate([ans_arr, unans_arr])
    threshold_candidates = np.linspace(np.min(all_scores), np.max(all_scores), 100)

    best_threshold = 0.45
    best_f1 = 0.0
    best_metrics = {}

    sweep_results = []
    for th in threshold_candidates:
        # True Positive: Answerable with score >= threshold
        tp = int(np.sum(ans_arr >= th))
        # False Negative: Answerable with score < threshold (incorrectly abstained)
        fn = int(np.sum(ans_arr < th))
        # True Negative: Unanswerable with score < threshold (correctly abstained)
        tn = int(np.sum(unans_arr < th))
        # False Positive: Unanswerable with score >= threshold (hallucination risk)
        fp = int(np.sum(unans_arr >= th))

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        balanced_acc = (recall + specificity) / 2.0

        sweep_results.append({
            "threshold": float(np.round(th, 4)),
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": float(np.round(precision, 4)),
            "recall": float(np.round(recall, 4)),
            "f1": float(np.round(f1, 4)),
            "balanced_accuracy": float(np.round(balanced_acc, 4))
        })

        if f1 > best_f1:
            best_f1 = f1
            best_threshold = float(np.round(th, 4))
            best_metrics = {
                "threshold": best_threshold,
                "precision": float(np.round(precision, 4)),
                "recall": float(np.round(recall, 4)),
                "f1": float(np.round(f1, 4)),
                "specificity": float(np.round(specificity, 4)),
                "balanced_accuracy": float(np.round(balanced_acc, 4))
            }

    report = {
        "dataset": "dev_questions.jsonl",
        "total_questions": int(len(ans_arr) + len(unans_arr)),
        "answerable_count": int(len(ans_arr)),
        "unanswerable_count": int(len(unans_arr)),
        "answerable_distribution": ans_stats,
        "unanswerable_distribution": unans_stats,
        "recommended_calibrated_threshold": best_threshold,
        "optimal_metrics": best_metrics
    }

    out_dir = Path(__file__).resolve().parent.parent / "evaluation" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "threshold_calibration_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info(f"Calibration report saved to: {out_path}")

    return report


if __name__ == "__main__":
    rep = run_threshold_calibration()
    print("\n================ THRESHOLD CALIBRATION REPORT ================")
    print(f"Total dev questions: {rep['total_questions']} (Answerable: {rep['answerable_count']}, Unanswerable: {rep['unanswerable_count']})")
    print(f"\nAnswerable Top Score Stats:")
    print(f"  Mean: {rep['answerable_distribution']['mean']} | Median: {rep['answerable_distribution']['median']} | P10: {rep['answerable_distribution']['p10']} | Max: {rep['answerable_distribution']['max']}")
    print(f"\nUnanswerable Top Score Stats:")
    print(f"  Mean: {rep['unanswerable_distribution']['mean']} | Median: {rep['unanswerable_distribution']['median']} | P90: {rep['unanswerable_distribution']['p90']} | Min: {rep['unanswerable_distribution']['min']}")
    print(f"\nRecommended Calibrated Threshold: {rep['recommended_calibrated_threshold']}")
    print(f"Metrics at Calibrated Threshold: {rep['optimal_metrics']}")
    print("===============================================================\n")
