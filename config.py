"""
config.py — Centralized Configuration for Legal AI Platform
============================================================
Loads environment variables from .env and defines all constants
used across the application. This is the SINGLE source of truth
for API keys, model names, and tuning parameters.

Production features added:
  • APP_ENV toggle (development / production)
  • File-based logging in production
  • API timeout settings
  • Optional Gradio basic auth
  • Worker count for Gunicorn
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env file (if it exists) ────────────────────────────
load_dotenv()

# =====================================================================
#  ENVIRONMENT & SERVER
# =====================================================================

# "development" or "production" — controls logging, auth, debug mode
APP_ENV: str = os.getenv("APP_ENV", "development")
IS_PRODUCTION: bool = APP_ENV == "production"

# Server port (Gradio listens here; Nginx proxies to it)
PORT: int = int(os.getenv("PORT", "10000"))

# Number of Gunicorn workers for production (ignored in dev)
WORKERS: int = int(os.getenv("WORKERS", "1"))

# App version (shown in health check)
APP_VERSION: str = "1.0.0"

# =====================================================================
#  LOGGING
# =====================================================================

# Log level from env — production defaults to WARNING, dev to INFO
LOG_LEVEL: str = os.getenv(
    "LOG_LEVEL",
    "WARNING" if IS_PRODUCTION else "INFO",
)

# Create logs directory
LOGS_DIR: Path = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Build handlers list
_handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

# In production, also write logs to a file
if IS_PRODUCTION:
    _file_handler = logging.FileHandler(
        LOGS_DIR / "app.log",
        encoding="utf-8",
    )
    _handlers.append(_file_handler)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=_handlers,
    force=True,  # override any prior basicConfig calls
)

# =====================================================================
#  API KEYS
# =====================================================================

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

# =====================================================================
#  OPTIONAL BASIC AUTH (production only)
# =====================================================================
# Set both to enable Gradio basic auth in production.
# Leave blank to disable auth.
GRADIO_AUTH_USER: str = os.getenv("GRADIO_AUTH_USER", "")
GRADIO_AUTH_PASS: str = os.getenv("GRADIO_AUTH_PASS", "")

# =====================================================================
#  LLM SETTINGS
# =====================================================================

LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "llama-3.1-8b-instant")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))

# Timeout for LLM API calls (seconds)
API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))

# =====================================================================
#  EMBEDDING MODEL
# =====================================================================

EMBEDDING_MODEL_NAME: str = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/all-MiniLM-L6-v2",
)

# =====================================================================
#  RAG SETTINGS
# =====================================================================

CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "600"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "3"))

# =====================================================================
#  WEB SEARCH SETTINGS
# =====================================================================

SEARCH_DEPTH: str = os.getenv("SEARCH_DEPTH", "advanced")
MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))

# =====================================================================
#  OUTPUT SETTINGS
# =====================================================================

OUTPUT_DIR: Path = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# =====================================================================
#  LEGAL KEYWORDS (Merged Superset)
# =====================================================================

LEGAL_KEYWORDS: list[str] = [
    # From GenAI Project
    "agreement", "contract", "party", "clause", "liability",
    "terms", "conditions", "confidential", "jurisdiction",
    "law", "obligation", "warranty", "breach",
    "settlement", "nda", "lease", "intellectual property",
    # From Agentic AI Project (unique additions)
    "legal", "act", "rights", "crime", "cyber",
    "court", "ipc", "constitution", "section",
    "regulation", "privacy", "penalty", "offence",
    # Additional useful keywords
    "statute", "arbitration", "compliance", "litigation",
    "defendant", "plaintiff", "verdict", "appeal",
]

LEGAL_DOC_MIN_MATCHES: int = 3
