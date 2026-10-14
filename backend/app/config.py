import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "SAP Knowledge Assistant"
    API_V1_STR: str = "/api"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5434/sap_assistant"
    )
    # If postgresql fails, fallback to local sqlite for zero-friction development
    SQLITE_FALLBACK_URL: str = f"sqlite:///{BASE_DIR / 'sap_assistant.db'}"

    # JWT Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "sap-super-secret-jwt-key-2026-production-ready")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Admin Key for Developer Ingestion
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "sap-admin-dev-secret-key-999")

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openrouter")  # openrouter, groq, openai, or local
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

    # Embedding & RAG parameters
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIM: int = 384
    TOP_K: int = int(os.getenv("TOP_K", "50"))
    RERANK_TOP_K: int = int(os.getenv("RERANK_TOP_K", "4"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.60"))
    GROUNDING_THRESHOLD: float = float(os.getenv("GROUNDING_THRESHOLD", "0.65"))

    # Evidence Confidence & Grounding Verification Settings (v2)
    INTERNAL_EVIDENCE_THRESHOLD: float = float(os.getenv("INTERNAL_EVIDENCE_THRESHOLD", "0.70"))
    # Search GitHub and approved SAP web sources whenever the best document match
    # falls below this calibrated relevance score.
    DOCUMENT_MATCH_THRESHOLD: float = float(os.getenv("DOCUMENT_MATCH_THRESHOLD", "0.80"))
    AUTO_MULTI_SOURCE_FALLBACK: bool = os.getenv("AUTO_MULTI_SOURCE_FALLBACK", "True").lower() in ("true", "1")
    ANSWER_GROUNDING_THRESHOLD: float = float(os.getenv("ANSWER_GROUNDING_THRESHOLD", "0.80"))
    MAX_GROUNDING_REPAIR_ATTEMPTS: int = int(os.getenv("MAX_GROUNDING_REPAIR_ATTEMPTS", "1"))
    FOLLOWUP_QUESTION_COUNT: int = int(os.getenv("FOLLOWUP_QUESTION_COUNT", "3"))
    TAVILY_MAX_RESULTS: int = int(os.getenv("TAVILY_MAX_RESULTS", "5"))

    # Generation Contract & Context Packing Flags (Grounded RAG)
    GROUNDED_CONTRACT_ENABLED: bool = os.getenv("GROUNDED_CONTRACT_ENABLED", "True").lower() in ("true", "1")
    GROUNDED_GENERATOR_MODEL: str = os.getenv("GROUNDED_GENERATOR_MODEL", "qwen/qwen3.8-27b")
    GROUNDED_TEMPERATURE: float = float(os.getenv("GROUNDED_TEMPERATURE", "0.15"))
    ANSWER_TEMPERATURE: float = float(os.getenv("ANSWER_TEMPERATURE", "0.10"))
    CONTEXT_PACKING_TOKEN_LIMIT: int = int(os.getenv("CONTEXT_PACKING_TOKEN_LIMIT", "3000"))
    CONTEXT_BASE_TOKEN_BUDGET: int = int(os.getenv("CONTEXT_BASE_TOKEN_BUDGET", "1500"))
    CONTEXT_PER_MODULE_TOKEN_BUDGET: int = int(os.getenv("CONTEXT_PER_MODULE_TOKEN_BUDGET", "600"))
    RETRIEVAL_CALIBRATED_THRESHOLD: float = float(os.getenv("RETRIEVAL_CALIBRATED_THRESHOLD", "0.6761"))
    DEDUPE_SIMILARITY_THRESHOLD: float = float(os.getenv("DEDUPE_SIMILARITY_THRESHOLD", "0.85"))
    PROMPT_PATH_GROUNDED_ANSWER: Path = (BASE_DIR / "app" / "prompts" / "grounded_answer.txt")

    # Tier Ranking Weights (relevance * tier_weight)
    TIER_WEIGHT_OFFICIAL_SAP: float = float(os.getenv("TIER_WEIGHT_OFFICIAL_SAP", "1.0"))
    TIER_WEIGHT_BOOK: float = float(os.getenv("TIER_WEIGHT_BOOK", "0.85"))
    TIER_WEIGHT_OFFICIAL_WEB: float = float(os.getenv("TIER_WEIGHT_OFFICIAL_WEB", "0.80"))
    TIER_WEIGHT_FORUM_WEB: float = float(os.getenv("TIER_WEIGHT_FORUM_WEB", "0.50"))
    TIER_WEIGHT_SELF_AUTHORED: float = float(os.getenv("TIER_WEIGHT_SELF_AUTHORED", "0.60"))
    ENABLE_SENTENCE_COMPRESSION: bool = os.getenv("ENABLE_SENTENCE_COMPRESSION", "False").lower() in ("true", "1")

    # Phase 1 & Advanced Architecture Feature Flags (Default OFF)
    SHADOW_MODE_ENABLED: bool = os.getenv("SHADOW_MODE_ENABLED", "False").lower() in ("true", "1")
    EXCLUDE_OFF_DOMAIN_DOCS: bool = os.getenv("EXCLUDE_OFF_DOMAIN_DOCS", "False").lower() in ("true", "1")
    USE_CORPUS_METADATA_V2: bool = os.getenv("USE_CORPUS_METADATA_V2", "False").lower() in ("true", "1")

    # GitHub Repository Retrieval & Multi-Source Comparison Feature Flags (Strictly Default FALSE)
    REPO_SOURCE_ENABLED: bool = os.getenv("REPO_SOURCE_ENABLED", "False").lower() in ("true", "1")
    MULTI_SOURCE_COMPARE_ENABLED: bool = os.getenv("MULTI_SOURCE_COMPARE_ENABLED", "False").lower() in ("true", "1")
    TIER_WEIGHT_GITHUB_REPO: float = float(os.getenv("TIER_WEIGHT_GITHUB_REPO", "0.80"))
    REPO_GATE_CALIBRATED_THRESHOLD: float = float(os.getenv("REPO_GATE_CALIBRATED_THRESHOLD", "0.65"))
    REPO_MIN_CHUNKS_THRESHOLD: int = int(os.getenv("REPO_MIN_CHUNKS_THRESHOLD", "10"))
    REPO_SNAPSHOTS_DIR: Path = BASE_DIR / "data" / "github_snapshots"

    # Extended Official SAP Web & Community Sources Feature Flags (Strictly Default FALSE)
    SAP_WEB_SOURCES_ENABLED: bool = os.getenv("SAP_WEB_SOURCES_ENABLED", "False").lower() in ("true", "1")
    TIER_WEIGHT_OFFICIAL_DEV_DOCS: float = float(os.getenv("TIER_WEIGHT_OFFICIAL_DEV_DOCS", "0.85"))
    TIER_WEIGHT_OFFICIAL_HELP_DOCS: float = float(os.getenv("TIER_WEIGHT_OFFICIAL_HELP_DOCS", "0.85"))
    TIER_WEIGHT_SAP_COMMUNITY: float = float(os.getenv("TIER_WEIGHT_SAP_COMMUNITY", "0.50"))
    WEB_DOC_SNAPSHOTS_DIR: Path = BASE_DIR / "data" / "web_doc_snapshots"

    # Rate Limiting & Backoff Settings
    RATE_LIMIT_MAX_RETRIES: int = int(os.getenv("RATE_LIMIT_MAX_RETRIES", "3"))
    RATE_LIMIT_BASE_BACKOFF_SEC: float = float(os.getenv("RATE_LIMIT_BASE_BACKOFF_SEC", "2.0"))

    # Web Fallback
    WEB_FALLBACK_ENABLED: bool = os.getenv("WEB_FALLBACK_ENABLED", "True").lower() in ("true", "1")
    WEB_SEARCH_API_KEY: str = os.getenv("WEB_SEARCH_API_KEY", "")

    # Canonical knowledge-base source directory (at repo root if present).
    # Keep exactly one source location so ingestion results can be reconciled with
    # the on-disk inventory and an operator never has to guess which folder is live.
    KNOWLEDGE_BASE_DIR: Path = (ROOT_DIR / "knowledge_base") if (ROOT_DIR / "knowledge_base").exists() else (BASE_DIR / "knowledge_base")
    DOCUMENTS_DIR: Path = (ROOT_DIR / "knowledge_base" / "documents") if (ROOT_DIR / "knowledge_base" / "documents").exists() else (BASE_DIR / "knowledge_base" / "documents")

    model_config = SettingsConfigDict(
        env_file=(
            str(BASE_DIR / ".env")
            if (BASE_DIR / ".env").exists()
            else (
                str(BASE_DIR / "app" / ".env")
                if (BASE_DIR / "app" / ".env").exists()
                else str(ROOT_DIR / ".env")
            )
        ),
        extra="allow"
    )

settings = Settings()

