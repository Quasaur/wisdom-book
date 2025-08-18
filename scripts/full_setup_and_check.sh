#!/usr/bin/env bash
#
# One-shot backend bootstrap + verification.
#
# Features:
#  - Creates/uses backend/.venv
#  - Installs requirements
#  - Copies .env.example -> .env (if missing)
#  - Applies migrations
#  - Optional non-interactive superuser (requires DJANGO_SUPERUSER_* env vars)
#  - Runs system checks
#  - Spins up dev server (background) and curls health/topics/search endpoints
#  - Runs Neo4j health script if credentials present
#  - Summarizes pass/fail
#
# Exit codes:
#   0 success
#   1 failure in steps
#
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
VENV_DIR="${BACKEND_DIR}/.venv"
PYTHON_BIN="python3"
MANAGE="${BACKEND_DIR}/manage.py"
PORT="${PORT:-8000}"
SERVER_LOG="${PROJECT_ROOT}/.dev_server.log"
CHECK_ERRORS=()

log() { printf "[%s] %s\n" "$(date +%H:%M:%S)" "$*" ; }

fail() {
  log "ERROR: $*"
  CHECK_ERRORS+=("$*")
}

section() {
  echo
  log "=== $* ==="
}

ensure_python() {
  if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    fail "python3 not found (install via Homebrew: brew install python)"
    exit 1
  fi
}

create_venv() {
  if [ ! -d "${VENV_DIR}" ]; then
    section "Creating virtual environment"
    (cd "${BACKEND_DIR}" && "${PYTHON_BIN}" -m venv .venv)
  fi
}

activate_venv() {
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
}

install_requirements() {
  section "Installing requirements"
  pip install --upgrade pip >/dev/null
  pip install -r "${BACKEND_DIR}/requirements.txt"
}

ensure_env_file() {
  if [ ! -f "${BACKEND_DIR}/.env" ]; then
    if [ -f "${BACKEND_DIR}/.env.example" ]; then
      section "Creating backend/.env from example"
      cp "${BACKEND_DIR}/.env.example" "${BACKEND_DIR}/.env"
      log "Edit backend/.env and set real secrets/Neo4j credentials."
    else
      fail ".env.example not found; cannot scaffold .env"
    fi
  fi
}

django_check() {
  section "Django system check"
  python "${MANAGE}" check || fail "django check failed"
}

django_migrate() {
  section "Applying migrations"
  python "${MANAGE}" migrate --noinput || fail "migrate failed"
}

maybe_create_superuser() {
  if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]] && [[ -n "${DJANGO_SUPERUSER_EMAIL:-}" ]] && [[ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
    section "Creating superuser (non-interactive)"
    python "${MANAGE}" createsuperuser --noinput || fail "superuser creation failed (maybe already exists)"
  else
    log "Skipping superuser (export DJANGO_SUPERUSER_USERNAME / EMAIL / PASSWORD to auto-create)"
  fi
}

start_server() {
  if [ "${#CHECK_ERRORS[@]}" -gt 0 ]; then
    section "Skipping server startup (previous errors present)"
    return
  fi
  section "Starting dev server (background on port ${PORT})"
  if lsof -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
    log "Port ${PORT} in use; attempting to free it."
    lsof -tiTCP:"${PORT}" | xargs -r kill || true
    sleep 1
  fi
  (cd "${BACKEND_DIR}" && python "${MANAGE}" runserver "${PORT}") >"${SERVER_LOG}" 2>&1 &
  SERVER_PID=$! || true
  if [ -z "${SERVER_PID:-}" ]; then
    fail "Could not capture server PID (see ${SERVER_LOG})"
  else
    log "Server PID=${SERVER_PID}"
  fi
}

wait_for_server() {
  if [ -z "${SERVER_PID:-}" ]; then
    section "Skipping readiness wait (server not started)"
    return
  fi
  section "Waiting for server readiness"
  local retries=30
  local ok=0
  for i in $(seq 1 "${retries}"); do
    if curl -fs "http://127.0.0.1:${PORT}/api/neo4j/health/" >/dev/null 2>&1; then
      ok=1; break
    fi
    sleep 0.4
  done
  if [ "${ok}" -ne 1 ]; then
    fail "Server not ready after $((retries*0.4))s (see ${SERVER_LOG})"
  else
    log "Server is responding."
  fi
}

curl_json() {
  local url="$1"
  if ! curl -fsS "${url}" ; then
    fail "Endpoint failed: ${url}"
  fi
  echo
}

probe_endpoints() {
  section "Probing API endpoints"
  curl_json "http://127.0.0.1:${PORT}/api/neo4j/health/"
  curl_json "http://127.0.0.1:${PORT}/api/neo4j/topics/?limit=3"
  curl_json "http://127.0.0.1:${PORT}/api/neo4j/search/?q=demo&limit=2" || true
}

neo4j_health() {
  # Only if env vars present
  if grep -q "^NEO4J_URI" "${BACKEND_DIR}/.env" 2>/dev/null; then
    section "Neo4j health script"
    (cd "${PROJECT_ROOT}" && python scripts/neo4j_health.py) || fail "neo4j health script failed"
  else
    log "Skipping Neo4j health (missing vars)."
  fi
}

stop_server() {
  section "Stopping dev server"
  if [ -n "${SERVER_PID:-}" ] && kill -0 "${SERVER_PID}" 2>/dev/null; then
    kill "${SERVER_PID}" || true
    wait "${SERVER_PID}" 2>/dev/null || true
  fi
}

summary() {
  echo
  section "Summary"
  if [ "${#CHECK_ERRORS[@]}" -eq 0 ]; then
    log "SUCCESS: All steps completed."
    exit 0
  else
    log "FAIL: ${#CHECK_ERRORS[@]} issue(s):"
    for e in "${CHECK_ERRORS[@]}"; do
      log " - ${e}"
    done
    log "See ${SERVER_LOG} for server output (if applicable)."
    exit 1
  fi
}

trap 'fail "Script interrupted"; stop_server; summary' INT TERM

main() {
  section "Backend full setup & verification"
  ensure_python
  create_venv
  activate_venv
  install_requirements
  ensure_env_file
  django_check
  django_migrate
  maybe_create_superuser
  # If critical steps failed, summarize early
  if [ "${#CHECK_ERRORS[@]}" -gt 0 ]; then
    section "Early summary (errors block runserver)"
    summary
  fi
  start_server
  wait_for_server
  neo4j_health
  probe_endpoints
  stop_server
  summary
}

main "$@"
