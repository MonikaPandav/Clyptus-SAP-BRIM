"""
Management Script: Ingest Extended Official SAP Documentation and Community Sources.

Complies with non-negotiable architectural requirements:
- Treats discovery sources (help.sap.com/, community.sap.com/, github.com/SAP*, etc.) as discovery roots,
  preventing wholesale ingestion.
- Preserves canonical URLs, product/version metadata, document headings, and section citations.
- For SAP Community, captures original author, publication date, and tags as forum_web.
- Applies strict deduplication for repeated URLs and overlapping chunk content.
- Respects the SAP_WEB_SOURCES_ENABLED feature flag (default False).
"""

import sys
import json
import logging
from pathlib import Path

# Ensure project root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.config import settings
from backend.app.database import SessionLocal, init_db
from backend.app.retrieval.source_registry import source_registry
from backend.app.retrieval.sap_web_doc_ingest import sap_web_doc_ingest_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ingest_sap_web_sources")


def run_web_ingestion(dry_run: bool = False, to_db: bool = False):
    logger.info("=" * 70)
    logger.info("Starting SAP Official Documentation & Community Ingestion Run")
    logger.info(f"Feature Flag SAP_WEB_SOURCES_ENABLED: {settings.SAP_WEB_SOURCES_ENABLED}")
    logger.info(f"Dry Run Mode: {dry_run}")
    logger.info(f"Database Persist Mode: {to_db}")
    logger.info("=" * 70)

    db = None
    if to_db and not dry_run:
        init_db()
        db = SessionLocal()

    try:
        summary = sap_web_doc_ingest_service.run_full_registry_ingestion(db=db, dry_run=dry_run)
        
        # Save evaluation summary
        output_eval = ROOT_DIR / "backend" / "evaluation" / "results" / "web_sources_ingestion_summary.json"
        output_eval.parent.mkdir(parents=True, exist_ok=True)
        output_eval.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        logger.info("\n" + "=" * 70)
        logger.info("INGESTION RUN COMPLETE")
        logger.info(f"Total Sources Evaluated: {summary['total_sources_evaluated']}")
        logger.info(f"Discovery Hubs Identified & Guarded: {summary['discovery_sources_identified_and_skipped']}")
        logger.info(f"Successful Sources Ingested: {summary['successful_sources_ingested']}")
        logger.info(f"Deduplicated Duplicate URLs Skipped: {summary['deduplicated_urls_skipped']}")
        logger.info(f"Total Chunks Retained: {summary['total_retained_chunks']}")
        logger.info(f"Report Written to: {output_eval}")
        logger.info("=" * 70)
        return summary
    finally:
        if db:
            db.close()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    db_persist = "--persist-db" in sys.argv
    run_web_ingestion(dry_run=dry, to_db=db_persist)
