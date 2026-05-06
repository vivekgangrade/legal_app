# ============================================================
# Dockerfile — Legal AI Platform (Multi-Stage, Optimized)
# ============================================================
# Build: docker build -t legal-ai-platform .
# Run:   docker run -p 10000:10000 --env-file .env legal-ai-platform
#
# Optimizations:
#   • python:3.11-slim base (small image ~150MB vs ~900MB full)
#   • Non-root user for security
#   • Layer caching: requirements installed before code COPY
#   • Pre-downloads embedding model at build time (fast cold start)
#   • Health check instruction for orchestrators
# ============================================================

# ── Stage 1: Build dependencies ──────────────────────────────
FROM python:3.11-slim AS builder

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install system dependencies needed for building packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first (layer caching — rebuilds only when deps change)
COPY requirements.txt .
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Production image ────────────────────────────────
FROM python:3.11-slim AS production

# Metadata
LABEL maintainer="Legal AI Team" \
      version="1.0.0" \
      description="Legal AI Platform — Document Q&A + Legal Research"

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Default production environment
    APP_ENV=production \
    PORT=10000

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Create non-root user for security
# (containers should never run as root in production)
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Create required directories
RUN mkdir -p /app/outputs /app/logs && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Pre-download the embedding model at build time
# This avoids a slow first-request download at runtime
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" \
    2>/dev/null || echo "Model pre-download skipped (no network)"

# Make startup script executable
RUN chmod +x scripts/startup.sh 2>/dev/null || true

# Switch to non-root user
USER appuser

# Expose Gradio port
EXPOSE ${PORT}

# Health check — Docker/ECS will ping this every 30s
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# Default command: run via startup script (uses Gunicorn in production)
CMD ["python", "app.py"]
