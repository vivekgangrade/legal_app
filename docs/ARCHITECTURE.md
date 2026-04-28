# 🏗️ Architecture & System Design

How the Legal AI Platform is built, deployed, and scaled.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        INTERNET                              │
│                           │                                  │
│                    ┌──────┴──────┐                           │
│                    │   Nginx     │  Port 80/443              │
│                    │  (Reverse   │  Rate limiting             │
│                    │   Proxy)    │  WebSocket support         │
│                    └──────┬──────┘                           │
│                           │                                  │
│                    ┌──────┴──────┐                           │
│                    │   Gradio    │  Port 10000               │
│                    │   App       │  Health: /health           │
│                    │   (ASGI)    │  Ready: /ready             │
│                    └──────┬──────┘                           │
│                           │                                  │
│              ┌────────────┼────────────┐                    │
│              │            │            │                    │
│       ┌──────┴──┐  ┌──────┴──┐  ┌──────┴──┐               │
│       │  RAG    │  │Research │  │  PDF    │               │
│       │ Service │  │ Service │  │ Service │               │
│       └────┬────┘  └────┬────┘  └─────────┘               │
│            │            │                                   │
│       ┌────┴────┐  ┌────┴────┐                             │
│       │  FAISS  │  │ Tavily  │                             │
│       │ Vector  │  │  Web    │                             │
│       │  Store  │  │ Search  │                             │
│       └─────────┘  └─────────┘                             │
│                                                             │
│            ┌────────────┐                                   │
│            │  Groq LLM  │  Shared by both services          │
│            │  (LLaMA)   │                                   │
│            └────────────┘                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## How Docker Works in This Project

### Build Process (Multi-Stage)

```
Stage 1: Builder                    Stage 2: Production
┌──────────────────┐               ┌──────────────────┐
│ python:3.11-slim │               │ python:3.11-slim │
│                  │               │                  │
│ Install gcc/g++  │               │ Copy packages    │
│ pip install deps │──────────────▶│ Copy app code    │
│ (with build      │  only the     │ Pre-download     │
│  tools)          │  installed    │  embedding model │
│                  │  packages     │ Non-root user    │
└──────────────────┘               └──────────────────┘
     ~900MB                             ~1.5GB (with model)
     (discarded)                        (final image)
```

### Layer Caching

```dockerfile
# These layers are cached (rebuild only when requirements.txt changes):
COPY requirements.txt .
RUN pip install -r requirements.txt

# This layer rebuilds on every code change (fast):
COPY . .
```

### Container Lifecycle

```
docker-compose up
     │
     ├── Build image (if needed)
     ├── Create container
     ├── Start: python app.py
     ├── Health check: /health every 30s
     │
     │   On failure:
     │   ├── Retry 3 times
     │   └── Mark unhealthy → orchestrator restarts
     │
     └── docker-compose down → graceful shutdown
```

---

## How CI/CD Works

```
Developer pushes to main
         │
         ▼
┌─────────────────────┐
│  GitHub Actions      │
│                      │
│  Job 1: Lint & Test  │
│  ├── Syntax check    │
│  ├── Flake8 lint     │
│  └── Pass? ─────────┼──▶ No → ❌ Stop
│                      │
│  Job 2: Build Docker │    Yes ▼
│  ├── Build image     │
│  ├── Test container  │
│  └── Pass? ─────────┼──▶ No → ❌ Stop
│                      │
│  Job 3: Deploy       │    Yes ▼
│  ├── SSH to EC2      │
│  ├── git pull        │
│  ├── docker build    │
│  ├── docker up       │
│  └── Health check    │
│       ├── Pass → ✅  │
│       └── Fail → ⏪  │ (auto-rollback)
└─────────────────────┘
```

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `EC2_HOST` | EC2 public IP or DNS |
| `EC2_USER` | SSH user (default: `ubuntu`) |
| `EC2_SSH_KEY` | Private key (PEM format) |
| `GROQ_API_KEY` | Groq API key |
| `TAVILY_API_KEY` | Tavily API key |

---

## How Scaling Works

### Current: Single Instance (Vertical Scaling)

```
EC2 t3.medium (2 vCPU, 4GB)
├── Nginx (port 80)
├── App container (port 10000)
└── Redis (optional, port 6379)
```

**To handle more load:** Upgrade to `t3.large` (2 vCPU, 8GB) or `t3.xlarge`.

