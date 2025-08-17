#!/usr/bin/env python
"""
verify_requirements.py

Purpose:
- Ensures installed distributions match the specifiers in backend/requirements.txt.
- Reports:
  * not installed
  * version mismatch (outside specifier)
  * pinned mismatch (== but different installed version)
- Optionally rewrites requirements.txt with exact installed versions (pinning everything).

Usage:
  python backend/scripts/verify_requirements.py
  python backend/scripts/verify_requirements.py --write-pin   # rewrites file with ==installed

Exit codes:
  0 = all good (or rewrite performed)
  1 = mismatches found (no rewrite)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
import re
from typing import List

try:
    from importlib import metadata as importlib_metadata
except ImportError:  # pragma: no cover
    import importlib.metadata as importlib_metadata  # type: ignore

try:
    from packaging.requirements import Requirement
    from packaging.version import Version
    from packaging.utils import canonicalize_name
except ImportError:  # pragma: no cover
    print("ERROR: 'packaging' is required. Install it first.", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
REQ_FILE = ROOT / "backend" / "requirements.txt"


def parse_requirements(text: str) -> List[str]:
    """
    Return clean requirement spec strings:
    - Drop blank lines and full-line comments.
    - Strip inline comments introduced by '#' (PEP 508 parser does not accept them).
    - Preserve the spec part only.
    """
    cleaned: List[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # Strip trailing inline comment
        spec = line.split("#", 1)[0].strip()
        if spec:
            cleaned.append(spec)
    return cleaned


def load_installed() -> dict:
    data = {}
    for dist in importlib_metadata.distributions():
        name = dist.metadata.get("Name")
        if name:
            data[canonicalize_name(name)] = dist.version
    return data


def requirement_display(req: Requirement) -> str:
    if req.specifier:
        return f"{req.name}{req.specifier}"
    return req.name


def rewrite_pinned(original_text: str, installed: dict) -> str:
    """
    Replace each requirement line with an exact pin ==installed_version
    Preserves comments and blank lines.
    """
    out_lines = []
    for line in original_text.splitlines():
        raw = line.rstrip("\n")
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            out_lines.append(raw)
            continue
        # Extract requirement portion (ignore inline comments)
        parts = re.split(r"\s+#", raw, maxsplit=1)
        req_part = parts[0].strip()
        comment = ""
        if len(parts) > 1:
            comment = "#" + parts[1]

        try:
            req = Requirement(req_part)
        except Exception:
            out_lines.append(raw)  # leave unparseable line
            continue

            # Determine installed version
        inst_ver = installed.get(req.name.lower())
        if not inst_ver:
            # keep as-is if not installed
            out_lines.append(raw)
            continue
        new_line = f"{req.name}=={inst_ver}"
        if comment:
            new_line = f"{new_line}  {comment}"
        out_lines.append(new_line)
    return "\n".join(out_lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-pin", action="store_true", help="Rewrite requirements.txt pinning to current installed versions.")
    parser.add_argument("--debug", action="store_true", help="Show diagnostic environment info.")
    args = parser.parse_args()

    if not REQ_FILE.exists():
        print(f"ERROR: requirements file not found: {REQ_FILE}", file=sys.stderr)
        return 2

    text = REQ_FILE.read_text(encoding="utf-8")
    raw_reqs = parse_requirements(text)
    installed = load_installed()
    if args.debug:
        print(f"[DEBUG] Python executable: {sys.executable}")
        print(f"[DEBUG] Requirements file: {REQ_FILE}")
        print(f"[DEBUG] Installed packages count: {len(installed)}")

    mismatches = []
    details = []

    for line in raw_reqs:
        try:
            req = Requirement(line)
        except Exception as e:
            details.append(f"[SKIP] {line} (unparseable: {e})")
            continue

        inst_ver = installed.get(canonicalize_name(req.name))
        if not inst_ver:
            mismatches.append(req.name)
            details.append(f"[MISSING] {requirement_display(req)} (not installed)")
            continue

        version_obj = Version(inst_ver)
        if req.specifier:
            if not req.specifier.contains(version_obj, prereleases=True):
                mismatches.append(req.name)
                details.append(f"[OUT-OF-RANGE] {requirement_display(req)} installed={inst_ver}")
            else:
                specs = list(req.specifier)
                pinned_spec = specs[0] if len(specs) == 1 and specs[0].operator == "==" else None
                if pinned_spec and inst_ver != pinned_spec.version:
                    mismatches.append(req.name)
                    details.append(f"[PIN-MISMATCH] {requirement_display(req)} installed={inst_ver}")
                else:
                    if pinned_spec:
                        details.append(f"[OK] {req.name}=={inst_ver}")
                    else:
                        details.append(f"[OK] {req.name} {req.specifier} (installed {inst_ver})")
        else:
            details.append(f"[UNSPECIFIED] {req.name} installed={inst_ver} (no specifier in file)")

    print("\n".join(details))

    if args.write_pin:
        new_text = rewrite_pinned(text, installed)
        REQ_FILE.write_text(new_text, encoding="utf-8")
        print(f"\nRewrote {REQ_FILE} with pinned versions.")
        return 0

    if mismatches:
        print(f"\nFAIL: {len(mismatches)} mismatch(es) detected.")
        print("To pin current environment: python backend/scripts/verify_requirements.py --write-pin")
        return 1

    print("\nSUCCESS: All installed versions satisfy current specifiers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
