import json
from pathlib import Path

PART = Path('docs/3_partisjonsfunksjonen.ipynb')
GAS = Path('docs/4_gasser.ipynb')


def text(cell):
    return ''.join(cell.get('source', []))


def set_text(cell, value):
    cell['source'] = value.splitlines(keepends=True)


def load(path):
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def save(path, nb):
    with path.open('w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        f.write('\n')


def replace_once(value, old, new, label):
    if old not in value:
        raise RuntimeError(f'Fant ikke teksten som skulle erstattes: {label}')
    return value.replace(old, new, 1)


# Kapittel 3: partisjonsfunksjonen
nb = load(PART)

for cell in nb['cells']:
    s = text(cell)
    if s.startswith('# Partisjonsfunksjonen og molekylær energi'):
        s = s.replace('- forklare Gibbs-entropien for en generell sannsynlighetsfordeling\n', '')
        s = s.replace('- vise at Gibbs-entropien gir $S=k_\\mathrm{B}\\ln\\Omega$ når mikrotilstandene er like sannsynlige\n', '')
        anchor = '- sette opp og beregne partisjonsfunksjonen for enkle systemer med bestemte energinivåer\n'
        addition = (
            '- forklare forskjellen mellom partisjonsfunksjonen $Q$ for et helt system og den molekylære partisjonsfunksjonen $q$\n'
            '- forklare hvorfor uavhengige energibidrag gjør at en molekylær partisjonsfunksjon kan faktoriseres\n'
            '- forklare betydningen av skjelnbare og ikke-skjelnbare partikler i opptellingen av mikrotilstander\n'
        )
        if addition.splitlines()[0] not in s:
            s = replace_once(s, anchor, anchor + addition, 'nye læringsmål')
        set_text(cell, s)
        break
else:
    raise RuntimeError('Fant ikke innledningscellen i partisjonskapitlet')

ensemble_text = r'''### Det kanoniske ensemblet

Vi har nå sett at Boltzmann-fordelingen beskriver hvordan sannsynligheten fordeles mellom mikrotilstander med ulik energi ved termisk likevekt. For å bruke denne beskrivelsen på et fysisk system må vi også være tydelige på **hvilke makroskopiske betingelser systemet har**. Det er her ensemblebegrepet kommer inn.

:::{admonition} Statistisk ensemble
:class: important

Et **statistisk ensemble** er en tenkt samling av mange identiske kopier av det samme systemet. Kopiene har de samme makroskopiske betingelsene, men kan befinne seg i ulike mikrotilstander.

Ensemblet er et tanke- og regneverktøy. Vi lager ikke fysisk mange kopier av systemet; kopiene hjelper oss å tolke sannsynligheter og gjennomsnittsverdier.

:::

Valget av ensemble bestemmes av hvilke størrelser som holdes konstante, og hvilke som kan variere. Du kan lese mer om ulike ensembler i [grunnleggende begreper](A1_grunnleggende_begreper.html#ensembler).

Når $N$, $V$ og $T$ er faste, mens systemet kan utveksle energi med et varmereservoar, bruker vi det **kanoniske ensemblet**. For å regne på systemet kan vi altså forestille oss mange kopier med samme $N$, $V$ og $T$, men med ulike øyeblikkelige energier. Hvis 20 prosent av kopiene befinner seg i mikrotilstand $i$, tolker vi dette som at sannsynligheten for mikrotilstanden er $p_i=0{,}20$.

:::{admonition} Fra isolert til kanonisk
:class: note

I et isolert system er $N$, $V$ og den totale energien faste. Dette kalles det **mikrokanoniske ensemblet**.

I det **kanoniske ensemblet** er $N$, $V$ og $T$ faste, mens energien kan variere fordi systemet kan utveksle energi med et varmereservoar.

Det er denne situasjonen vi bruker når vi arbeider med Boltzmann-fordelingen i dette kapitlet.

:::

Systemet vi lager de tenkte kopiene av, trenger ikke være en hel makroskopisk prøve. Vi kan også velge **ett enkelt molekyl** som system. Kopiene representerer da det samme molekylet i ulike translasjonelle, rotasjonelle, vibrasjonelle eller elektroniske tilstander. Litt senere skal vi bruke dette til å definere den **molekylære partisjonsfunksjonen** $q$.

:::{admonition} Underveisoppgave
:class: tip

En lukket gassbeholder med fast volum står i et stort vannbad med konstant temperatur.

1. Hvilke av størrelsene $N$, $V$ og $T$ holdes faste?
2. Kan energien til systemet variere?
3. Hvorfor kan energien variere selv om temperaturen er konstant?
4. Hvilket ensemble beskriver denne situasjonen?

:::

:::{admonition} Løsningsforslag
:class: tip dropdown

$N$, $V$ og $T$ holdes faste. Systemet kan utveksle energi med vannbadet og derfor skifte mellom mikrotilstander med forskjellig energi. Temperaturen er stabil fordi vannbadet er mye større enn systemet. Situasjonen beskrives av det kanoniske ensemblet.

:::
'''

found = False
for cell in nb['cells']:
    if cell.get('cell_type') == 'markdown' and '### Det kanoniske ensemblet' in text(cell):
        set_text(cell, ensemble_text)
        found = True
        break
if not found:
    raise RuntimeError('Fant ikke ensembleavsnittet')

new_cells = []
removed_sim = False
for cell in nb['cells']:
    s = text(cell)
    if cell.get('id') == 'ensemble_simulering':
        removed_sim = True
        continue
    if 'Hver rute i simuleringen representerer én kopi av det samme systemet.' in s:
        continue
    new_cells.append(cell)
nb['cells'] = new_cells
if not removed_sim:
    raise RuntimeError('Fant ikke ensemblesimuleringen som skulle fjernes')

partition_text = r'''## Partisjonsfunksjonen

For å finne sannsynlighetene må vi først summere Boltzmann-vektene til alle mikrotilstandene. Denne summen kalles **partisjonsfunksjonen**.

:::{admonition} Kanonisk partisjonsfunksjon
:class: important

$$Q=\sum_i e^{-E_i/k_\mathrm{B}T}$$

Sannsynligheten for mikrotilstand $i$ er

$$p_i=\frac{e^{-E_i/k_\mathrm{B}T}}{Q}$$

:::

Boltzmann-vektene $e^{-E_i/k_\mathrm{B}T}$ summerer ikke nødvendigvis til 1. Derfor er de ikke sannsynligheter ennå. Når vi deler hver vekt på summen $Q$, får vi sannsynligheter som til sammen er lik 1.

Partisjonsfunksjonen er altså ikke selv en sannsynlighet. Den er heller ikke generelt et bokstavelig antall mikrotilstander.

:::{admonition} Hvilket system gjelder $Q$ for?
:class: note

Energiene $E_i$ og partisjonsfunksjonen $Q$ må beskrive det samme systemet. Hvis $E_i$ er energiene til ett molekyl, gjelder sannsynlighetene og gjennomsnittsenergien dette molekylet. Hvis $E_i$ er energiene til hele prøven, gjelder $Q$, $U$ og $S$ for hele prøven.

:::

## Den molekylære partisjonsfunksjonen

For molekyler er det ofte nyttig å starte med ett enkelt molekyl. Vi bruker da symbolet $\varepsilon_i$ for energien til molekylets mikrotilstand $i$, og skriver partisjonsfunksjonen med liten bokstav $q$.

:::{admonition} Molekylær partisjonsfunksjon
:class: important

Den **molekylære partisjonsfunksjonen** er partisjonsfunksjonen for ett molekyl:

$$q=\sum_i e^{-\varepsilon_i/k_\mathrm{B}T}$$

Summen går over de tilgjengelige mikrotilstandene til molekylet.

:::

Energien til et molekyl kan bestå av flere bidrag. Når vi kan behandle disse bidragene som uavhengige, kan vi skrive

$$\varepsilon=\varepsilon_\mathrm{trans}+\varepsilon_\mathrm{rot}+\varepsilon_\mathrm{vib}+\varepsilon_\mathrm{elec}$$

Da faktoriserer også Boltzmann-faktoren:

$$e^{-\varepsilon/k_\mathrm{B}T}
=e^{-\varepsilon_\mathrm{trans}/k_\mathrm{B}T}
 e^{-\varepsilon_\mathrm{rot}/k_\mathrm{B}T}
 e^{-\varepsilon_\mathrm{vib}/k_\mathrm{B}T}
 e^{-\varepsilon_\mathrm{elec}/k_\mathrm{B}T}$$

Dermed kan den molekylære partisjonsfunksjonen skrives som et produkt

$$q=q_\mathrm{trans}\,q_\mathrm{rot}\,q_\mathrm{vib}\,q_\mathrm{elec}$$

Dette er nyttig fordi vi kan undersøke de ulike energiformene hver for seg og deretter sette bidragene sammen.

## Fra ett molekyl til $N$ molekyler

La oss nå gå fra ett molekyl til en prøve med $N$ molekyler. Vi antar først at molekylene ikke vekselvirker, slik at energien til hele systemet er summen av energiene til de enkelte molekylene:

$$E_i=\varepsilon_{i_1}+\varepsilon_{i_2}+\cdots+\varepsilon_{i_N}$$

Hvis de $N$ delsystemene kan **skilles fra hverandre**, faktoriserer også partisjonsfunksjonen:

$$Q=q^N$$

For identiske molekyler i en gass må vi imidlertid være litt mer forsiktige med opptellingen.

:::{admonition} Skjelnbare og ikke-skjelnbare partikler
:class: important

Partikler er **skjelnbare** dersom vi i modellen kan holde rede på hvilken partikkel som er hvilken. Da gir en ombytting av to partikler en ny mikrotilstand.

Identiske molekyler i en gass behandles derimot som **ikke-skjelnbare**: En ren ombytting av to identiske molekyler representerer ikke en ny fysisk tilstand.

:::

Uttrykket $q^N$ teller alle ombyttinger som om de var forskjellige. For $N$ identiske molekyler finnes det $N!$ slike permutasjoner, og vi ville derfor overtelle mikrotilstandene med en faktor $N!$. For en klassisk, fortynnet gass av identiske molekyler uten vekselvirkninger får vi derfor

$$Q=\frac{q^N}{N!}$$

Faktoren $N!$ er altså ikke et ekstra energibidrag. Den korrigerer selve **opptellingen av mikrotilstander** når molekylene er identiske.
'''

found = False
for cell in nb['cells']:
    s = text(cell)
    if cell.get('cell_type') == 'markdown' and s.startswith('## Partisjonsfunksjonen\n'):
        marker = ':::{admonition} Underveisoppgave\n'
        if marker not in s:
            raise RuntimeError('Fant ikke underveisoppgaven etter partisjonsfunksjonen')
        tail = s[s.index(marker):]
        set_text(cell, partition_text + '\n' + tail)
        found = True
        break
if not found:
    raise RuntimeError('Fant ikke partisjonsfunksjonscellen')

for cell in nb['cells']:
    s = text(cell)
    if 'RL: er det ikke når' in s:
        lines = [line for line in s.splitlines(keepends=True) if not line.lstrip().startswith('**RL:')]
        s = ''.join(lines)
        target = '$$3e^{-\\Delta\\varepsilon/k_\\mathrm{B}T}=1$$\n'
        explanation = (
            'Lik sannsynlighet betyr mer eksplisitt at den **samlede** sannsynligheten for det eksiterte nivået er lik sannsynligheten for grunntilstanden:\n\n'
            '$$\\frac{3e^{-\\Delta\\varepsilon/k_\\mathrm{B}T}}{Q}=\\frac{1}{Q}$$\n\n'
            'Partisjonsfunksjonen $Q$ står på begge sider og kansellerer. Derfor er betingelsen ganske enkelt\n\n'
        )
        s = replace_once(s, target, explanation + target, 'kansellering av Q i degenerasjonseksemplet')
        set_text(cell, s)
        break

for cell in nb['cells']:
    s = text(cell)
    changed = False
    if 'For lineære diatomære molekyler:' in s:
        s = s.replace('For lineære diatomære molekyler:', 'For lineære molekyler:')
        changed = True
    if 'For ikke-lineære diatomære molekyler:' in s:
        s = s.replace('For ikke-lineære diatomære molekyler:', 'For ikke-lineære molekyler:')
        changed = True
    if changed:
        set_text(cell, s)

save(PART, nb)

# Kapittel 4: gasser
nb = load(GAS)

for cell in nb['cells']:
    s = text(cell)
    changed = False
    old = ('I en fortynnet gass er avstanden mellom molekylene stor sammenliknet med størrelsen deres. '
           'Derfor beveger de seg tilfeldig og mesteparten av tiden tilnærmet uavhengig av hverandre. '
           'Dermed er oppførselen fullstendig stokastisk. Dette gjør gasser langt enklere å beskrive enn '
           'væsker og faste stoffer, der partiklene hele tiden påvirker hverandre.')
    new = ('I en fortynnet gass er avstanden mellom molekylene stor sammenliknet med størrelsen deres. '
           'Mellom kollisjonene beveger molekylene seg derfor tilnærmet uavhengig av hverandre, mens de mange '
           'kollisjonene gjør at retning og fart for det enkelte molekylet stadig endres. Det er derfor mest '
           'hensiktsmessig å beskrive gassen statistisk. Dette gjør gasser langt enklere å beskrive enn væsker '
           'og faste stoffer, der partiklene hele tiden påvirker hverandre.')
    if old in s:
        s = s.replace(old, new)
        changed = True
    old2 = ('Det er enda et eksempel på **likevekt** hvordan voldsom aktivitet på mikronivå kan gi stabile '
            'egenskaper på makronivå.')
    new2 = ('Dette er et godt eksempel på **dynamisk likevekt**: Det skjer hele tiden endringer på mikronivå, '
            'samtidig som fordelingen og de makroskopiske egenskapene er stabile.')
    if old2 in s:
        s = s.replace(old2, new2)
        changed = True
    if changed:
        set_text(cell, s)

new_middle = r'''#### Trinn 2: Hvor mange molekyler når veggen i løpet av $\Delta t$?

I en virkelig gass kolliderer molekylene også med hverandre. Vi bør derfor ikke basere utledningen på at **det samme molekylet** nødvendigvis går helt til motsatt vegg og tilbake. I stedet teller vi hvor mange molekyler som kan nå veggen i løpet av et kort tidsintervall $\Delta t$.

:::{admonition} Middelfri vei
:class: note

Den **middelfrie veien**, ofte skrevet $\lambda$, er den gjennomsnittlige avstanden et molekyl beveger seg mellom to kollisjoner med andre molekyler. I en vanlig gass kan $\lambda$ være mye mindre enn avstanden mellom veggene i beholderen. Derfor er det mer generelt å telle strømmen av molekyler mot veggen enn å følge ett bestemt molekyl fra vegg til vegg.

:::

Tenk på et molekyl som beveger seg mot veggen med en positiv hastighetskomponent $v_x$. I løpet av tiden $\Delta t$ rekker det avstanden

$$v_x\Delta t$$

langs $x$-retningen. Bare molekyler som ved starten av tidsintervallet befinner seg i et tynt lag med denne tykkelsen, kan derfor nå veggen. Veggen har areal $A$, så laget har volum

$$\Delta V=A v_x\Delta t$$

og utgjør brøkdelen

$$\frac{\Delta V}{V}=\frac{A v_x\Delta t}{V}$$

av hele gassvolumet. Dette gir oss sannsynligheten for at et molekyl med denne $v_x$ befinner seg nær nok veggen til å treffe den i løpet av $\Delta t$.

#### Trinn 3: Fra antall støt til kraft

Fra trinn 1 vet vi at et molekyl som treffer veggen, overfører bevegelsesmengden $2mv_x$. For molekyl $i$ med $v_{x,i}>0$ blir det forventede bidraget til bevegelsesmengden i løpet av $\Delta t$ derfor

$$2mv_{x,i}\frac{A v_{x,i}\Delta t}{V}$$

Når vi summerer over alle molekylene som beveger seg mot veggen, får vi

$$\Delta p_\mathrm{vegg}=\frac{2mA\Delta t}{V}\sum_{v_{x,i}>0}v_{x,i}^2$$

Ved likevekt er bevegelsen isotrop: positive og negative $v_x$ forekommer symmetrisk. Siden vi summerer $v_x^2$, gir de to retningene like store bidrag. Dermed kan vi skrive

$$2\sum_{v_{x,i}>0}v_{x,i}^2=\sum_{i=1}^{N}v_{x,i}^2$$

og kraften på veggen blir

$$F=\frac{\Delta p_\mathrm{vegg}}{\Delta t}
=\frac{mA}{V}\sum_{i=1}^{N}v_{x,i}^2$$

Vi innfører nå gjennomsnittet

$$\langle v_x^2\rangle=\frac{1}{N}\sum_{i=1}^{N}v_{x,i}^2$$

og får dermed

$$F=\frac{NmA}{V}\langle v_x^2\rangle$$

Her ser vi hvorfor hastighetskomponenten kommer inn i andre potens: Molekyler med stor $v_x$ overfører mer bevegelsesmengde i hvert støt **og** kan nå veggen fra et større volum i løpet av samme tidsintervall.

'''

found = False
for cell in nb['cells']:
    s = text(cell)
    if cell.get('cell_type') == 'markdown' and '#### Trinn 2: Hvor ofte skjer støtene?' in s:
        start = s.index('#### Trinn 2: Hvor ofte skjer støtene?')
        end = s.index('#### Trinn 5: Fra $v_x$ til den totale farten $v$')
        prefix = s[:start]
        suffix = s[end:]
        prefix = prefix.replace(
            'Vi ser på en rektangulær boks med lengde $a$ langs $x$-aksen, der veggen vi studerer har areal $A$. Volumet til boksen er da $V=Aa$. Boksen inneholder $N$ molekyler, hvert med masse $m$.',
            'Vi ser på en beholder med volum $V$. Veggen vi studerer har areal $A$, og beholderen inneholder $N$ molekyler, hvert med masse $m$.'
        )
        suffix = suffix.replace('#### Trinn 5: Fra $v_x$ til den totale farten $v$', '#### Trinn 4: Fra $v_x$ til den totale farten $v$', 1)
        suffix = suffix.replace('#### Trinn 6: Fra kraft til trykk', '#### Trinn 5: Fra kraft til trykk', 1)
        suffix = suffix.replace('#### Trinn 7: Temperaturen kobles på', '#### Trinn 6: Temperaturen kobles på', 1)
        set_text(cell, prefix + new_middle + suffix)
        found = True
        break
if not found:
    raise RuntimeError('Fant ikke trykkutledningen i gasskapitlet')

inserted = False
for i, cell in enumerate(nb['cells']):
    s = text(cell)
    if cell.get('cell_type') == 'code' and 'Simulering2_trykk_energi_entropi_3D.html' in s:
        note = {
            'cell_type': 'markdown',
            'metadata': {},
            'source': (
                ':::{admonition} Om simuleringen\n'
                ':class: note\n\n'
                'Simuleringen nedenfor bruker en bevisst forenklet, kollisjonsfri modell der molekylene beveger seg ballistisk mellom veggene. I denne modellen kan ett molekyl følges fram og tilbake over boksen, slik at tiden $2a/|v_x|$ kan brukes som en illustrasjon.\n\n'
                'I en virkelig gass kolliderer molekylene også med hverandre, og den middelfrie veien kan være mye kortere enn avstanden mellom veggene. **Den generelle trykkutledningen ovenfor bygger derfor på strømmen av molekyler mot veggen, ikke på at ett bestemt molekyl går fra vegg til vegg.** Bruk simuleringen først og fremst til å utforske bevegelsesmengdeoverføring, statistiske gjennomsnitt og hvordan et stabilt trykk vokser fram fra mange støt.\n\n'
                ':::\n'
            ).splitlines(keepends=True)
        }
        nb['cells'].insert(i, note)
        inserted = True
        break
if not inserted:
    raise RuntimeError('Fant ikke trykksimuleringen for å legge inn modellpresisering')

new_task4 = r'''### Oppgave 4 – Fra molekylære støt til trykk

En beholder med volum $V$ inneholder $N$ molekyler med masse $m$. Vi studerer en vegg med areal $A$ og et kort tidsintervall $\Delta t$.

a) Et molekyl beveger seg mot veggen med hastighetskomponenten $v_x>0$. Forklar hvorfor det bare kan nå veggen i løpet av $\Delta t$ dersom det i utgangspunktet befinner seg innenfor avstanden $v_x\Delta t$ fra veggen.

b) Vis at dette laget har volum $A v_x\Delta t$, og at det utgjør brøkdelen

$$\frac{A v_x\Delta t}{V}$$

av hele volumet.

c) Ved et elastisk støt overfører molekylet bevegelsesmengden $2mv_x$ til veggen. Forklar kvalitativt hvorfor bidraget fra molekyler med en bestemt $v_x$ derfor blir proporsjonalt med $v_x^2$.

d) Ved å summere over molekylene og bruke symmetrien mellom positive og negative $v_x$, får vi

$$F=\frac{NmA}{V}\langle v_x^2\rangle$$

Bruk dette til å vise at

$$P=\frac{Nm}{V}\langle v_x^2\rangle$$

og deretter

$$P=\frac{Nm}{3V}\langle v^2\rangle$$

for en isotrop gass.

e) Bruk $\frac12m\langle v^2\rangle=\frac32k_\mathrm{B}T$ til å vise at $PV=Nk_\mathrm{B}T$.

:::{dropdown} Løsningsforslag

a) I løpet av tiden $\Delta t$ forflytter molekylet seg maksimalt $v_x\Delta t$ i retning mot veggen. Molekyler som starter lenger unna, rekker derfor ikke fram i dette tidsintervallet.

b) Laget har grunnflate $A$ og tykkelse $v_x\Delta t$, så

$$\Delta V=A v_x\Delta t$$

og volumfraksjonen er $\Delta V/V=A v_x\Delta t/V$.

c) Bevegelsesmengden per støt er proporsjonal med $v_x$. Samtidig er tykkelsen på laget som kan nå veggen i løpet av $\Delta t$, og dermed forventet antall treff, også proporsjonal med $v_x$. Produktet blir derfor proporsjonalt med $v_x^2$.

d) Trykk er kraft per areal:

$$P=\frac{F}{A}=\frac{Nm}{V}\langle v_x^2\rangle$$

I en isotrop gass er

$$\langle v_x^2\rangle=\frac13\langle v^2\rangle$$

slik at

$$P=\frac{Nm}{3V}\langle v^2\rangle$$

e) Fra temperatur–energi-sammenhengen får vi

$$m\langle v^2\rangle=3k_\mathrm{B}T$$

og dermed

$$P=\frac{N}{3V}\,3k_\mathrm{B}T=\frac{Nk_\mathrm{B}T}{V}$$

altså

$$PV=Nk_\mathrm{B}T$$

:::


'''

found = False
for cell in nb['cells']:
    s = text(cell)
    if '### Oppgave 4 – Fra molekylære støt til trykk' in s and '### Oppgave 5' in s:
        start = s.index('### Oppgave 4 – Fra molekylære støt til trykk')
        end = s.index('### Oppgave 5', start)
        set_text(cell, s[:start] + new_task4 + s[end:])
        found = True
        break
if not found:
    raise RuntimeError('Fant ikke Oppgave 4-blokken i gasskapitlet')

save(GAS, nb)
print('Reviderte kapittel 3 og 4 konservativt.')
