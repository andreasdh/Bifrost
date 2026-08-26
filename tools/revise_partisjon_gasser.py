import json
from pathlib import Path

path = Path('docs/4_gasser.ipynb')

with path.open(encoding='utf-8') as f:
    nb = json.load(f)


def text(cell):
    return ''.join(cell.get('source', []))


def set_text(cell, value):
    cell['source'] = value.splitlines(keepends=True)


new_step = r'''#### Trinn 5: Fra kraft til trykk

Nå går vi fra kraften på én vegg til trykket i gassen. Trykk er kraft per areal:

$$P=\frac{F}{A}$$

Fra trinn 3 har vi

$$F=\frac{NmA}{V}\langle v_x^2\rangle$$

Når vi deler på veggens areal $A$, får vi derfor direkte

$$P=\frac{Nm}{V}\langle v_x^2\rangle$$

Fra trinn 4 vet vi at

$$\langle v_x^2\rangle=\frac13\langle v^2\rangle$$

og dermed

$$PV=\frac13Nm\langle v^2\rangle$$

Dette er et rent mekanisk resultat. Vi har ennå ikke brukt temperaturbegrepet.

Den gjennomsnittlige translasjonsenergien til ett molekyl er

$$\langle E_\mathrm{trans}\rangle=\frac12m\langle v^2\rangle$$

Dermed kan vi skrive

$$PV=\frac23N\langle E_\mathrm{trans}\rangle$$

Trykket bestemmes altså av hvor mange partikler vi har per volum, og hvor stor translasjonsenergi de i gjennomsnitt har.

'''

found = False
for cell in nb['cells']:
    s = text(cell)
    if '#### Trinn 5: Fra kraft til trykk' in s and '#### Trinn 6: Temperaturen kobles på' in s:
        start = s.index('#### Trinn 5: Fra kraft til trykk')
        end = s.index('#### Trinn 6: Temperaturen kobles på', start)
        set_text(cell, s[:start] + new_step + s[end:])
        found = True
        break

if not found:
    raise RuntimeError('Fant ikke trinn 5 i trykkutledningen')

with path.open('w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
    f.write('\n')

print('Rettet overgangen fra kraft til trykk.')
