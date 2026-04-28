$ErrorActionPreference = "Stop"

Write-Host "Checking for Python..."
try {
    python --version
}
catch {
    Write-Error "Python not found. Please install Python 3.10+ and add it to your PATH."
    exit 1
}

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "Installing dependencies..."
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies. Please checks the logs above."
    exit 1
}

Write-Host "Starting Legal Case Management App..."
Write-Host "Access Swagger UI at: http://localhost:8000/docs"
uvicorn app.main:app --reload
