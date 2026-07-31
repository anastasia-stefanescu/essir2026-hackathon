# Run this instead of "uv run uvicorn ..."
& "$PSScriptRoot\.venv\Scripts\python.exe" -m uvicorn app.main:app --port 8791 --reload
