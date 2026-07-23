#!/usr/bin/env python3
"""vault-gate: validate the vault's record toll — frontmatter, placement, naming, index.

Checks exactly what CONTRIBUTING.md promises and nothing more.
Stdlib only. Exit 0 clean, exit 1 with one line per violation.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TYPED_DIRS = {
    "reports": "report",
    "research": "research",
    "handoffs": "handoff",
    "certifications": "certification",
}
ROOT_MD_ALLOWED = {"INDEX.md", "CONTRIBUTING.md", "AGENTS.md", "README.md"}
FILENAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*\.md$")
REQUIRED_KEYS = ["date", "worker", "type", "mission", "source"]


def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = {}
    for line in parts[1].splitlines():
        m = re.match(r"^(\w+):\s*(.*?)\s*(#.*)?$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return fm


def main() -> int:
    errors = []
    index_text = (ROOT / "INDEX.md").read_text(encoding="utf-8") if (ROOT / "INDEX.md").exists() else ""
    if not index_text:
        errors.append("INDEX.md: missing or empty — the vault is index-first")

    for md in ROOT.glob("*.md"):
        if md.name not in ROOT_MD_ALLOWED:
            errors.append(f"{md.name}: records belong in a typed directory (see CONTRIBUTING.md), not the root")

    for dirname, expected_type in TYPED_DIRS.items():
        d = ROOT / dirname
        if not d.exists():
            continue
        for md in sorted(d.glob("*.md")):
            rel = f"{dirname}/{md.name}"
            if not FILENAME_RE.match(md.name):
                errors.append(f"{rel}: filename must be YYYY-MM-DD-kebab-title.md")
            fm = parse_frontmatter(md.read_text(encoding="utf-8"))
            if fm is None:
                errors.append(f"{rel}: missing frontmatter block")
                continue
            for key in REQUIRED_KEYS:
                if key not in fm:
                    errors.append(f"{rel}: frontmatter missing key '{key}'")
            for key in ("date", "worker", "type"):
                if key in fm and not fm[key]:
                    errors.append(f"{rel}: frontmatter key '{key}' must not be empty")
            if fm.get("type") and fm["type"] != expected_type:
                errors.append(f"{rel}: type '{fm['type']}' does not match directory (expected '{expected_type}')")
            if rel not in index_text:
                errors.append(f"{rel}: no matching line in INDEX.md — a record isn't in the vault until its index line is")

    for line in errors:
        print(f"vault-gate: {line}")
    if errors:
        print(f"vault-gate: {len(errors)} violation(s)")
        return 1
    print("vault-gate: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
