# Backend Demo

This is a minimal FastAPI/SQLModel backend demo for the Biznooks accounting prototype.

Requirements:

```
pip install -r requirements.txt
```

Run the demo script (creates `data.db` and a sample balanced journal entry):

```
python -m backend.tests.run_demo
```

To run the API server locally:

```
uvicorn backend.app.main:app --reload
```
