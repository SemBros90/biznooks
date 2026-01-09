Go-live checklist

- Verify data migration and run Alembic migrations against production DB.
- Perform security review: secrets, key management, TLS, webhook auth, RBAC.
- Ensure backups and monitoring are configured for Postgres.
- Finalize SLAs for GSTN/GSP retries and error handling.
- Run end-to-end tests with sample invoices, e-invoice filing, and returns.
- Conduct user acceptance testing and compliance sign-off.
- Prepare rollback plan and DB restore steps.
- Configure and test CI/CD to deploy to staging, then production.
