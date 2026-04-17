# Activity 22 — End-to-End CI/CD Pipeline (FastAPI + Docker)

A complete production-style CI/CD pipeline. Every push to `main` automatically:

```
Run Tests  →  Build Docker Image  →  Push to Docker Hub  →  Deploy
```

This is the **capstone activity** — it combines everything from Activities 19, 20, and 21 into one end-to-end automated pipeline.

## Architecture

```
Developer pushes code
       │
       ▼
┌──────────────┐
│   GitHub     │
└──────┬───────┘
       │ on: push to main
       ▼
┌──────────────────────────────────────────────────────┐
│  GitHub Actions Runner (Ubuntu)                      │
│                                                      │
│   1. Checkout code                                   │
│   2. Run pytest  ──── (fail → pipeline stops)        │
│   3. Build Docker image                              │
│   4. Login to Docker Hub                             │
│   5. Push image: USERNAME/myapp:latest + :sha        │
│   6. Deploy (simulated, or SSH to VM)                │
└──────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│  Docker Hub  │  ← image is now publicly pullable
└──────────────┘
```

## Project structure

```
activity-22-cicd-pipeline/
├── app/
│   ├── __init__.py          ← Makes `app` an importable package
│   └── main.py              ← FastAPI application
├── tests/
│   └── test_main.py         ← 4 pytest tests
├── .github/
│   └── workflows/
│       └── ci-cd.yml        ← The CI/CD pipeline
├── Dockerfile
├── requirements.txt
├── .dockerignore
└── .gitignore
```

## Prerequisites

