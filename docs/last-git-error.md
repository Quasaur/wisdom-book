git push origin main
To https://github.com/Quasaur/wisdom-book.git
 ! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to 'https://github.com/Quasaur/wisdom-book.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. Integrate the remote changes (e.g.
hint: 'git pull ...') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.

## Cause

Your local `main` is behind `origin/main`. Git blocks the push to prevent losing remote commits.

## Quick Fix Matrix

| Situation | Command Sequence |
|-----------|------------------|
| Only behind (no local commits) | `git fetch origin && git reset --hard origin/main` |
| Behind + you have local commits | `git fetch origin && git rebase origin/main && git push` |
| Want merge (not linear) | `git pull --no-rebase && git push` |
| Remote updated during your work | `git fetch origin && git rebase origin/main && git push` |
| Must overwrite remote (last resort) | `git push --force-with-lease` |

## Step-by-Step (Recommended Linear Workflow)

```bash
# 1. Ensure on main
git branch --show-current

# 2. Fetch remote refs
git fetch origin

# 3. Show what you have locally that's not remote
git log --oneline origin/main..main

# 4a. If output EMPTY -> only behind:
git reset --hard origin/main
# (Now recreate / recommit any intended changes, then:)
git push origin main

# 4b. If output shows commits (you have local work):
git rebase origin/main

# (Resolve conflicts if they appear)
#   Edit files, then:
git add <file1> <file2>
git rebase --continue

# 5. After successful rebase:
git push origin main
```

## Conflict Resolution Pattern

During rebase when conflict arises:
1. `git status` (see conflicted files)
2. Edit & fix
3. `git add <file>`
4. `git rebase --continue`
5. If you must abort: `git rebase --abort`

## Safety: Uncommitted Changes

```bash
git stash push -m "pre-rebase"
# ... do rebase ...
git stash pop
```

## Verification

```bash
git log --oneline -n 5
git push origin main
```

If push succeeds, the rejection is resolved.

## Last Resort (Overwrite)

Only if you intentionally want your local history to replace remote (confirm no one else relies on remote commits):

```bash
git push origin main --force-with-lease
```

(`--force-with-lease` protects against overwriting new remote work you have not fetched.)

## Helpful Aliases (Optional)

Add to `~/.gitconfig`:

```
[alias]
  lg = log --oneline --graph --decorate --all --max-count=30
  ff = pull --ff-only
```

## Summary

1. Always `git fetch origin` first.  
2. Decide: fast-forward vs rebase vs merge.  
3. Rebase for a clean linear history.  
4. Use `--force-with-lease` only when rewriting already-published commits intentionally.

## Example: Resolving a `.gitignore` Conflict During Rebase

When `git rebase origin/main` stops with:
```
CONFLICT (content): Merge conflict in .gitignore
error: could not apply f20264f...
```

### 1. Confirm state
```bash
git status
```

### 2. Inspect conflict
Open `.gitignore` and locate markers:
```
<<<<<<< ours
# your version lines
=======
# origin/main lines
>>>>>>> theirs
```

Optional deeper diff:
```bash
git show :2:.gitignore   # ours (current commit being replayed)
git show :3:.gitignore   # theirs (origin/main)
```

### 3. Choose resolution method

Keep remote (theirs):
```bash
git checkout --theirs .gitignore
```

Keep your version (ours):
```bash
git checkout --ours .gitignore
```

Manual merge (common for .gitignore):
- Keep all unique patterns from both sides.
- Remove conflict markers.
- Order/group logically (e.g., IDE, Python, Node, OS).

### 4. Deduplicate (optional)
```bash
awk '!x[$0]++' .gitignore > .gitignore.new && mv .gitignore.new .gitignore
```

### 5. Stage & continue
```bash
git add .gitignore
git rebase --continue
```

### 6. Repeat if more conflicts
Address each file similarly.

### 7. Finish & push
```bash
git push origin main
```

If rejected because remote advanced:
```bash
git fetch origin
git rebase origin/main
git push origin main
```

### 8. Abort (only if you want to stop rebase)
```bash
git rebase --abort
```

### 9. Last resort overwrite (intentional history rewrite)
```bash
git push --force-with-lease origin main
```

## Current Rebase State (Interactive Rebase Paused)

`git status` output shows:
- Rebase stopped after applying commit `f20264f`.
- `.gitignore` is conflicted.
- Several new files staged (.DS_Store, backend/.env, workspace file, scripts, etc.).
- `docs/last-git-error.md` is untracked (safe to add later).

### Goal

Resolve `.gitignore` conflict, prevent committing secrets / OS junk, then continue rebase.

### 1. Resolve `.gitignore` Conflict

Open `.gitignore`, remove conflict markers, keep union of both sides, and ensure these patterns (dedupe if present):

```
# OS
.DS_Store
backend/.DS_Store

# Env / Secrets
.env
*.env
backend/.env

# Editors / Workspace
*.code-workspace
.vscode/
```

Save file, then:
```bash
git add .gitignore
```

(If you want to see only markers quickly: `sed -n '/^<<<<<<<\|^=======\|^>>>>>>>/p' .gitignore`)

### 2. Remove Unwanted Tracked Files Before Continuing

You do not want `.env` or `.DS_Store` in the commit:

```bash
git rm --cached backend/.env 2>/dev/null || true
git rm --cached .DS_Store backend/.DS_Store 2>/dev/null || true
```

### 3. Fix Example Env Filename (Typo)

If `backend/.en.example` is meant to be a template:

```bash
git mv backend/.en.example backend/.env.example
```

(If it was intentional, skip.)

### 4. Verify Staged Set

```bash
git diff --cached --name-status
```

Confirm no real secret content remains (open `backend/.env.example`, not `backend/.env`).

### 5. Continue Rebase

