[CI/CD](https://github.com/YOUR-USERNAME/cicd-pipeline-lab/actions/workflows/ci-cd.yml/badge.svg)
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