- All the prereqs from Activity 21 (Git, GitHub account, ability to push)
- A **Docker Hub account** (free — sign up at https://hub.docker.com)
- Docker Desktop running locally (only if you want to test the build locally before pushing)

---

## Phase 1 — Test everything locally first (~3 min)

Before wiring up CI/CD, verify the app and tests work on your machine.

### 1a. Install dependencies
```bash
cd activity-22-cicd-pipeline
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 1b. Run tests
```bash
pytest -v
```
**Expected:** `4 passed`. If not, fix it before proceeding — CI won't magically make failing tests pass.

### 1c. Run the app
```bash
uvicorn app.main:app --reload --port 8000
```
Open **http://localhost:8000/** — you should see `{"message":"Hello CI/CD"}`.
Also try:
- http://localhost:8000/health
- http://localhost:8000/greet/Michael
- http://localhost:8000/docs (auto-generated Swagger)

Stop with `Ctrl+C`.

### 1d. (Optional) Build and run the Docker image locally
```bash
docker build -t myapp:latest .
docker run -d -p 8080:80 --name myapp-local myapp:latest
curl http://localhost:8080/
docker stop myapp-local && docker rm myapp-local
```
> Note: the container listens on port **80** inside (see the `CMD` in the Dockerfile), mapped to host port 8080 here. The handout's Dockerfile uses port 80 to match production web-server conventions.

---

## Phase 2 — Set up Docker Hub (~5 min, one-time)

The pipeline pushes images to Docker Hub. You need an account and an access token.

### 2a. Create a Docker Hub account
Go to https://hub.docker.com and sign up. **Your Docker Hub username** is what you'll reference as `DOCKER_USERNAME` later.

### 2b. Create an access token (safer than using your password)
1. Log in to Docker Hub
2. Click your avatar (top right) → **Account Settings**
3. Left sidebar → **Personal access tokens**
4. Click **Generate new token**
5. Description: `github-actions`
6. Access permissions: **Read, Write, Delete** (or just Read & Write)
7. Click **Generate** → **copy the token immediately** — you can't see it again after closing the dialog
8. Paste it somewhere temporarily; you'll need it in Phase 3

### 2c. (Optional) Create the `myapp` repo ahead of time
Docker Hub will auto-create it on first push if your account is public. If your account is private, create it manually: **Repositories → Create repository → name: `myapp`**.

---

## Phase 3 — Push the project to GitHub (~3 min)

### 3a. Create a new GitHub repo
1. https://github.com/new
2. Name: `cicd-pipeline-lab` (or whatever)
3. Public or Private — either works
4. **Don't** check "Add a README" — leave it empty

### 3b. Init and push
From inside `activity-22-cicd-pipeline/`:
```bash
git init
git add .
git commit -m "Initial commit: CI/CD pipeline"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/cicd-pipeline-lab.git
git push -u origin main
```

> The pipeline will **trigger immediately** on this first push. Go to the Actions tab and watch it.

---

## Phase 4 — Configure secrets (~2 min)

Without secrets, the pipeline's "test" and "build" jobs still run — but the "push to Docker Hub" step will be skipped. To enable the push, add these two secrets:

### 4a. Add Docker Hub credentials as repo secrets

1. In your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add **DOCKER_USERNAME**:
   - Name: `DOCKER_USERNAME`
   - Value: your Docker Hub username
4. Click **New repository secret** again
5. Add **DOCKER_PASSWORD**:
   - Name: `DOCKER_PASSWORD`
   - Value: the access token you generated in Phase 2b (**not** your actual account password)

### 4b. Re-run the pipeline
You have two options:
- **Re-run the last workflow** — Actions tab → click the latest run → top right **Re-run all jobs**
- **Push a trivial commit**:
  ```bash
  git commit --allow-empty -m "Trigger CI with Docker Hub secrets"
  git push
  ```

Watch the pipeline run. This time the "Push Image to Docker Hub" step will execute (no longer skipped). When it finishes, check **Docker Hub** — your repo should show two new tags: `latest` and a long commit SHA.

---

## Phase 5 — Pull and run your deployed image (the payoff)

From any machine with Docker:
```bash
docker pull YOUR-DOCKERHUB-USERNAME/myapp:latest
docker run -d -p 8080:80 --name myapp YOUR-DOCKERHUB-USERNAME/myapp:latest
curl http://localhost:8080/
```
**Expected:** `{"message":"Hello CI/CD"}`

You just deployed code from GitHub → tests ran → Docker built → image pushed to Docker Hub → you pulled it on another machine. **That's a complete CI/CD cycle.**

---

## The "wow" moments for demo day

### Demo 1 — Break a test, watch CI catch it
Edit `tests/test_main.py`, change:
```python
assert response.json() == {"message": "Hello CI/CD"}
```
to:
```python
assert response.json() == {"message": "deliberately wrong"}
```
Push. Watch the pipeline fail red — the `build` and `deploy` jobs never run because `test` failed (that's what `needs: test` enforces). Revert and push again, it goes green.

### Demo 2 — Show the image running from Docker Hub
After secrets are set up and a push has completed:
```bash
docker pull YOUR-USERNAME/myapp:latest
docker run -d -p 8080:80 --name demo YOUR-USERNAME/myapp:latest
open http://localhost:8080/docs     # Mac — opens the Swagger UI
```
You're running a container that GitHub Actions built and published.

### Demo 3 — Show a status badge on the README
Add to the top of your repo's README:
```markdown
![CI/CD](https://github.com/YOUR-USERNAME/cicd-pipeline-lab/actions/workflows/ci-cd.yml/badge.svg)
```
Push. The badge shows pass/fail live from your pipeline.

---

## (Optional) Phase 6 — Real deployment to a VM

The handout's Step 8 describes deploying to an actual server via SSH. The `deploy` job in `ci-cd.yml` has this commented out at the bottom — uncomment it to enable.

**You need:**
- A Linux VM (AWS EC2, DigitalOcean droplet, any cloud VM) with Docker installed
- Three more secrets:
  - `SERVER_IP` — the VM's public IP
  - `SERVER_USER` — SSH username (e.g. `ubuntu` for EC2)
  - `SERVER_SSH_KEY` — the **private key** for SSH (paste the full contents of your `.pem` or `id_rsa` file)

Once secrets are set and the job is uncommented, each push pulls the freshly-built image onto your VM, stops the old container, and starts a new one — **zero-downtime-ish deployment.**

**This is the full production pattern.** Same shape as what real companies ship.

---

## Workflow details

### What runs in each job
| Job | Runs | Purpose |
|-----|------|---------|
| `test` | Ubuntu runner, Python 3.11 | Checks out code, installs deps, runs pytest |
| `build` | Ubuntu runner | Builds the Docker image; if secrets are set, also pushes to Docker Hub |
| `deploy` | Ubuntu runner | Simulated deploy (prints a message). Uncomment SSH block for real deployment. |

### Why `needs:` is critical
`build` has `needs: test` and `deploy` has `needs: build`. If any step in `test` fails, neither `build` nor `deploy` run. This is the safety net — broken code can't reach production.

### Why tag with commit SHA as well as `latest`
Only tagging `latest` means every push overwrites the same tag. Tagging with `${{ github.sha }}` gives every build a permanent, traceable identifier — so if `latest` breaks production, you can roll back to a specific previous build by its commit hash.

---

## Enhancements beyond the lab handout

| Handout | This version |
|---------|-------------|
| Pipeline fails on first push if secrets aren't set yet | Push step is guarded with `if: ${{ secrets.DOCKER_USERNAME != '' }}` — pipeline runs green even before secrets are configured |
| Only pushes `:latest` tag | Also pushes `:${{ github.sha }}` for traceability/rollback |
| Missing `__init__.py` in `app/` | Added, so `from app.main import app` actually works |
| Missing `httpx` dep (required by FastAPI's `TestClient`) | Added to `requirements.txt` |
| 1 test | 4 tests covering home, health, path params, and 404 handling |
| No `.dockerignore` | Added — excludes venv, caches, git metadata from the build context |
| `workflow_dispatch` missing | Added — lets you manually trigger runs from the Actions UI |
| SSH deploy mentioned in prose | Included as commented-out block in the workflow, ready to uncomment |

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Pipeline fails on "Run Tests" | Run `pytest -v` locally — fix the failures there first. |
| `ModuleNotFoundError: No module named 'app'` in CI | Make sure `app/__init__.py` exists and is committed. |
| "Login to Docker Hub" step fails with "401 Unauthorized" | `DOCKER_PASSWORD` is wrong — regenerate the access token and update the secret. |
| "Push" step fails with "denied: requested access to the resource is denied" | Username in the image tag doesn't match your Docker Hub account, or the repo is private and your token lacks push permission. |
| Image pushed but `docker pull` returns "not found" | Repository is private — either make it public on Docker Hub, or `docker login` before pulling. |
| First push triggers workflow but it shows "Skipping" for Docker Hub steps | Expected — you haven't set `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets yet. Add them and re-run. |

---

## Learning outcomes
✔ Design and build a complete CI/CD pipeline from scratch
✔ Integrate testing, Docker builds, container registry, and deployment into one automated flow
✔ Use repository secrets to safely handle credentials in automation
✔ Understand `needs:` dependencies to gate downstream jobs on upstream success
✔ Tag container images with both semantic (`latest`) and traceable (`:sha`) identifiers
✔ Connect GitHub → Docker Hub → deployment target in a continuous pipeline