### Next Level: Horizontal Scaling with ALB

```
                   ┌────────────┐
                   │    ALB     │
                   │ (port 80)  │
                   └─────┬──────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
         ┌────┴───┐ ┌────┴───┐ ┌────┴───┐
         │ EC2 #1 │ │ EC2 #2 │ │ EC2 #3 │
         │  App   │ │  App   │ │  App   │
         └────────┘ └────────┘ └────────┘
```

### Future: Container Orchestration

#### AWS ECS (Easiest Migration)

```yaml
# Convert docker-compose.yml to ECS task definition
# Use `ecs-cli compose` or Copilot CLI
ecs-cli compose --file docker-compose.yml service up
```

#### Kubernetes (Most Flexible)

```yaml
# Create Deployment + Service + Ingress
# The Dockerfile stays the same
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legal-ai
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: legal-ai-platform:latest
        ports:
        - containerPort: 10000
        livenessProbe:
          httpGet:
            path: /health
            port: 10000
        readinessProbe:
          httpGet:
            path: /ready
            port: 10000
```

#### AWS Lambda (Serverless)

For future microservices split:
- **Research API** → Lambda + API Gateway
- **PDF Generator** → Lambda
- **RAG Pipeline** → ECS (needs persistent FAISS index)

---

## Environment Configuration Flow

```
.env.example          .env (local)          EC2 Environment
(committed)           (gitignored)          (set via CI/CD)
     │                     │                      │
     ▼                     ▼                      ▼
┌─────────┐         ┌─────────┐           ┌─────────┐
│ Template │ ──cp──▶ │  Local  │           │ GitHub  │
│  file    │         │  dev    │           │ Secrets │
└─────────┘         └────┬────┘           └────┬────┘
                         │                      │
                    ┌────┴────┐           ┌────┴────┐
                    │ dotenv  │           │  CI/CD  │
                    │ loads   │           │ writes  │
                    └────┬────┘           └────┬────┘
                         │                      │
                         ▼                      ▼
                    ┌─────────────────────────────┐
                    │        config.py             │
                    │   (single source of truth)   │
                    └─────────────────────────────┘
```

---

## Request Flow (Production)

```
User Browser
     │
     │ HTTPS (port 443)
     ▼
┌──────────┐
│  Nginx   │ ── Rate limit (10 req/s)
│          │ ── Security headers
│          │ ── Gzip compression
│          │ ── WebSocket upgrade
└────┬─────┘
     │ proxy_pass (port 10000)
     ▼
┌──────────┐
│  Gradio  │ ── Auth check (if enabled)
│  ASGI    │ ── Route to handler
└────┬─────┘
     │
     ├──▶ /health  → health.py → JSON response
     ├──▶ /ready   → health.py → JSON response
     │
     ├──▶ Tab 1: Document Q&A
     │    ├── Upload PDFs → rag_service.process_pdfs()
     │    │   ├── PyPDFLoader
     │    │   ├── Validate (legal doc?)
     │    │   ├── Chunk (600 chars, 100 overlap)
     │    │   ├── Embed (MiniLM-L6-v2)
     │    │   └── FAISS index
     │    └── Ask question → rag_service.query_documents()
     │        ├── Similarity search (top 3)
     │        └── llm_service.get_rag_answer()
     │            └── Groq API (with 30s timeout + retry)
     │
     └──▶ Tab 2: Legal Research
          ├── Validate query (legal keywords?)
          ├── research_service.search_legal_web()
          │   └── Tavily API (with retry)
          ├── llm_service.get_research_report()
          │   └── Groq API (with 30s timeout + retry)
          └── pdf_service.generate_pdf()
              └── FPDF → outputs/legal_report_xxx.pdf
```

---

## Performance Optimizations

| Optimization | Where | Impact |
|-------------|-------|--------|
| Lazy-init LLM client | `llm_service.py` | No startup cost if tab unused |
| Lazy-init embeddings | `rag_service.py` | Saves ~500MB if tab unused |
| Pre-download model in Docker | `Dockerfile` | No cold-start download |
| Gzip compression | `nginx.conf` | 60-80% smaller responses |
| Layer caching | `Dockerfile` | Faster rebuilds |
| Non-root user | `Dockerfile` | Security (no privilege escalation) |
| Rate limiting | `nginx.conf` | Prevents abuse |
| API timeout | `config.py` | No hung requests |
| Retry with backoff | `retry.py` | Handles transient failures |
