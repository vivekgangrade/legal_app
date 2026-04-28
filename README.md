<<<<<<< HEAD
# ⚖️ Legal AI Platform

A production-ready, Dockerized legal AI assistant combining **document-based Q&A** (RAG) with **autonomous web research** — deployable to AWS with CI/CD.

> **Built by merging:**
> - [GenAI Project](https://github.com/Jogendar-Bairagi/GenAI-Project) — Legal Documents RAG System
> - [Agentic AI](https://github.com/Jogendar-Bairagi/Agentic-AI) — Autonomous Legal Research Agent

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 📄 Document Q&A | Upload PDFs → FAISS vector search → LLM answers |
| 🔍 Legal Research | Web search (Tavily) → Structured report → PDF download |
| 🐳 Dockerized | Multi-stage build, non-root user, health checks |
| 🔄 CI/CD | GitHub Actions: lint → build → deploy to EC2 |
| 🌐 Nginx | Reverse proxy, WebSocket, rate limiting, SSL-ready |
| 🏥 Health Checks | `/health` and `/ready` endpoints |
| 🔒 Security | Env-based secrets, optional auth, non-root container |
| 📊 Logging | Structured logs, file logging in production |
| ♻️ Retry Logic | Exponential backoff on all API calls |

---

## 📁 Project Structure

```
LegalFinal/
├── app.py                          # Main entry point (Gradio + health mount)
├── config.py                       # Centralized env-based configuration
├── health.py                       # /health and /ready endpoints
├── services/
│   ├── llm_service.py              # Shared LLM client (Groq)
│   ├── rag_service.py              # PDF → FAISS → search (GenAI)
│   ├── research_service.py         # Tavily search → report (Agentic AI)
│   └── pdf_service.py              # PDF report generation
├── utils/
│   ├── validators.py               # Legal content validation
│   └── retry.py                    # Retry with exponential backoff
├── nginx/
│   └── nginx.conf                  # Reverse proxy config
├── scripts/
│   ├── setup-ec2.sh                # First-time EC2 setup
│   ├── deploy.sh                   # Deployment with rollback
│   └── startup.sh                  # Container entry point
├── .github/workflows/
│   └── deploy.yml                  # CI/CD pipeline
├── Dockerfile                      # Multi-stage optimized build
├── docker-compose.yml              # Dev orchestration
├── docker-compose.prod.yml         # Production overrides
├── .env.example                    # Environment template
├── .dockerignore                   # Docker build exclusions
├── .gitignore
├── requirements.txt
├── docs/
│   ├── AWS_DEPLOYMENT.md           # AWS deployment guide
│   └── ARCHITECTURE.md             # System design & scaling
└── README.md
```

---

## ⚡ Quick Start

### Option 1: Local Python

```bash
# 1. Clone and enter directory
git clone <your-repo-url>
cd LegalFinal

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env      # Windows
cp .env.example .env        # Linux/Mac
# Edit .env with your API keys

# 5. Run
python app.py
# → http://localhost:10000
```

### Option 2: Docker (Recommended)

```bash
# 1. Build and start
copy .env.example .env      # Edit with your API keys
docker-compose up --build

# → http://localhost:10000
# Health: http://localhost:10000/health
```

### Option 3: Docker Production (with Nginx)

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# → http://localhost (port 80 via Nginx)
```

---

## 🔑 API Keys

| Key | Get It | Used For |
|-----|--------|----------|
| `GROQ_API_KEY` | [console.groq.com/keys](https://console.groq.com/keys) | LLM (both tabs) |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) | Web search (Tab 2) |

---

## 🐳 Docker Commands

```bash
# Build
docker-compose build

# Start (background)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop
docker-compose down

# Full production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 🚢 AWS Deployment

See [docs/AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md) for the complete guide.

**Quick version:**
```bash
# On fresh EC2 Ubuntu instance:
sudo ./scripts/setup-ec2.sh
git clone <repo> /home/ubuntu/legal-ai-platform
cd /home/ubuntu/legal-ai-platform
cp .env.example .env && nano .env
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 🔄 CI/CD Pipeline

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

**Pipeline:** Push to `main` → Lint → Build Docker → Deploy to EC2

Required GitHub Secrets: `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`, `GROQ_API_KEY`, `TAVILY_API_KEY`

---

## 📊 Health & Monitoring

```bash
# Health check
curl http://localhost:10000/health
# → {"status": "healthy", "version": "1.0.0", "uptime_seconds": 123.4}

# Readiness check
curl http://localhost:10000/ready
# → {"ready": true}
```

---

## 👨‍💻 Team Members
- Jogendar Das Bairagi
- ROSHAN BANKAR
- VIVEK GANGRADE
- MAAHI MAHESHWARI
- SHUBHANGI PRAJAPAT

---

## 📚 References
- [Groq API](https://console.groq.com/docs) • [Tavily API](https://docs.tavily.com) • [Gradio](https://www.gradio.app/docs) • [LangChain](https://python.langchain.com) • [FAISS](https://github.com/facebookresearch/faiss) • [Docker](https://docs.docker.com) • [Nginx](https://nginx.org/en/docs/)
=======
# Legal Case Management Web Application
[GitHub Repository](https://github.com/vivekgangrade/legal_app)

A production-ready Full Stack Legal Case Management system, built with FastAPI (Backend), React (Frontend), Docker, and Kubernetes.

## Project Structure

```
legal_app/
├── backend/                # Python FastAPI Backend
│   ├── app/                # Application Source Code
│   │   ├── main.py         # Entry point
│   │   ├── models.py       # Data models (SQLAlchemy)
│   │   ├── routers/        # API routes
│   │   └── utils/          # Utilities
│   ├── Dockerfile          # Backend Docker Build
│   └── requirements.txt    # Python Dependencies
├── frontend/               # React Frontend
│   ├── src/                # React Source Code
│   ├── Dockerfile          # Frontend Docker Build
│   ├── nginx.conf          # Nginx Config
│   └── package.json        # JS Dependencies
├── k8s/                    # Kubernetes manifests
├── docker-compose.yml      # Docker Orchestration
└── .github/workflows/      # CI/CD Pipeline
```

## Features

- **Full Stack Architecture**: Separated Frontend and Backend.
- **FastAPI Backend**:
    - `POST /cases`: Create a new legal case.
    - `GET /cases`: List all cases.
    - `POST /users/token`: Authentication (User: `admin`, Pass: `password`).
    - Connects to PostgreSQL database.
- **React Frontend**: Modern UI with Dashboard and Case Management.
- **Dockerized**: 
    - `backend/Dockerfile`: Builds the Python API.
    - `frontend/Dockerfile`: Builds React and serves with Nginx.
    - `docker-compose.yml`: Runs the entire stack with one command.

## How to Run

### Option 1: Using Docker (Recommended)
*Prerequisite: Install Docker Desktop.*

1. Open a terminal in the project root.
2. Run:
   ```bash
   docker compose up --build
   ```
3. Access:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000/docs`

### Option 2: Running Locally (Manual)

**Backend**:
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
(Runs on port 8000)

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```
(Runs on port 5173)

## CI/CD Pipeline

The project includes a GitHub Actions workflow (`.github/workflows/ci-cd.yml`) that:
1. Tests the Backend (`pytest`).
2. Builds the Backend Docker Image.

## Kubernetes Deployment
1. Apply deployments: `kubectl apply -f k8s/`
>>>>>>> 0be617d20256d6634f88d373d4bd7e451672cf23
