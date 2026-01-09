# Biznooks - Architecture (proposal)

- **Backend**: FastAPI + SQLModel (Pydantic + SQLAlchemy) — lightweight, developer-friendly, fast to iterate.
- **Database**: Postgres for production; SQLite used for local demos/tests.
- **Frontend**: React with TypeScript (separate `frontend/` repo) and component library for forms and reports.
- **Auth**: OAuth2 / JWT for API; role-based access for accounting operations.
- **Integrations**: GSTN/GSP connectors, bank statement import, payment gateways, customs portals.
- **Deployment**: Containerized (Docker), Kubernetes or managed services on AWS/GCP/Azure.

Key decisions:
- Use double-entry ledger primitives (JournalEntry and LedgerEntry) as the system of record.
- Store amounts in account currency with exchange rates for conversion to company base currency for reporting.
- Implement e-invoicing and GST flows as pluggable modules to comply with India rules.