```bash
git rebase --continue
```

If another conflict appears, repeat conflict steps for that file.  
If you decide to abandon: `git rebase --abort`.

### 6. Post-Rebase Commit for This Doc (Optional)

After rebase finishes cleanly:

```bash
git add docs/last-git-error.md
git commit -m "docs: add rebase conflict resolution notes"
```

### 7. Push

```bash
git push origin main
```

If rejected (remote moved):

```bash
git fetch origin
git rebase origin/main
git push origin main
```

### 8. Final Checklist

```bash
git ls-files | grep -E '\.env$|\.DS_Store'   # should output nothing
grep -R "PASSWORD" backend/.env || true      # ensure not committed (file should be absent)
```

If any secret accidentally committed earlier and already on remote, plan a follow-up history rewrite (separate documented procedure).

## Mini Flow Summary

```bash
# While rebase paused
sed -n '/^<<<<<<<\|^=======\|^>>>>>>>/p' .gitignore
# edit .gitignore merging both sides
git add .gitignore
git rm --cached backend/.env .DS_Store backend/.DS_Store 2>/dev/null || true
git mv backend/.en.example backend/.env.example 2>/dev/null || true
git diff --cached --name-only
git rebase --continue
git push origin main
```

## Removing a Stray / Duplicate Virtual Environment (e.g. `envwisdom`)

If you accidentally created multiple virtual environments (e.g. `envwisdom` and `backend/.venv`), keep only one to avoid version mismatch errors in scripts.

### 1. Detect active interpreter
```bash
which python
python -c "import sys; print(sys.prefix)"
```
If it shows the unwanted folder (`envwisdom`), deactivate:
```bash
deactivate 2>/dev/null || true
```

### 2. Activate the canonical env
(Your convention: backend/.venv)
```bash
source backend/.venv/bin/activate
```

### 3. Remove the duplicate safely
```bash
rm -rf envwisdom
```
(Ensure you are in the project root before running.)

### 4. Add ignore patterns (if not already)
Top-level `.gitignore` should include:
```
/envwisdom
/.venv
```

### 5. Re-verify tooling
```bash
which python
python -V
python backend/scripts/verify_requirements.py --debug
```

### 6. Clean stale bytecode (optional)
```bash
find . -name '__pycache__' -prune -exec rm -rf {} +
```

### 7. Commit housekeeping (if `.gitignore` changed)
```bash
git add .gitignore
git commit -m "chore: remove stray envwisdom virtualenv and enforce single venv"
```

Result: A single authoritative environment prevents false “package missing” or version mismatch reports.

## Troubleshooting: `which python` -> "python not found"

Modern macOS no longer ships `python` (only `python3`). Fix:

### 1. Check python3
```bash
which python3 || echo "python3 missing"
python3 -V
```

### 2. (Re)create / activate venv
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
which python
python -V
```
Expected: path ends with `backend/.venv/bin/python`.

### 3. If `python3` missing install via Homebrew
```bash
brew install python
hash -r
which python3
```

### 4. Optional convenience alias
```bash
echo 'alias python=python3' >> ~/.zshrc
exec $SHELL
```

### 5. Verify packages
```bash
pip install -r backend/requirements.txt  # run from repo root if venv already active
python backend/scripts/verify_requirements.py --debug
```

### 6. Common pitfalls
- Forgot to activate venv in a new terminal.
- Removed venv directory; recreate as above.
- Using a different shell session (VSCode integrated vs system Terminal).

Result: `python` resolves inside the virtual environment and project scripts function correctly.

### Troubleshooting: `which python3` shows `/opt/homebrew/bin/python3` (system interpreter)

Cause: Your virtual environment (`backend/.venv`) is not active. When the venv is active the path should end with:
```
.../backend/.venv/bin/python3
```

Fix:

```bash
# From repo root (ensure backend/.venv exists)
ls backend/.venv || python3 -m venv backend/.venv

# Activate it
source backend/.venv/bin/activate

# Verify now
which python3
python3 -V
```

If `which python3` still shows `/opt/homebrew/bin/python3`:
1. You may be in a different shell tab – activate again.
2. Your shell rc file re-aliases python – temporarily run the full path:
   `source backend/.venv/bin/activate && command -v python3`
3. Fish shell users: `source backend/.venv/bin/activate.fish`

Install dependencies (inside venv):
```bash
pip install -r backend/requirements.txt
python backend/scripts/verify_requirements.py --debug
```

Optional helper (adds auto-activation alias):
```bash
echo 'cd() { builtin cd "$@"; if [ -f backend/.venv/bin/activate ]; then source backend/.venv/bin/activate >/dev/null 2>&1 || true; fi; }' >> ~/.zshrc
exec $SHELL
```

Deactivate when done:
```bash
deactivate
```

### Fixing Django IndentationError in neo4j_app/urls.py During Automation

If the setup script fails at "Django system check" with:
```
IndentationError: unexpected indent (neo4j_app/urls.py, line ...)
```
Cause: malformed `neo4j_app/urls.py` (bad indent or stale route pointing to `views.ItemDetailView`).

Fix:
1. Open `backend/neo4j_app/urls.py`
2. Replace contents with:
```python
from django.urls import path
from .api import HealthView, TopicsView, SearchView, ItemDetailView

app_name = "neo4j_app"
urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("topics/", TopicsView.as_view(), name="topics"),
    path("search/", SearchView.as_view(), name="search"),
    path("items/<str:item_type>/<str:item_id>/", ItemDetailView.as_view(), name="item-detail"),
]
```
3. Ensure `ItemDetailView` exists in `backend/neo4j_app/api.py`.
4. Re-run:
```bash
bash scripts/full_setup_and_check.sh
```
If earlier steps failed the script now skips server start and exits with a summary; fix listed errors then rerun.