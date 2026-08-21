import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CALLS = {
    "docs/matematikk/flervariabel_kalkulus.ipynb": 'vis_sim("../Simuleringer/flervariabel_flate.html")',
    "docs/matematikk/formler_og_enheter.ipynb": 'vis_sim("../Simuleringer/maxwell_boltzmann.html")',
    "docs/matematikk/kalkulus.ipynb": 'vis_sim("../Simuleringer/jevn_odde_funksjon.html")',
    "docs/matematikk/kombinatorikk.ipynb": 'vis_sim("../Simuleringer/fakultet.html")',
    "docs/matematikk/sannsynlighet.ipynb": 'vis_sim("../Simuleringer/utfallsrom_hendelser.html")',
    "docs/matematikk/statistikk.ipynb": 'vis_sim("../Simuleringer/diskret_kontinuerlig.html")',
}

for rel, call in CALLS.items():
    path = ROOT / rel
    notebook = json.loads(path.read_text(encoding="utf-8"))
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if "def vis_sim(" in source:
            if call not in source:
                source = source.rstrip() + "\n\n" + call + "\n"
                cell["source"] = source.splitlines(keepends=True)
            break
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"repaired {rel}")
