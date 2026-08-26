import json
from pathlib import Path

# Temporary helper used by the PR branch only.
path = Path("docs/A1_grunnleggende_begreper.ipynb")
nb = json.loads(path.read_text(encoding="utf-8"))

ensemble_idx = None
for i, cell in enumerate(nb["cells"]):
    if cell.get("cell_type") == "markdown":
        text = "".join(cell.get("source", []))
        if "## Ensembler" in text:
            ensemble_idx = i
            break

if ensemble_idx is None:
    raise RuntimeError("Fant ikke seksjonen '## Ensembler'")

ensemble_text = r'''(ensembler)=
## Ensembler

Et **statistisk ensemble** er en tenkt samling av mange identiske kopier av det samme systemet. Kopiene har de samme makroskopiske betingelsene, men kan befinne seg i ulike mikrotilstander. Ensemblet er altså et tanke- og regneverktøy: vi lager ikke fysisk mange kopier av systemet, men bruker dem til å tolke sannsynligheter og gjennomsnittsverdier.

Valget av ensemble bestemmes av hva systemet kan utveksle med omgivelsene, og hvilke størrelser som derfor holdes konstante:

- **Mikrokanonisk ensemble:** Brukes for å beskrive et isolert system med konstant energi $E$, volum $V$ og antall partikler $N$. Se for deg en lukket termos med varmt vann; ingen varme overføres fra termosen til rommet rundt, og mengden vann i termosen er konstant.

- **Kanonisk ensemble:** Brukes for å beskrive et lukket system med konstant temperatur $T$, volum $V$ og antall partikler $N$. Her kan vi tenke på en lukket vannflaske som har stått på benken over natten. Flasken kan utveksle varme med rommet, men ikke partikler. Ved termisk likevekt har den samme temperatur som omgivelsene, mens energien til systemet fortsatt kan variere fra øyeblikk til øyeblikk.

- **Makrokanonisk ensemble:** Beskriver et åpent system med konstant temperatur $T$, volum $V$ og kjemisk potensial $\mu$. Systemet kan utveksle både energi og partikler med omgivelsene. Et eksempel kan være et åpent glass vann ved romtemperatur, der vannmolekyler både kan fordampe fra og kondensere tilbake til væsken.

I dette emnet arbeider vi mest med det **kanoniske ensemblet**. Når vi sier at en mikrotilstand har en bestemt sannsynlighet, kan vi forestille oss et svært stort ensemble: sannsynligheten tilsvarer da omtrent andelen av kopiene som befinner seg i denne mikrotilstanden.

Når en størrelse holdes konstant for systemet, vises dette ofte i notasjonen. Et eksempel er varmekapasiteten ved konstant volum,

$$ C_V = \left(\frac{\partial U}{\partial T}\right)_{V,N}.$$

Her viser $V,N$ at volumet og antall partikler holdes konstant mens temperaturen endres. Du kan lese mer om slik notasjon i _Nyttige matematiske verktøy_ under [blandede partiellderiverte](matematikk/flervariabel_kalkulus.html#blandede-partiellderiverte).

### Et ensemblegjennomsnitt

Simuleringen nedenfor viser et enkelt system med fem tillatte energinivåer. Tenk deg at hver kopi i et stort kanonisk ensemble alltid befinner seg på ett av disse nivåene. Søylene viser hvor stor andel av kopiene som befinner seg på hvert nivå, mens den stiplede linjen viser gjennomsnittsenergien $U$ for hele ensemblet.

Når du flytter glideren, endrer du forholdet mellom energiforskjellen $\Delta\varepsilon$ og den termiske energiskalaen $k_\mathrm{B}T$. Du trenger ikke kunne beregne sannsynlighetene eller varmekapasiteten ennå. Her er poenget å se forskjellen mellom **energien til én bestemt kopi** og **gjennomsnittet over mange kopier**.
'''

nb["cells"][ensemble_idx]["source"] = ensemble_text.splitlines(keepends=True)

sim_code = '''from IPython.display import HTML\n\nwith open("Simuleringer/indre_energi_ensemble_gjennomsnitt.html", "r", encoding="utf-8") as f:\n    html = f.read()\n\nHTML(html)\n'''

sim_cell = {
    "cell_type": "code",
    "execution_count": None,
    "id": "ensemble-intro-sim",
    "metadata": {"tags": ["hide-input"]},
    "outputs": [],
    "source": sim_code.splitlines(keepends=True),
}

exercise_text = r''':::{admonition} Underveisoppgave
:class: tip

Bruk simuleringen til å undersøke ensemblet:

1. Gjør $\Delta\varepsilon/k_\mathrm{B}T$ stor. Hvilket energinivå befinner flest kopier seg på?
2. Gjør forholdet mindre. Hva skjer med fordelingen av kopiene mellom energinivåene?
3. Den enkelte kopien befinner seg alltid på ett av de tillatte energinivåene. Hvordan kan gjennomsnittsenergien $U$ likevel ligge mellom to energinivåer?

:::

:::{admonition} Løsningsforslag
:class: tip dropdown

Når $\Delta\varepsilon/k_\mathrm{B}T$ er stor, dominerer det laveste energinivået. Når forholdet blir mindre, fordeles ensemblet over flere energinivåer. $U$ er ikke energien til én bestemt kopi, men gjennomsnittet over hele ensemblet. Derfor kan $U$ ligge mellom de tillatte energinivåene selv om ingen enkelt kopi har akkurat denne energien.

:::

Denne tolkningen av sannsynlighet og gjennomsnittsenergi blir viktig når vi senere introduserer [Boltzmann-fordelingen og partisjonsfunksjonen](3_partisjonsfunksjonen.html).
'''

exercise_cell = {
    "cell_type": "markdown",
    "id": "ensemble-intro-exercise",
    "metadata": {},
    "source": exercise_text.splitlines(keepends=True),
}

# Avoid duplicate insertion if the helper is accidentally run twice.
existing_ids = {cell.get("id") for cell in nb["cells"]}
if "ensemble-intro-sim" not in existing_ids:
    nb["cells"].insert(ensemble_idx + 1, sim_cell)
    nb["cells"].insert(ensemble_idx + 2, exercise_cell)

path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
