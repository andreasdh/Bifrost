import json
from pathlib import Path

path = Path("docs/4_gasser.ipynb")
notebook = json.loads(path.read_text(encoding="utf-8"))

converted_dropdowns = 0
converted_embeds = 0

# Convert admonition-based collapsibles to native MyST dropdowns.
for cell in notebook.get("cells", []):
    if cell.get("cell_type") != "markdown":
        continue

    source = cell.get("source", [])
    text = "".join(source) if isinstance(source, list) else source

    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    changed = False
    while i < len(lines):
        line = lines[i]
        if line.startswith(":::{admonition} ") and i + 1 < len(lines):
            title = line[len(":::{admonition} "):].rstrip("\n")
            class_line = lines[i + 1].strip()
            if class_line == ":class: tip dropdown":
                out.append(f":::{{dropdown}} {title}\n")
                i += 2
                converted_dropdowns += 1
                changed = True
                continue
        out.append(line)
        i += 1

    if changed:
        cell["source"] = out

# Replace Python HTML-file embeds with static iframes so they work when
# notebooks are not executed during the deployment build.
embeds = {
    "Simuleringer/fartsfordeling.html": 720,
    "Simuleringer/MB_sim.html": 720,
    "Simuleringer/Simulering2_trykk_energi_entropi_3D.html": 780,
}

for cell in notebook.get("cells", []):
    if cell.get("cell_type") != "code":
        continue

    source = cell.get("source", [])
    text = "".join(source) if isinstance(source, list) else source

    for src, height in embeds.items():
        if src not in text:
            continue

        cell_id = cell.get("id")
        cell.clear()
        cell.update(
            {
                "cell_type": "markdown",
                "id": cell_id,
                "metadata": {},
                "source": [
                    f'<iframe src="{src}" width="100%" height="{height}" '
                    'style="border: 0;" loading="lazy"></iframe>\n'
                ],
            }
        )
        converted_embeds += 1
        break

if converted_embeds != 3:
    raise RuntimeError(f"Expected to convert 3 simulation embeds, converted {converted_embeds}")
if converted_dropdowns == 0:
    raise RuntimeError("No admonition dropdowns were converted")

path.write_text(
    json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
    encoding="utf-8",
)

print(f"Converted {converted_dropdowns} dropdowns and {converted_embeds} simulation embeds")
