#!/usr/bin/env python3
"""
validate_notebooks.py — find and diagnose broken Jupyter notebooks.

Scans a directory tree for *.ipynb files, checks that each is valid JSON
(and, optionally, a valid notebook per nbformat), and prints the exact
location of the first error with a few lines of surrounding context so you
can see the problem immediately.

Usage
-----
    # scan ./docs (default) and report problems
    python validate_notebooks.py

    # scan a different directory
    python validate_notebooks.py --root docs

    # also validate notebook structure, not just JSON (needs nbformat)
    python validate_notebooks.py --nbformat

    # attempt safe automatic repairs (BOM strip + nbformat re-serialize)
    python validate_notebooks.py --fix

Exit status is 0 if everything is valid, 1 if any notebook is invalid.
"""

import argparse
import glob
import json
import os
import sys


def find_notebooks(root):
    """Return a sorted list of .ipynb paths under root (recursive)."""
    pattern = os.path.join(root, "**", "*.ipynb")
    return sorted(glob.glob(pattern, recursive=True))


def context_around(text, lineno, colno, radius=5):
    """Return numbered source lines around (lineno, colno) with a caret marker."""
    lines = text.splitlines()
    if not lines:
        return "  (file is empty)"
    start = max(1, lineno - radius)
    end = min(len(lines), lineno + radius)
    width = len(str(end))
    out = []
    for i in range(start, end + 1):
        marker = ">>" if i == lineno else "  "
        out.append(f"{marker} {str(i).rjust(width)} | {lines[i - 1]}")
        if i == lineno and colno and colno >= 1:
            # caret line: account for marker + number + " | " prefix
            prefix = len(marker) + 1 + width + 3
            out.append(" " * (prefix + colno - 1) + "^")
    return "\n".join(out)


def strip_bom(path):
    """Remove a leading UTF-8 BOM if present. Returns True if changed."""
    with open(path, "rb") as f:
        data = f.read()
    if data.startswith(b"\xef\xbb\xbf"):
        with open(path, "wb") as f:
            f.write(data[3:])
        return True
    return False


def check_conflict_markers(text):
    """Return line numbers that look like git merge-conflict markers."""
    markers = ("<<<<<<<", "=======", ">>>>>>>")
    hits = []
    for i, line in enumerate(text.splitlines(), start=1):
        if line.startswith(markers):
            hits.append((i, line[:40]))
    return hits


def try_nbformat_rewrite(path):
    """Re-read and re-write with nbformat to normalize. Returns (ok, message)."""
    try:
        import nbformat
    except ImportError:
        return False, "nbformat not installed (pip install nbformat)"
    try:
        nb = nbformat.read(path, as_version=4)
        nbformat.write(nb, path)
        return True, "re-serialized with nbformat"
    except Exception as e:  # noqa: BLE001 - want the raw diagnostic
        return False, f"nbformat could not repair: {e}"


def validate_one(path, use_nbformat=False, fix=False):
    """
    Validate a single notebook.
    Returns (is_valid, detail_string_or_None).
    """
    # Optional repair pass first, so we validate the repaired file.
    repairs = []
    if fix and strip_bom(path):
        repairs.append("removed UTF-8 BOM")

    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError as e:
        return False, f"not valid UTF-8 -> {e}"

    conflicts = check_conflict_markers(text)
    if conflicts:
        loc = ", ".join(f"line {ln}" for ln, _ in conflicts)
        return False, f"contains git merge-conflict markers at {loc}"

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        detail = f"{e.msg}: line {e.lineno} column {e.colno}"
        ctx = context_around(text, e.lineno, e.colno)
        if fix:
            # Last-ditch: let nbformat try to normalize/repair.
            ok, msg = try_nbformat_rewrite(path)
            if ok:
                # Re-validate after the rewrite.
                return validate_one(path, use_nbformat=use_nbformat, fix=False)
            return False, f"{detail}\n{ctx}\n  auto-fix: {msg}"
        return False, f"{detail}\n{ctx}"

    if use_nbformat:
        try:
            import nbformat
            nbformat.validate(data)
        except ImportError:
            return False, "nbformat requested but not installed (pip install nbformat)"
        except Exception as e:  # nbformat.ValidationError and friends
            return False, f"JSON is valid but notebook schema is not: {e}"

    ok_note = f" ({'; '.join(repairs)})" if repairs else ""
    return True, ok_note or None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate Jupyter notebooks (JSON and optionally notebook schema)."
    )
    parser.add_argument(
        "--root", default="docs",
        help="Directory to scan recursively (default: docs)",
    )
    parser.add_argument(
        "--nbformat", action="store_true",
        help="Also validate notebook structure via nbformat, not just JSON",
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="Attempt safe repairs: strip BOM, then nbformat re-serialize",
    )
    args = parser.parse_args(argv)

    if not os.path.isdir(args.root):
        print(f"error: directory not found: {args.root}", file=sys.stderr)
        return 2

    notebooks = find_notebooks(args.root)
    if not notebooks:
        print(f"No .ipynb files found under {args.root}/")
        return 0

    bad = []
    fixed = []
    for path in notebooks:
        ok, detail = validate_one(path, use_nbformat=args.nbformat, fix=args.fix)
        if ok:
            if detail:  # a repair note
                fixed.append(path)
                print(f"FIXED   {path}{detail}")
        else:
            bad.append(path)
            print(f"INVALID {path}")
            print("        " + detail.replace("\n", "\n        "))
            print()

    total = len(notebooks)
    print("-" * 60)
    print(f"Scanned {total} notebook(s) under {args.root}/")
    if fixed:
        print(f"Repaired {len(fixed)}")
    if bad:
        print(f"Invalid  {len(bad)}")
        return 1
    print("All notebooks are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
