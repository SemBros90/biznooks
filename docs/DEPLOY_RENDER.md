## Deploying to Render (automatic via GitHub Actions)

This repository includes a `render.yaml` manifest and a GitHub Action (`.github/workflows/deploy-to-render.yml`) that can trigger deployments to Render via API.

Before using the workflow, set the following GitHub Secrets in your repository settings:

- `RENDER_API_KEY` — a Render API key (create in Render Dashboard → Account → API Keys).
- `RENDER_SERVICE_ID` — the ID of the Render service you want to deploy (find in Render Dashboard; or create the service first by connecting the repo).

How it works:

- On push to `main` and on pull requests the Action will call Render API to trigger a deploy for the given service.
- The workflow fetches service info and attempts to print the default domain as a preview URL.

Steps to use:

1. Go to https://dashboard.render.com and connect your GitHub repository (SemBros90/biznooks).
2. Create two services (or one combined service):
   - Web Service: use the `Dockerfile` at repo root, name it `biznooks-backend`.
   - Static Site: for frontend, name it `biznooks-frontend`, set build command `cd frontend && npm ci && npm run build`, publish `frontend/build`.
3. In Render, grab the Service ID for the backend service (shown in the service settings) and create an API key.
4. Add `RENDER_SERVICE_ID` and `RENDER_API_KEY` as GitHub Secrets for your repo.
5. Push a change or open a PR — the GitHub Action will trigger and print a preview URL if available.

Limitations:

- The Action cannot create services for you; you must create them in Render or use Render's UI to connect the repo.
- Preview deployments for PRs may require additional Render configuration (e.g., Pull Request Previews feature) — consult Render docs.
