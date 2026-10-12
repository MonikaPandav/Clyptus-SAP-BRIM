import os
import sys
import time
from pathlib import Path

# Add project root to path
backend_dir = Path(__file__).resolve().parent
root_dir = backend_dir.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(backend_dir))

from backend.app.database import SessionLocal
from backend.app.services.rag_service import rag_service
from backend.app.services.sap_classifier import sap_classifier
from backend.app.services.query_rewriter import query_rewriter
from backend.app.services.embedding_service import embedding_service
from backend.app.services.retrieval_service import retrieval_service
from backend.app.services.reranking_service import reranking_service
from backend.app.services.evidence_selection_service import evidence_selection_service
from backend.app.services.grounding_service import grounding_service

def run_measurements():
    db = SessionLocal()
    print("=" * 60)
    print("MEASURING COMPONENT LATENCY BREAKDOWN (POST-OPTIMIZATION)")
    print("=" * 60)

    # 1. Warm-up
    q_warm = "What is SAP Convergent Charging?"
    _ = embedding_service.embed_text(q_warm)
    _ = retrieval_service.hybrid_search(db, q_warm, top_k=20)

    queries = [
        "What is SAP BRIM and its core architecture?",
        "How does Convergent Invoicing process billable items into invoicing documents?",
        "Explain the integration between SOM, CC, CI, and FI-CA in SAP BRIM.",
        "What are the key database tables in SAP Convergent Invoicing: DFKKBIXBIT2 and DFKKBIXBIT4?",
        "How does real-time rating work in Convergent Charging compared to batch rating?"
    ]

    embed_times = []
    retrieval_times = []
    cached_retrieval_times = []
    rerank_times = []
    evidence_times = []

    for q in queries:
        t0 = time.perf_counter()
        _ = sap_classifier.classify(q)
        t_class = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        _ = query_rewriter.resolve_query(q)
        t_rewrite = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        _ = embedding_service.embed_text(q)
        t_embed = (time.perf_counter() - t0) * 1000
        embed_times.append(t_embed)

        t0 = time.perf_counter()
        candidates = retrieval_service.hybrid_search(db, q, top_k=50)
        t_ret = (time.perf_counter() - t0) * 1000
        retrieval_times.append(t_ret)

        # Measure cached retrieval
        t0 = time.perf_counter()
        _ = retrieval_service.hybrid_search(db, q, top_k=50)
        t_cached_ret = (time.perf_counter() - t0) * 1000
        cached_retrieval_times.append(t_cached_ret)

        t0 = time.perf_counter()
        top_chunks, _, _ = reranking_service.rerank_kb(q, candidates, top_n=4)
        t_rerank = (time.perf_counter() - t0) * 1000
        rerank_times.append(t_rerank)

        t0 = time.perf_counter()
        conf_data = evidence_selection_service.compute_internal_confidence(q, top_chunks)
        t_ev = (time.perf_counter() - t0) * 1000
        evidence_times.append(t_ev)

    print(f"Embedding Latency (Warm): avg {sum(embed_times)/len(embed_times):.2f} ms")
    print(f"Hybrid Retrieval Latency: avg {sum(retrieval_times)/len(retrieval_times):.2f} ms")
    print(f"Cached Hybrid Retrieval Latency: avg {sum(cached_retrieval_times)/len(cached_retrieval_times):.2f} ms")
    print(f"Reranking Latency: avg {sum(rerank_times)/len(rerank_times):.2f} ms")
    print(f"Evidence Scoring Latency: avg {sum(evidence_times)/len(evidence_times):.2f} ms")

    print("\n" + "=" * 60)
    print("MEASURING STREAMING TTFT AND TOTAL LATENCY")
    print("=" * 60)

    test_stream_queries = [
        "What is SAP BRIM?",
        "How does Convergent Invoicing process billable items?",
        "What is the difference between online and offline charging in SAP CC?"
    ]

    ttfts = []
    totals = []

    for q in test_stream_queries:
        t_start = time.perf_counter()
        ttft = None
        total_tokens = 0
        collected_text = ""

        for event in rag_service.stream_query(db, q):
            if event.get("type") == "token":
                if ttft is None:
                    ttft = (time.perf_counter() - t_start) * 1000
                total_tokens += 1
                collected_text += event.get("content", "")

        t_end = time.perf_counter()
        total_lat = (t_end - t_start) * 1000
        ttfts.append(ttft or 0)
        totals.append(total_lat)

        print(f"Query: {q[:45]}...")
        print(f"  TTFT: {ttft:.1f} ms | Total: {total_lat:.1f} ms | Tokens: {total_tokens} | Words: {len(collected_text.split())}")

    print("\n" + "=" * 60)
    print("SUMMARY PERFORMANCE METRICS")
    print("=" * 60)
    ttfts.sort()
    totals.sort()
    p50_ttft = ttfts[len(ttfts)//2]
    p95_ttft = ttfts[-1]
    p50_total = totals[len(totals)//2]
    p95_total = totals[-1]

    print(f"TTFT (Time-To-First-Token) p50: {p50_ttft:.1f} ms | p95: {p95_ttft:.1f} ms")
    print(f"Total Response Latency p50: {p50_total:.1f} ms | p95: {p95_total:.1f} ms")
    print("=" * 60)

if __name__ == "__main__":
    run_measurements()
