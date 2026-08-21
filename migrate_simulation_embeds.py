from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def active_notebooks():
    paths = []
    for raw in (ROOT / "_toc.yml").read_text(encoding="utf-8").splitlines():
        if raw.lstrip().startswith("#"):
            continue
        match = re.match(r"\s*-\s+file:\s+(.+?)\s*$", raw)
        if not match:
            continue
        stem = match.group(1).strip().strip("'\"")
        path = ROOT / f"{stem}.ipynb"
        if path.exists():
            paths.append(path)
    return paths


def source_text(cell):
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def set_source(cell, text):
    cell["source"] = text.splitlines(keepends=True)


def vis_sim_replacement():
    return (
        "from IPython.display import display, IFrame\n"
        "import html\n\n"
        "def vis_sim(sti, width=\"100%\"):\n"
        "    with open(sti, \"r\", encoding=\"utf-8\") as f:\n"
        "        innhold = f.read()\n"
        "    escaped = html.escape(innhold, quote=True)\n"
        "    display(IFrame(\n"
        "        \"about:blank\",\n"
        "        width=width,\n"
        "        height=200,\n"
        "        extras=[\n"
        "            f'srcdoc=\"{escaped}\"',\n"
        "            'scrolling=\"no\"',\n"
        "            'style=\"border:none;display:block;\"',\n"
        "            'onload=\"this.style.height=this.contentWindow.document.body.scrollHeight+\\\'px\\\'\"',\n"
        "        ],\n"
        "    ))\n"
    )


def migrate_vis_sim(source):
    if "def vis_sim(" not in source or "display(HTML(" not in source or "<iframe" not in source:
        return None
    return vis_sim_replacement()


def migrate_base64_embed(source):
    if "base64.b64encode" not in source or "HTML(" not in source or "data:text/html;base64" not in source:
        return None

    path_match = re.search(r"with open\(([\"'][^\"']+[\"'])\s*,\s*[\"']r[\"']", source)
    height_match = re.search(r"height=[\"'](\d+)[\"']", source)
    width_match = re.search(r"width=[\"']([^\"']+)[\"']", source)
    if not path_match:
        return None

    path_literal = path_match.group(1)
    height = height_match.group(1) if height_match else "860"
    width = width_match.group(1) if width_match else "100%"

    return (
        "from IPython.display import IFrame\n"
        "import base64\n\n"
        f"with open({path_literal}, \"r\", encoding=\"utf-8\") as f:\n"
        "    innhold = f.read()\n\n"
        "encoded = base64.b64encode(innhold.encode(\"utf-8\")).decode(\"utf-8\")\n"
        f"IFrame(f\"data:text/html;base64,{{encoded}}\", width=\"{width}\", height={height})\n"
    )


def migrate_notebook(path):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    changed = 0

    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = source_text(cell)
        replacement = migrate_base64_embed(source)
        if replacement is None:
            replacement = migrate_vis_sim(source)
        if replacement is not None:
            set_source(cell, replacement)
            changed += 1

    if changed:
        path.write_text(
            json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
    return changed


def main():
    changed_files = 0
    changed_cells = 0
    for path in active_notebooks():
        count = migrate_notebook(path)
        if count:
            changed_files += 1
            changed_cells += count
            print(f"updated {path.relative_to(ROOT).as_posix()}: {count} embed cell(s)")
    print(f"changed {changed_files} notebook(s), {changed_cells} embed cell(s)")


if __name__ == "__main__":
    main()
