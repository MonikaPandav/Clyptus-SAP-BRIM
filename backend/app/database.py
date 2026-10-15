import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

import socket
from urllib.parse import urlparse

def _is_postgres_reachable(url: str) -> bool:
    """Fast TCP socket probe (0.25s) to avoid 15s psycopg2 connection timeout when Postgres is offline."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        with socket.create_connection((host, port), timeout=0.25):
            return True
    except Exception:
        return False

def get_engine():
    """Attempt connecting to configured PostgreSQL database; fallback to SQLite if unavailable."""
    postgres_url = settings.DATABASE_URL
    if not _is_postgres_reachable(postgres_url):
        logger.info(
            f"PostgreSQL port not reachable at configured target. "
            f"Using local high-performance SQLite engine ({settings.SQLITE_FALLBACK_URL})."
        )
        sqlite_engine = create_engine(
            settings.SQLITE_FALLBACK_URL,
            connect_args={"check_same_thread": False}
        )
        return sqlite_engine

    try:
        engine = create_engine(postgres_url, pool_pre_ping=True, connect_args={"connect_timeout": 1})
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            # Ensure pgvector extension exists if postgres
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
            except Exception as e:
                logger.warning(f"Could not enable pgvector extension (might not be installed or lacks privileges): {e}")
        logger.info(f"Connected to PostgreSQL database: {postgres_url}")
        return engine
    except Exception as e:
        logger.warning(
            f"Could not connect to PostgreSQL ({postgres_url}): {e}. "
            f"Falling back to local SQLite engine ({settings.SQLITE_FALLBACK_URL})."
        )
        sqlite_engine = create_engine(
            settings.SQLITE_FALLBACK_URL,
            connect_args={"check_same_thread": False}
        )
        return sqlite_engine

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.app.models import user, chat, message, document, chunk, citation, web_source, web_image, uploaded_attachment, repo_chunk  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")

    # Lightweight migration: Ensure role column exists on users table
    try:
        with engine.connect() as conn:
            if engine.dialect.name == "sqlite":
                cols = [r[1] for r in conn.execute(text("PRAGMA table_info(users)")).fetchall()]
                if "role" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'consultant'"))
                    conn.execute(text("UPDATE users SET role = 'admin' WHERE is_admin = 1"))
                    conn.commit()
            elif engine.dialect.name == "postgresql":
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'consultant'"))
                conn.execute(text("UPDATE users SET role = 'admin' WHERE is_admin = true AND (role IS NULL OR role = 'consultant')"))
                conn.commit()
    except Exception as e:
        logger.warning(f"Could not verify or migrate users.role column: {e}")

    # Lightweight migration: Ensure Document Management columns exist on documents table
    try:
        with engine.connect() as conn:
            if engine.dialect.name == "sqlite":
                cols = [r[1] for r in conn.execute(text("PRAGMA table_info(documents)")).fetchall()]
                if "file_type" not in cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN file_type VARCHAR(50) DEFAULT 'pdf'"))
                if "file_size_bytes" not in cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN file_size_bytes INTEGER DEFAULT 0"))
                if "status" not in cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN status VARCHAR(50) DEFAULT 'completed'"))
                if "stage" not in cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN stage VARCHAR(100) DEFAULT 'Indexed'"))
                if "error_message" not in cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN error_message TEXT"))
                if "vector_indexed" not in cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN vector_indexed BOOLEAN DEFAULT 1"))
                if "updated_at" not in cols:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN updated_at DATETIME"))
                conn.commit()
            elif engine.dialect.name == "postgresql":
                conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_type VARCHAR(50) DEFAULT 'pdf'"))
                conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_size_bytes INTEGER DEFAULT 0"))
                conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'completed'"))
                conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS stage VARCHAR(100) DEFAULT 'Indexed'"))
                conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS error_message TEXT"))
                conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS vector_indexed BOOLEAN DEFAULT true"))
                conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
                conn.commit()
    except Exception as e:
        logger.warning(f"Could not verify or migrate documents columns: {e}")

    if engine.dialect.name == "postgresql":
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                # Create HNSW vector index for high-performance cosine similarity
                conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw "
                    "ON document_chunks USING hnsw (embedding vector_cosine_ops);"
                ))
                # Create GIN full-text search index for high-precision lexical retrieval
                conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS ix_document_chunks_fts "
                    "ON document_chunks USING gin (to_tsvector('english', chunk_text));"
                ))
                conn.commit()
                logger.info("pgvector HNSW index and GIN full-text search index verified.")
        except Exception as e:
            logger.warning(f"Could not initialize PostgreSQL vector/FTS indices: {e}")

    # Seed designated super admin user
    try:
        from backend.app.models.user import User
        from backend.app.security.auth import hash_password, verify_password
        with SessionLocal() as db:
            admin_email = "vamshiyadav245@gmail.com"
            admin_user = db.query(User).filter(User.email == admin_email).first()
            if not admin_user:
                new_admin = User(
                    email=admin_email,
                    name="Vamshi Yadav (Super Admin)",
                    password_hash=hash_password("Vamshi@06"),
                    is_admin=True,
                    role="admin",
                )
                db.add(new_admin)
                db.commit()
                logger.info(f"Default Super Admin account created: {admin_email}")
            else:
                updated = False
                if not admin_user.is_admin:
                    admin_user.is_admin = True
                    updated = True
                if admin_user.role != "admin":
                    admin_user.role = "admin"
                    updated = True
                if not verify_password("Vamshi@06", admin_user.password_hash):
                    admin_user.password_hash = hash_password("Vamshi@06")
                    updated = True
                if updated:
                    db.commit()
                    logger.info(f"Updated Super Admin account permissions/credentials: {admin_email}")
    except Exception as e:
        logger.warning(f"Could not seed super admin user: {e}")


