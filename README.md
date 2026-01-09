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

Running on Replit or other single-process hosts
----------------------------------------------

You can import this repo into Replit (or similar code-run hosts) and run the backend directly.

- Replit will use the `start-replit.sh` script (configured in `.replit`) which starts the FastAPI app
	with an on-disk SQLite DB by default.
- If you need Redis or MinIO in that environment, configure external services and set the appropriate
	environment variables in the Replit Secrets settings (`REDIS_URL`, `S3_ENDPOINT_URL`, `S3_BUCKET`,
	`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).

To run locally with the Replit-style startup (for testing):

```bash
bash start-replit.sh
```

Note: Do not commit secrets or private keys. Use `.env.example` as reference and set actual values
in the host's secret settings.
