#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
REQ_FILE="backend/requirements.txt"
VENV_DIR=".venv"

if [ ! -f "$REQ_FILE" ]; then
  echo "Requirements file not found: $REQ_FILE" >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "[+] Creating virtual environment in $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

echo "[+] Upgrading pip tooling"
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel

echo "[+] Installing dependencies from $REQ_FILE"
"$VENV_DIR/bin/pip" install -r "$REQ_FILE"

echo "[+] Verifying core imports"
"$VENV_DIR/bin/python" - <<'PY'
import django, neo4j
print("Django Version:", django.get_version())
print("Neo4j driver import OK")
PY

cat <<EOF

Environment ready.

Activate:
  source $VENV_DIR/bin/activate

Next:
  cp .env.example .env  # then edit with real values (DO NOT COMMIT)

EOF