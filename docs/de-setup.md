# Backend Dev Environment

## Prerequisites
- Python 3.12+ (macOS: brew install python@3.12)
- Neo4j Aura credentials
- (Optional) direnv for automatic env loading

## One-Time Setup
```bash
bash scripts/bootstrap_backend_env.sh
source .venv/bin/activate
cp .env.example .env   # edit values; DO NOT COMMIT real secrets
```

## Common Commands
```bash
make install        # install deps (after first venv)
make check          # import smoke test
make neo4j-health   # verify database connectivity
make test           # run tests
make lint           # static analysis
make fmt            # auto-format
make freeze         # write backend/requirements.lock snapshot
```

## Updating Dependencies
1. Edit backend/requirements.txt
2. Run: make reinstall
3. (Optional) make freeze to capture exact versions.

## Troubleshooting
- Missing packages: ensure you are inside venv (`which python` shows .../.venv/bin/python).
- Neo4j auth errors: rotate password in Aura; update .env.
- SSL issues: upgrade driver (pip install -U neo4j).