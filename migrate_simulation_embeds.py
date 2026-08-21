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
        m = re.match(r"\s*-\s+file:\s+(.+?)\s*$", raw)
        if not m:
            continue
        stem = m.group(1).strip().strip("'\"")
        p = ROOT / f"{stem}.ipynb"
        if p.exists():
            paths.append(p)
    return paths

def source_text(cell):
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else src

def set_source(cell, text):
    cell["source"] = text.splitlines(keepends=True)

def vis_sim_replacement():
    return "\n".join([
        "from IPython.display import display, IFrame",
        "import html",
        "",
        'def vis_sim(sti, width="100%"):','
        '    with open(sti, "r", encoding="utf-8") as f:',
        "        innhold = f.read()",
        "    escaped = html.escape(innhold, quote=True)",
        "    display(IFrame(",
        '        "about:blank",',
        "        width=width,",
        "        height=200,",
        "        extras=[",
        '            f\'srcdoc="{escaped}"\',',
        '            \'scrolling="no"\',',
        '            \'style="border:none;display:block;"\',',
        '            \'onload="this.style.height=this.contentWindow.document.body.scrollHeight+\\\'px\\\'"\',',
        "        ],",
        "    ))",
        "",
    ])

def migrate_vis_sim(src):
    if "def vis_sim(" not in src or "display(HTML(" not in src or "<iframe" not in src:
        return None
    return vis_sim_replacement()

def migrate_base64_embed(src):
    if "base64.b64encode" not in src or "HTML(" not in src or "data:text/html;base64" not in src:
        return None
    path_match = re.search(r"with open\(([\"'][^\"']+[\"'])\s*,\s*[\"']r[\"']", src)
    height_match = re.search(r"height=[\"'](\d+)[\"']", src)
    width_match = re.search(r"width=[\"']([^\"']+)[\"']", src)
    if not path_match:
        return None
    path_literal = path_match.group(1)
    height = height_match.group(1) if height_match else "860"
    width = width_match.group(1) if width_match else "100%"
    return "\n".join([
        "from IPython.display import IFrame",
        "import base64",
        "",
        f'with open({path_literal}, "r", encoding="utf-8") as f:',
        "    innhold = f.read()",
        "",
        'encoded = base64.b64encode(innhold.encode("utf-8")).decode("utf-8")',
        f'IFrame(f"data:text/html;base64,{{encoded}}", width="{width}", height={height})',
        "",
    ])

def migrate_notebook(path):
    nb = json.loads(path.read_text(encoding="utf-8"))
    changed = 0
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = source_text(cell)
        repl = migrate_base64_embed(src)
        if repl is None:
            repl = migrate_vis_sim(src)
        if repl is not None:
            set_source(cell, repl)
            changed += 1
    if changed:
        path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return changed

def main():
    files = 0
    cells = 0
    for p in active_notebooks():
        n = migrate_notebook(p)
        if n:
            files += 1
            cells += n
            print(f"updated {p.relative_to(ROOT).as_posix()}: {n} embed cell(s)")
    print(f"changed {files} notebook(s), {cells} embed cell(s)")

if __name__ == "__main__":
    main()
