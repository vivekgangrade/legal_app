$ErrorActionPreference = "Stop"

if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Please run 'run.ps1' first to set up."
    exit 1
}

Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

Write-Host "Running Tests..."
pytest
