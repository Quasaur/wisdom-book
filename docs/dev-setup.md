# Development Environment Setup (Backend Python)

Purpose: Define a reproducible Python environment for the Django + Neo4j backend.

## 1. Prerequisites

- macOS Sequoia
- Homebrew (recommended)
- Python 3.11 or 3.12 installed (`python3 -V`)
- Git
- (Optional) pyenv or uv for version management
- Neo4j AuraDB credentials (kept in `.env`, never committed)

## 2. Check If a Virtual Environment Already Exists

```bash
ls -d .venv venv 2>/dev/null
# If one exists, activate:
source .venv/bin/activate 2>/dev/null || source venv/bin/activate
which python
python -V
```

If `which python` points inside the project directory, you are inside a venv.

## 3. Create a Virtual Environment

### Option A: Stdlib venv (simple)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

### Option B: pyenv (explicit version pin)

```bash
brew install pyenv
pyenv install 3.12.4
pyenv virtualenv 3.12.4 wisdom-book-312
pyenv local wisdom-book-312
pip install -r backend/requirements.txt
```

### Option C: uv (fast resolver)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -r backend/requirements.txt
```

## 4. Environment Variables

Create `backend/.env` (NOT committed) using `backend/.env.example`:

```
NEO4J_URI=neo4j+s://<your-instance>.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=***
NEO4J_DATABASE=neo4j
```

Load automatically during Django startup using `python-dotenv` (ensure code loads it—planned in `neo4j_service.py` / settings).

## 5. Verifying Dependencies

After install:

```bash
python -m pip list | grep Django
python backend/scripts/verify_requirements.py
```

If mismatches reported and you want to pin exact versions:

```bash
python backend/scripts/verify_requirements.py --write-pin
git diff backend/requirements.txt
```

Commit only if you intentionally want to lock.

## 6. Running Backend (placeholder)

```bash
cd backend
python manage.py runserver
```

(Will work after Django project skeleton is added.)

## 7. Test & Lint

```bash
pytest -q
ruff check .
black --check .
mypy .
```

(Optional pre-commit once configured):

```bash
pre-commit install
pre-commit run --all-files
```

## 8. Upgrading Dependencies

```bash
source .venv/bin/activate
pip install -U <package>
python backend/scripts/verify_requirements.py --write-pin   # if locking
```

## 9. Cleaning / Rebuild

```bash
deactivate || true
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

## 10. Quick Commands Cheat Sheet

| Action | Command |
|--------|---------|
| Create venv | `python3 -m venv .venv` |
| Activate | `source .venv/bin/activate` |
| Install deps | `pip install -r backend/requirements.txt` |
| Verify | `python backend/scripts/verify_requirements.py` |
| Pin | `python backend/scripts/verify_requirements.py --write-pin` |
| Deactivate | `deactivate` |
| Remove venv | `rm -rf .venv` |

## 11. Common Issues

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError` | Activate venv or reinstall requirements |
| `ssl.SSLError` hitting Aura | Ensure Python >= 3.11, update certs (`/Applications/Python.../Install Certificates.command`) |
| Env vars not loading | Confirm `.env` exists and loader code executes early |

## 12. Next Steps

- Add Django project skeleton (`backend/wisdom-book/`).
- Implement `neo4j_service.py` with lazy driver init.
- Add `.env.example` if missing & commit it (no secrets).
