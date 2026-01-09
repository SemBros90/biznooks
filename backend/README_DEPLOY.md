Deployment notes

- Dockerfile included for containerized backend.
- `docker-compose.yml` provides a Postgres service for local testing.
- For production, use migrations (Alembic) to manage schema changes; local demo uses SQLite.

Quick local test with Docker Compose:

```bash
docker compose up --build
```

Set `DATABASE_URL` env var to point to Postgres when using production DB.
