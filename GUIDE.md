# User Guide: Running the Legal Case Management App

## Quick Start (Windows)

I have included a helper script `run.ps1` to automate the entire process for you.

1.  Open PowerShell in the project folder:
    `C:\Users\VIVEk\.gemini\antigravity\scratch\legal_case_management_py`
2.  Run the script:
    ```powershell
    .\run.ps1
    ```
    *Note: If you get a permission error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` first.*

This script will:
1.  Check for Python.
2.  Create a virtual environment (`venv`) if it doesn't exist.
3.  Install all required libraries.
4.  Start the server at `http://localhost:8000`.

## Manual Setup

If you prefer to run commands manually:

1.  **Create Environment**:
    ```bash
    python -m venv venv
    ```
2.  **Activate**:
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```
3.  **Install**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run**:
    ```bash
    uvicorn app.main:app --reload
    ```

## Running Tests

To verify everything is working correctly:

1.  Run the test script:
    ```powershell
    .\test.ps1
    ```

Or manually:
```bash
pytest
```

## Docker

If you have Docker installed, you can run the app in a container:

```bash
docker compose up --build
```
