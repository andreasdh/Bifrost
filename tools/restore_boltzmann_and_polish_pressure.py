import json
from pathlib import Path

PART = Path('docs/3_partisjonsfunksjonen.ipynb')
GAS = Path('docs/4_gasser.ipynb')


def load(path):
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def save(path, nb):
    with path.open('w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        f.write('\n')


def text(cell):
    return ''.join(cell.get('source', []))


def set_text(cell, value):
    cell['source'] = value.splitlines(keepends=True)


# Restore the pre-existing Boltzmann section that shares a markdown cell with
# the rewritten canonical-ensemble section.
nb = load(PART)
restored = r'''(nar-gjelder-boltzmann-fordelingen)=
## Når gjelder Boltzmann-fordelingen?

Boltzmann-fordelingen beskriver et system som er i termisk likevekt med omgivelsene. Systemet kan ta opp og avgi energi, men omgivelsene er så store at temperaturen deres praktisk talt ikke endres. Slike omgivelser kalles et **varmereservoar**.

Vi bruker følgende modell:

- partikkeltallet $N$ er fast
- volumet $V$ er fast
- temperaturen $T$ er fast
- energien $E_i$ kan variere når systemet skifter mikrotilstand

Ved termisk likevekt er sannsynligheten for mikrotilstand $i$ gitt av Boltzmann-fordelingen:

$$p_i=\frac{e^{-E_i/k_\mathrm{B}T}}{Q}$$

Systemets energi varierer fra mikrotilstand til mikrotilstand. Gjennomsnittsenergien er likevel stabil

$$U=\langle E\rangle$$

:::{admonition} Hva betyr $\langle E\rangle$?
:class: note

De spisse parentesene betyr at vi tar gjennomsnittet, eller forventningsverdien, av energien. Du kan lese mer om dette i [6.2 Forventningsverdi](matematikk/statistikk.html#forventningsverdi).

:::

'''

found = False
for cell in nb['cells']:
    s = text(cell)
    if s.startswith('### Det kanoniske ensemblet'):
        set_text(cell, restored + s)
        found = True
        break
if not found:
    raise RuntimeError('Fant ikke ensemblecellen som skulle få Boltzmann-avsnittet tilbake')
save(PART, nb)

# Final small pedagogical/technical polish of the new pressure derivation.
nb = load(GAS)

old_intro = ('Før vi begynner, er det nyttig å vite hva vi prøver å gjøre. Vi skal først finne hvor stor '
             '*gjennomsnittlig kraft* ett molekyl utøver på en vegg når det kolliderer med den igjen og igjen. '
             'Deretter summerer vi bidragene fra alle molekylene. Til slutt kobler vi molekylenes bevegelse til temperatur.')
new_intro = ('Før vi begynner, er det nyttig å vite hva vi prøver å gjøre. Vi skal først finne hvor mye '
             'bevegelsesmengde ett molekyl overfører i ett støt. Deretter teller vi hvor mange molekyler som kan '
             'nå veggen i løpet av et kort tidsintervall og summerer bidragene deres. Til slutt kobler vi '
             'molekylenes bevegelse til temperatur.')

old_fraction = ('av hele gassvolumet. Dette gir oss sannsynligheten for at et molekyl med denne $v_x$ befinner '
                'seg nær nok veggen til å treffe den i løpet av $\\Delta t$.')
new_fraction = ('av hele gassvolumet. Ved likevekt er molekylene jevnt fordelt i volumet. Den samme brøkdelen '
                'angir derfor sannsynligheten for at et molekyl med denne $v_x$ befinner seg nær nok veggen til '
                'å treffe den i løpet av $\\Delta t$.')

old_symmetry = ('Ved likevekt er bevegelsen isotrop: positive og negative $v_x$ forekommer symmetrisk. Siden vi '
                'summerer $v_x^2$, gir de to retningene like store bidrag. Dermed kan vi skrive')
new_symmetry = ('Ved likevekt er bevegelsen isotrop: positive og negative $v_x$ forekommer symmetrisk. Siden vi '
                'summerer $v_x^2$, gir de to retningene like store bidrag i gjennomsnitt. For et makroskopisk '
                'antall molekyler kan vi derfor skrive')

replacements = [(old_intro, new_intro), (old_fraction, new_fraction), (old_symmetry, new_symmetry)]
seen = [False, False, False]
for cell in nb['cells']:
    s = text(cell)
    changed = False
    for i, (old, new) in enumerate(replacements):
        if old in s:
            s = s.replace(old, new, 1)
            seen[i] = True
            changed = True
    if changed:
        set_text(cell, s)

if not all(seen):
    raise RuntimeError(f'Manglet forventet gass-tekst: {seen}')

save(GAS, nb)
print('Restored Boltzmann section and polished pressure derivation.')
