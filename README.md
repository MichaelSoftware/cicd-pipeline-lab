# Activity 22 — End-to-End CI/CD Pipeline (FastAPI + Docker)

This is the **capstone activity** — it combines everything from Activities 19, 20, and 21 into one end-to-end automated pipeline.

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
