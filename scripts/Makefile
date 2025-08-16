PYTHON ?= python3
VENV := .venv
REQ := backend/requirements.txt
ACTIVATE := . $(VENV)/bin/activate

.PHONY: help venv install reinstall freeze check neo4j-health lint fmt test clean

help:
    @grep -E '^[a-zA-Z_-]+:.*?##' Makefile | awk 'BEGIN {FS=":.*?## "}; {printf "%-18s %s\n", $$1, $$2}'

venv: ## Create virtual environment
    $(PYTHON) -m venv $(VENV)
    $(ACTIVATE); pip install --upgrade pip setuptools wheel

install: venv ## Install deps from backend/requirements.txt
    $(ACTIVATE); pip install -r $(REQ)

reinstall: ## Recreate venv + reinstall
    rm -rf $(VENV)
    $(MAKE) install

freeze: ## Snapshot resolved versions
    $(ACTIVATE); pip freeze > backend/requirements.lock

check: ## Smoke test Django + neo4j imports
    $(ACTIVATE); python -c "import django, neo4j; print('OK Django', django.get_version())"

neo4j-health: ## Connectivity check (needs env vars)
    $(ACTIVATE); python scripts/neo4j_health.py

lint: ## Ruff + Black + mypy (non-fatal mypy)
    $(ACTIVATE); ruff check backend
    $(ACTIVATE); black --check backend
    $(ACTIVATE); mypy backend || true

fmt: ## Auto-format
    $(ACTIVATE); black backend
    $(ACTIVATE); ruff check backend --fix

test: ## Run pytest (cov if configured)
    $(ACTIVATE); pytest -q

clean: ## Remove caches & venv
    find . -name '__pycache__' -prune -exec rm -rf {} \;
    rm -rf .mypy_cache .pytest_cache