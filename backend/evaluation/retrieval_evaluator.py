import re
from typing import List, Dict, Any, Optional

class RetrievalEvaluator:
    """Evaluates retrieval performance: Recall@5, Recall@10, MRR, Context Precision, and Context Recall."""

    @staticmethod
    def evaluate(
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        expected_keywords: List[str],
        gold_chunk_ids: Optional[List[str]] = None
    ) -> Dict[str, float]:
        if not retrieved_chunks:
            return {
                "recall_at_5": 0.0,
                "recall_at_10": 0.0,
                "mrr": 0.0,
                "context_precision": 0.0,
                "context_recall": 0.0
            }

        retrieved_ids = [c.get("chunk_id") for c in retrieved_chunks if c.get("chunk_id")]
        top_5 = retrieved_chunks[:5]
        top_10 = retrieved_chunks[:10]
        top_5_ids = [c.get("chunk_id") for c in top_5 if c.get("chunk_id")]
        top_10_ids = [c.get("chunk_id") for c in top_10 if c.get("chunk_id")]

        # 1. Gold Chunk Recall@5 & Recall@10
        if gold_chunk_ids:
            clean_gold = [gid for gid in gold_chunk_ids if gid]
            if clean_gold:
                matched_5 = sum(1 for gid in clean_gold if gid in top_5_ids)
                recall_at_5 = matched_5 / len(clean_gold)
                matched_10 = sum(1 for gid in clean_gold if gid in top_10_ids)
                recall_at_10 = matched_10 / len(clean_gold)

                # MRR (Mean Reciprocal Rank)
                mrr = 0.0
                for rank, cid in enumerate(retrieved_ids, 1):
                    if cid in clean_gold:
                        mrr = 1.0 / rank
                        break
            else:
                recall_at_5 = 1.0
                recall_at_10 = 1.0
                mrr = 1.0
        else:
            # Keyword fallback if gold chunk IDs not provided
            top_5_text = " ".join((c.get("chunk_text") or c.get("snippet") or "").lower() for c in top_5)
            matched_kws = sum(1 for kw in expected_keywords if kw.lower() in top_5_text)
            recall_at_5 = matched_kws / max(1, len(expected_keywords))
            recall_at_10 = recall_at_5
            mrr = 1.0 if recall_at_5 > 0 else 0.0

        # 2. Context Precision & Recall
        all_text = " ".join((c.get("chunk_text") or c.get("snippet") or "").lower() for c in retrieved_chunks)
        matched_total = sum(1 for kw in expected_keywords if kw.lower() in all_text)
        context_recall = matched_total / max(1, len(expected_keywords))

        relevant_chunks_in_top5 = 0
        for c in top_5:
            c_text = (c.get("chunk_text") or c.get("snippet") or "").lower()
            if any(kw.lower() in c_text for kw in expected_keywords):
                relevant_chunks_in_top5 += 1
        context_precision = relevant_chunks_in_top5 / len(top_5) if top_5 else 0.0

        return {
            "recall_at_5": round(recall_at_5, 4),
            "recall_at_10": round(recall_at_10, 4),
            "mrr": round(mrr, 4),
            "context_precision": round(context_precision, 4),
            "context_recall": round(context_recall, 4)
        }

retrieval_evaluator = RetrievalEvaluator()
