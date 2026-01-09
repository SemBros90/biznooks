# Importing a Private GitHub Repo into Replit

If Replit cannot import the repository because it is private or requires authentication, follow one of these secure options.

Recommended order:
1) Connect Replit to your GitHub account (OAuth/GitHub App) — easiest and most secure.
2) Add a repository deploy key (SSH) — good for single-repo access.
3) Use a personal access token (PAT) if you prefer HTTPS cloning.

Option A — Connect GitHub (recommended)

- In Replit, choose "Import from GitHub" → sign in with GitHub and authorize Replit.
- During GitHub authorization, grant access to private repositories (or select specific repos).
- After authorization, you can import the repo directly into Replit.

Option B — Add a Deploy Key (SSH)

1. On the machine/session where Replit runs (or locally), generate an SSH keypair:

```bash
ssh-keygen -t ed25519 -C "replit-deploy" -f replit_deploy_key -N ''
```

2. Copy the public key content (`replit_deploy_key.pub`) and add it to your GitHub repo:

- Go to GitHub → Repository → Settings → Deploy keys → Add deploy key.
- Paste the public key and give it a name (e.g., `replit-deploy`).
- If you need Replit to push changes, enable `Allow write access` (optional).

3. Add the private key to Replit Secrets (or the Replit SSH key settings):

- In Replit, open the Secrets/Environment panel and add a secret named `SSH_PRIVATE_KEY` with the contents of `replit_deploy_key`.

4. In Replit's shell (or using `start-replit.sh`), load the key and clone via SSH:

```bash
mkdir -p ~/.ssh
echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519
ssh-keyscan github.com >> ~/.ssh/known_hosts
git clone git@github.com:YOUR_GITHUB_USER/YOUR_REPO.git
```

Option C — Use a Personal Access Token (HTTPS)

1. Create a PAT on GitHub with `repo` scope (minimum: `repo` to clone private repos):

- https://github.com/settings/tokens → Generate new token → check `repo` → Create token.

2. In Replit, add the token to Secrets as `GITHUB_TOKEN`.

3. Clone using the token (safer: use credential helper; quick method shown):

```bash
git clone https://$GITHUB_TOKEN@github.com/YOUR_GITHUB_USER/YOUR_REPO.git
```

Notes, security and best practices
- Prefer connecting Replit via GitHub OAuth (Option A) or using deploy keys (Option B) rather than embedding PATs in URLs.
- Do NOT commit secrets (tokens, private keys) to the repository. Use Replit Secrets or environment variables.
- If you made the repo public temporarily, remember to revert visibility after import.

If you'd like, I can also create a short `start-replit.sh` hook (already present) and `replit.nix` (already present) — both included — plus this guide is committed so you can follow the exact steps inside Replit.
