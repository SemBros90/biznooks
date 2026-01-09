# BizNooks

BizNooks — demo accounting + compliance scaffold focused on India (e-invoicing, GST workflows, multi-currency, FX, TDS, e-waybill) with a minimal React frontend.

Quickstart (local development)

- Start local infrastructure (Postgres, Redis, MinIO) with Docker:

```bash
docker-compose up --build -d
```

- Create MinIO bucket (init job runs in compose, or manually):

```bash
python scripts/init_minio.py
```

- Run Alembic migrations:

```bash
export DATABASE_URL=postgresql://biznooks:changeme@localhost:5432/biznooks
chmod +x scripts/run_migrations.sh
./scripts/run_migrations.sh
```

- Start the API server:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

- (Optional) Start background worker locally:

```bash
python backend/worker.py
```

- Frontend (optional):

```bash
cd frontend
npm install
npm start
```

More details are in `docs/USAGE.md` and `.env.example`.
