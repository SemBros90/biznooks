Continuation plan and what was just added

- DB: `backend/app/database.py` now respects `DATABASE_URL` for Postgres; falls back to SQLite demo DB.
- Integrations: `backend/app/integrations.py` placeholders for GSTN, banks, payment gateways, customs.
- LUT: endpoint `POST /invoices/{invoice_id}/apply_lut` to apply LUT reference to invoices.
- Migrations: Alembic scaffold (alembic.ini, alembic/env.py) included; run `alembic revision --autogenerate -m "init"` after setting `DATABASE_URL` and installing alembic.
- Frontend: minimal React scaffold in `frontend/` with `package.json` and `src/App.tsx`.

Next recommended actions:
- Wire Alembic and create initial migration.
- Implement real GSTN integration (signing + auth) and webhook handling.
- Build frontend pages and connect to backend endpoints.
