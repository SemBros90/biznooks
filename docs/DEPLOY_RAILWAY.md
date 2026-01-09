## Deploying to Railway

Railway makes it easy to deploy connected services (Postgres, Redis) and host your app. The most straightforward way is to connect your GitHub repo to Railway via their UI.

Steps (recommended):

1. Create a Railway account at https://railway.app and sign in.
2. Create a new Project and choose "Deploy from GitHub". Connect your GitHub account and grant access to the `SemBros90/biznooks` repo.
3. Add two services: a Web Service for the backend and a Static Site for the frontend (or a single Docker service). Configure build commands:
   - Backend (Web Service): `uvicorn backend.app.main:app --reload --host 0.0.0.0 --port $PORT` or use Docker.
   - Frontend (Static): `cd frontend && npm ci && npm run build` and set publish directory `frontend/build`.
4. Railway automatically provides environment variables and preview URLs for each deployment. Use the Railway dashboard to find the public URLs for the running services.

Automated deploy via GitHub Actions (template):

Add a GitHub Actions workflow that triggers a Railway deploy via the Railway CLI using a Railway service token stored as `RAILWAY_TOKEN`.

Example job snippet (requires `railwayapp/cli` installed or use `curl` to Railway API):

```yaml
# This is an example — Railway CLI usage requires a token and project ID
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Railway CLI
        run: |
          curl -sSfL https://railway.app/install.sh | sh
      - name: Deploy
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          railway login --token "$RAILWAY_TOKEN"
          railway up --detach
```

Notes:
- Railway will create preview URLs automatically when you deploy from branches or PRs if configured. The dashboard shows the URL.
- You will need to add secrets (`RAILWAY_TOKEN`) to GitHub to allow the Action to run.
