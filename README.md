# RiceCare FastAPI (Refactor to package)

This is a 1:1 refactor of your original `main.py` into a clean package structure.
All functions and logic are kept as-is; only *moved* into modules.

## Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Local run (same behavior)
```bash
python -m app.main
```
