## Usage

This document gives quick copy-paste commands to run BizNooks locally for development.

Prerequisites

- Docker & docker-compose
- Python 3.11/3.12
- Node.js + npm (for frontend)

1) Start infrastructure (Postgres, Redis, MinIO)

```bash
docker-compose up --build -d
```

2) (Optional) Create the MinIO bucket (compose includes an init job):

```bash
python scripts/init_minio.py
```

3) Run migrations

```bash
export DATABASE_URL=postgresql://biznooks:changeme@localhost:5432/biznooks
chmod +x scripts/run_migrations.sh
./scripts/run_migrations.sh
```

4) Start API

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

5) Start background worker (if not running in Docker)

```bash
python backend/worker.py
```

6) Frontend

```bash
cd frontend
npm install
npm start
```

Demos

```bash
PYTHONPATH=. python3 backend/tests/run_gsp_sandbox_demo.py
PYTHONPATH=. python3 backend/tests/run_enqueue_demo.py
PYTHONPATH=. python3 backend/tests/run_store_signed_demo.py
```

Environment

See `.env.example` for the main env vars used by the project.
