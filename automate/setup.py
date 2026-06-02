#!/usr/bin/env python3
"""
Customize template files for a student's assigned domain.

Reads automate/options.csv, selects a row based on the GitHub repository name
(stable hash → row index), and replaces {{placeholder}} tokens in all template
files. Subsequent runs are no-ops once placeholders are replaced.

"""

import csv
import hashlib
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OPTIONS_CSV = Path(__file__).resolve().parent / "options.csv"

# Files that contain {{placeholders}} and must be customized
TEMPLATE_FILES = [
    "README.md",
    "gse.xtext.assignment.tests/src/gse/xtext/assignment/tests/AccessPoliciesCodeGenTest.xtend",
    "gse.xtext.assignment.tests/src/gse/xtext/assignment/tests/AccessPoliciesParsingTest.xtend",
]

PLACEHOLDER_RE = re.compile(r"\{\{[a-zA-Z0-9_]+\}\}")


# ── Helpers ───────────────────────────────────────────────────────────────────


def select_row(rows: list[dict]) -> dict:
    """Pick a row deterministically from the GitHub repository name."""
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    repo_name = repo.split("/")[-1] if "/" in repo else repo
    if not repo_name:
        return rows[0]
    index = int(hashlib.sha256(repo_name.encode()).hexdigest(), 16) % len(rows)
    return rows[index]


def build_replacements(row: dict) -> dict:
    """Return a flat {placeholder: value} dict for all keys"""
    replacements: dict[str, str] = {}
    for key, value in row.items():
        replacements[f"{{{{{key}}}}}"] = value                      # {{role1}}

    return replacements


def needs_customization() -> bool:
    """Return True if any template file still contains {{...}} tokens."""
    for rel in TEMPLATE_FILES:
        path = REPO_ROOT / rel
        if path.exists() and PLACEHOLDER_RE.search(path.read_text(encoding="utf-8")):
            return True
    return False


def apply_replacements(replacements: dict[str, str]) -> None:
    for rel in TEMPLATE_FILES:
        path = REPO_ROOT / rel
        if not path.exists():
            print(f"  [skip] {rel} — file not found", file=sys.stderr)
            continue
        content = path.read_text(encoding="utf-8")
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        path.write_text(content, encoding="utf-8")
        print(f"  [done] {rel}")


def main() -> None:
    if not needs_customization():
        print("Repository already customized — nothing to do.")
        return

    with open(OPTIONS_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("ERROR: options.csv is empty", file=sys.stderr)
        sys.exit(1)

    row = select_row(rows)
    print(f"Selected domain: {row['domain_name']}")
    for key in rows[0].keys():
        print(f"  {key:12s}: {row[key]}")

    replacements = build_replacements(row)
    apply_replacements(replacements)

if __name__ == "__main__":
    main()
