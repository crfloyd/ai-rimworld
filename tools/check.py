#!/usr/bin/env python3
"""Offline checks only: Python syntax, local links, templates, and behavior fixtures."""

import ast
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    errors = []
    for path in (ROOT / "tools").rglob("*.py"):
        try:
            ast.parse(path.read_text(), filename=str(path))
        except SyntaxError as exc:
            errors.append(str(exc))
    for folder in ("templates", "knowledge", "tests/fixtures"):
        for path in (ROOT / folder).rglob("*.json"):
            try:
                json.loads(path.read_text())
            except ValueError as exc:
                errors.append(f"{path}: {exc}")
    for folder in (ROOT, ROOT / "docs", ROOT / "knowledge", ROOT / "templates", ROOT / "profiles"):
        paths = folder.glob("*.md") if folder == ROOT else folder.rglob("*.md")
        for path in paths:
            for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", path.read_text()):
                target = target.strip("<>").split("#")[0]
                if not target or "://" in target:
                    continue
                if not (path.parent / target).exists():
                    errors.append(f"Broken local link in {path}: {target}")
    if errors:
        print("\n".join(errors))
        return 1
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    print("Offline only: no game endpoint, live UI, or saves accessed.")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
