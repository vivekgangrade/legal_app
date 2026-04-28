# Troubleshooting Import Errors

There is nothing wrong with your code or installation. The error `Could not find import of 'fastapi.middleware.cors'` is usually an IDE configuration issue (e.g., VS Code using the wrong Python interpreter).

## Symptoms
- IDE shows `Import "fastapi.middleware.cors" could not be resolved`.
- Yet, trying to run the app works fine.
- `pip list` shows `fastapi` installed.

## Solution

1. Open the Command Palette (**Ctrl+Shift+P** or **Cmd+Shift+P**).
2. Type and select **Python: Select Interpreter**.
3. Choose the interpreter that corresponds to your project (typically the one marked "Recommended" or checking `pip list` output).
4. Restart VS Code if needed.

## Verification

To verify your environment is correct independently of the IDE:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

If the server starts (you see `INFO: Uvicorn running on...`), your setup is correct.
