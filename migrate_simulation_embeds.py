"""Migrate active Bifrost notebooks away from HTML(<iframe ...>) warnings.

Only notebooks referenced by uncommented ``- file:`` entries in _toc.yml are
modified. Markdown, outputs, and unrelated code cells are left untouched.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def active_notebooks() -> list[Path]:
    paths: list[Path] = []
    for raw in (ROOT / "_toc.yml").read_text(encoding="utf-8").splitlines():
        stripped = raw.lstrip()
        if stripped.startswith("#"):
            continue
        match = re.match(r"\s*-\s+file:\s+(.+?)\s*$", raw)
        if not match:
            continue
        stem = match.group(1).strip().strip("'\"")
        candidate = ROOT / f"{stem}.ipynb"
        if candidate.exists():
            paths.append(candidate)
    return paths


def source_text(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def set_source(cell: dict, text: str) -> None:
    cell["source"] = text.splitlines(keepends=True)


def migrate_vis_sim(src: str) -> str | None:
    """Replace the repeated srcdoc-based vis_sim helper with IFrame."""
    if "def vis_sim(" not in src or "display(HTML(" not in src or "<iframe" not in src:
        return None

    return '''from IPython.display import display, IFrame\nimport html\n\ndef vis_sim(sti, width="100%"):\n    with open(sti, "r", encoding="utf-8") as f:\n        innhold = f.read()\n    escaped = html.escape(innhold, quote=True)\n    display(IFrame(\n        "about:blank",\n        width=width,\n        height=200,\n        extras=[\n            f'srcdoc="{escaped}"',\n            'scrolling="no"',\n            'style="border:none;display:block;"',\n            'onload="this.style.height=this.contentWindow.document.body.scrollHeight+\\\'px\\\'"',\n        ],\n    ))\n'''


def migrate_base64_embed(src: str) -> str | None:
    """Convert direct base64 HTML iframe cells to IPython.display.IFrame."""
    if "base64.b64encode" not in src or "HTML(" not in src or "data:text/html;base64" not in src:
        return None

    path_match = re.search(r'''with open\((["'][^"']+["'])\s*,\s*["']r["']''', src)
    height_match = re.search(r'''height=["'](\d+)["']''', src)
    width_match = re.search(r'''width=["']([^"']+)["']''', src)
    if not path_match:
        return None

    path_literal = path_match.group(1)
    height = height_match.group(1) if height_match else "860"
    width = width_match.group(1) if width_match else "100%"

    return f'''from IPython.display import IFrame\nimport base64\n\nwith open({path_literal}, "r", encoding="utf-8") as f:\n    innhold = f.read()\n\nencoded = base64.b64encode(innhold.encode("utf-8")).decode("utf-8")\nIFrame(f"data:text/html;base64,{{encoded}}", width="{width}", height={height})\n'''


def migrate_notebook(path: Path) -> tuple[bool, int]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    count = 0

    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = source_text(cell)
        replacement = migrate_base64_embed(src)
        if replacement is None:
            replacement = migrate_vis_sim(src)
        if replacement is None:
            continue
        set_source(cell, replacement)
        changed = True
        count += 1

    if changed:
        path.write_text(
            json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
    return changed, count


def main() -> None:
    total = 0
    changed_files: list[str] = []
    for path in active_notebooks():
        changed, count = migrate_notebook(path)
        if changed:
            rel = path.relative_to(ROOT).as_posix()
            changed_files.append(rel)
            total += count
            print(f"updated {rel}: {count} embed cell(s)")

    print(f"changed {len(changed_files)} notebook(s), {total} embed cell(s)")


if __name__ == "__main__":
    main()
