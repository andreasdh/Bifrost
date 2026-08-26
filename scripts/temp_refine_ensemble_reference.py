import json
from pathlib import Path

# Temporary helper for PR #11.
path = Path("docs/A1_grunnleggende_begreper.ipynb")
nb = json.loads(path.read_text(encoding="utf-8"))

ensemble_idx = None
for i, cell in enumerate(nb["cells"]):
    if cell.get("cell_type") == "markdown" and "## Ensembler" in "".join(cell.get("source", [])):
        ensemble_idx = i
        break

if ensemble_idx is None:
    raise RuntimeError("Fant ikke seksjonen '## Ensembler'")

ensemble_text = r'''(ensembler)=
## Ensembler

Et **statistisk ensemble** er en tenkt samling av mange identiske kopier av det samme systemet. Kopiene beskrives med de samme betingelsene, men kan befinne seg i ulike mikrotilstander. Ensemblet er et tanke- og regneverktøy som gjør det mulig å tolke sannsynligheter og gjennomsnittsverdier.

Systemet som kopieres trenger ikke være makroskopisk. Det kan for eksempel være ett enkelt molekyl, et mindre delsystem eller en hel gassprøve. Det avgjørende er hva vi har valgt å definere som **systemet**.

Valget av ensemble bestemmes av hva systemet kan utveksle med omgivelsene, og hvilke størrelser som holdes konstante:

- **Mikrokanonisk ensemble:** Et isolert system med konstant energi $E$, volum $V$ og antall partikler $N$. Systemet utveksler verken energi eller partikler med omgivelsene.

- **Kanonisk ensemble:** Et system med konstant temperatur $T$, volum $V$ og antall partikler $N$. Systemet kan utveksle energi med et varmereservoar, slik at energien kan variere selv om temperaturen er konstant.

- **Makrokanonisk ensemble:** Et system med konstant temperatur $T$, volum $V$ og kjemisk potensial $\mu$. Systemet kan utveksle både energi og partikler med et reservoar, slik at både energien og antall partikler kan variere.

Når en størrelse holdes konstant, vises dette ofte i notasjonen. Et eksempel er varmekapasiteten ved konstant volum,

$$ C_V = \left(\frac{\partial U}{\partial T}\right)_{V,N}.$$

Her viser $V,N$ at volumet og antall partikler holdes konstant mens temperaturen endres. Se også [blandede partiellderiverte](matematikk/flervariabel_kalkulus.html#blandede-partiellderiverte).

### Ensemblegjennomsnitt

I et ensemble kan de ulike kopiene befinne seg i forskjellige mikrotilstander. En gjennomsnittsverdi over ensemblet trenger derfor ikke være lik verdien i én bestemt kopi.

Simuleringen nedenfor viser et enkelt system med fem tillatte energinivåer. Hver kopi i ensemblet befinner seg på ett av nivåene. Søylene viser fordelingen av kopiene mellom energinivåene, mens den stiplede linjen viser gjennomsnittsenergien $U$ for hele ensemblet. Derfor kan $U$ ligge mellom to tillatte energinivåer selv om ingen enkelt kopi har akkurat denne energien.

Glideren endrer forholdet $\Delta\varepsilon/k_\mathrm{B}T$. Når forholdet er stort, er fordelingen konsentrert mot de laveste energinivåene. Når forholdet blir mindre, fordeles kopiene over flere nivåer.
'''

nb["cells"][ensemble_idx]["source"] = ensemble_text.splitlines(keepends=True)

# Remove the exercise/progression cell added in the earlier revision.
nb["cells"] = [cell for cell in nb["cells"] if cell.get("id") != "ensemble-intro-exercise"]

path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
