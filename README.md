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
