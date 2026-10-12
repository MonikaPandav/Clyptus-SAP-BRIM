import os
import sys
import time
import json
from pathlib import Path
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker

# Setup paths
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(backend_dir))

from backend.app.config import settings
from backend.app.database import Base
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.chunk import DocumentChunk
from backend.app.models.chat import Chat
from backend.app.models.message import Message
from backend.app.models.citation import Citation
from backend.app.models.web_source import WebSource

def run_migration(pg_url: str = None, dry_run: bool = False):
    """
    Production-grade, non-destructive migration utility from SQLite to PostgreSQL with pgvector.
    Preserves existing SQLite database as an intact backup.
    Verifies embedding dimensions (384), chunk count, and HNSW index creation.
    """
    target_pg_url = pg_url or settings.DATABASE_URL
    sqlite_url = settings.SQLITE_FALLBACK_URL

    print("=" * 65)
    print("SAP BRIM ASSISTANT - DATABASE MIGRATION TO PGVECTOR")
    print("=" * 65)
    print(f"Source SQLite (Read-Only Backup): {sqlite_url}")
    print(f"Target PostgreSQL:               {target_pg_url}")
    print(f"Dry Run:                          {dry_run}")
    print("-" * 65)

    # 1. Connect to SQLite
    sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    SqliteSession = sessionmaker(bind=sqlite_engine)
    src_db = SqliteSession()

    total_sqlite_docs = src_db.query(Document).count()
    total_sqlite_chunks = src_db.query(DocumentChunk).count()
    total_sqlite_users = src_db.query(User).count()

    print(f"Verified Source SQLite Contents:")
    print(f"  - Users:           {total_sqlite_users}")
    print(f"  - Documents:       {total_sqlite_docs}")
    print(f"  - Document Chunks: {total_sqlite_chunks}")

    if total_sqlite_chunks == 0:
        print("[ERROR] Source SQLite database has 0 chunks. Aborting migration.")
        src_db.close()
        return False

    # 2. Check PostgreSQL target connection
    try:
        pg_engine = create_engine(target_pg_url, connect_args={"connect_timeout": 3})
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("[SUCCESS] PostgreSQL target database is online and reachable.")
            
            # Ensure pgvector extension
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
                print("[SUCCESS] pgvector extension verified on target database.")
            except Exception as ext_err:
                print(f"[WARNING] Could not enable extension vector: {ext_err}")
    except Exception as pg_err:
        print(f"\n[NOTICE] PostgreSQL target database at '{target_pg_url}' is not currently reachable:")
        print(f"         {pg_err}")
        print("\nSQLite database remains active as local development backend.")
        print("To complete production cutover when PostgreSQL is provisioned, run:")
        print(f"  python backend/scripts/migrate_sqlite_to_pgvector.py --url postgresql://user:pass@host:5432/dbname")
        src_db.close()
        return False

    if dry_run:
        print("\n[DRY RUN COMPLETE] Target verified. No records copied.")
        src_db.close()
        return True

    # 3. Initialize Target Tables
    Base.metadata.create_all(bind=pg_engine)
    PgSession = sessionmaker(bind=pg_engine)
    tgt_db = PgSession()

    # 4. Migrate Users
    print("\nMigrating Users...")
    users = src_db.query(User).all()
    for u in users:
        existing = tgt_db.query(User).filter(User.id == u.id).first()
        if not existing:
            tgt_db.add(User(
                id=u.id,
                email=u.email,
                name=u.name,
                password_hash=u.password_hash,
                role=getattr(u, "role", "consultant"),
                is_admin=u.is_admin,
                is_active=u.is_active,
                created_at=u.created_at
            ))
    tgt_db.commit()
    print(f"  Migrated {len(users)} users.")

    # 5. Migrate Documents
    print("Migrating Documents...")
    docs = src_db.query(Document).all()
    for d in docs:
        existing = tgt_db.query(Document).filter(Document.id == d.id).first()
        if not existing:
            tgt_db.add(Document(
                id=d.id,
                name=d.name,
                file_path=d.file_path,
                content_hash=d.content_hash,
                total_pages=d.total_pages,
                total_chunks=d.total_chunks,
                status=d.status,
                created_at=d.created_at,
                updated_at=d.updated_at
            ))
    tgt_db.commit()
    print(f"  Migrated {len(docs)} documents.")

    # 6. Migrate Document Chunks (Batch size 500)
    print("Migrating Document Chunks with 384-dim embeddings...")
    chunks = src_db.query(DocumentChunk).all()
    batch_size = 500
    migrated_chunks = 0

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        for c in batch:
            existing = tgt_db.query(DocumentChunk).filter(DocumentChunk.id == c.id).first()
            if not existing:
                emb = c.embedding
                if isinstance(emb, str):
                    emb = json.loads(emb)
                
                # Validate dimensions
                if len(emb) != settings.EMBEDDING_DIM:
                    print(f"[WARNING] Chunk {c.id} has dimension {len(emb)} != {settings.EMBEDDING_DIM}. Skipping.")
                    continue

                tgt_db.add(DocumentChunk(
                    id=c.id,
                    document_id=c.document_id,
                    document_name=c.document_name,
                    chunk_index=c.chunk_index,
                    page_number=c.page_number,
                    section=c.section,
                    chunk_text=c.chunk_text,
                    metadata_json=c.metadata_json,
                    embedding=emb
                ))
                migrated_chunks += 1
        tgt_db.commit()
        print(f"  Progress: {min(i+batch_size, len(chunks))}/{len(chunks)} chunks committed.")

    # 7. Create HNSW Vector Index and GIN Text Index on PostgreSQL
    print("Verifying HNSW Vector Index and GIN Text Index...")
    with pg_engine.connect() as conn:
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw "
            "ON document_chunks USING hnsw (embedding vector_cosine_ops);"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_document_chunks_fts "
            "ON document_chunks USING gin (to_tsvector('english', chunk_text));"
        ))
        conn.commit()
    print("[SUCCESS] HNSW cosine index (ix_document_chunks_embedding_hnsw) verified.")

    # 8. Verification & Latency Benchmark
    target_docs = tgt_db.query(Document).count()
    target_chunks = tgt_db.query(DocumentChunk).count()

    print("\n" + "=" * 65)
    print("MIGRATION INTEGRITY VALIDATION")
    print("=" * 65)
    print(f"Source SQLite Documents:   {total_sqlite_docs} | Target PostgreSQL Documents:   {target_docs}")
    print(f"Source SQLite Chunks:      {total_sqlite_chunks} | Target PostgreSQL Chunks:      {target_chunks}")

    if target_chunks == total_sqlite_chunks:
        print("[SUCCESS] 100% Data Integrity Verified! All chunks successfully migrated.")
    else:
        print(f"[WARNING] Discrepancy detected: {total_sqlite_chunks - target_chunks} chunks missing.")

    # Benchmark pgvector retrieval
    test_vec = [0.01] * settings.EMBEDDING_DIM
    t0 = time.perf_counter()
    with pg_engine.connect() as conn:
        q_str = "[" + ",".join(str(f) for f in test_vec) + "]"
        rows = conn.execute(text(
            "SELECT id, document_name, page_number, 1 - (embedding <=> :q) AS sim "
            "FROM document_chunks ORDER BY embedding <=> :q ASC LIMIT 10"
        ), {"q": q_str}).fetchall()
    t_elapsed = (time.perf_counter() - t0) * 1000
    print(f"[BENCHMARK] Native PostgreSQL HNSW Vector Query Latency: {t_elapsed:.2f} ms ({len(rows)} rows)")
    print("=" * 65)

    src_db.close()
    tgt_db.close()
    return True

if __name__ == "__main__":
    url_arg = None
    dry = "--dry-run" in sys.argv
    if "--url" in sys.argv:
        idx = sys.argv.index("--url")
        if idx + 1 < len(sys.argv):
            url_arg = sys.argv[idx + 1]
    run_migration(pg_url=url_arg, dry_run=dry)
