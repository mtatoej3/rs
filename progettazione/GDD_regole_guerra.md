# GDD – Regole di Guerra

---

## Panoramica
- **Formato:** videogioco digitale (prototipo testato dal vivo come gioco da tavolo)
- **Giocatori:** da 3 a 6 (testato dal vivo a 3)
- **Base di partenza:** regole ispirate a Futurisiko, modificate
- **Territori:** tutti di valore uguale. La differenza la fa il giocatore con la gestione dell'economia di guerra, il piazzamento e la scelta delle truppe, e le infrastrutture.

---

## Fase 1 – Assegnazione dei territori

### 1.1 Preparazione
- Si divide il numero totale di territori della mappa per il numero di giocatori. Il risultato intero è il numero di territori che **ogni giocatore deve scegliere**.
  - Esempio: 3 giocatori → 12 territori a testa.
- Se la divisione ha un **resto**, i territori avanzati diventano **non selezionabili** e vengono piazzati in posizioni **casuali** sulla mappa (un territorio bloccato per ogni unità di resto).
  - Esempio: 42 territori, 5 giocatori → 8 territori a testa, 2 non selezionabili.
- Se la divisione è esatta, non ci sono territori non selezionabili.

> **Intento di design:** i territori non selezionabili diventano bersagli facili nelle fasi successive. I giocatori sono spinti a scegliere regioni confinanti con essi, il che aggiunge lettura degli avversari e profondità alla scelta.

### 1.2 Scelta segreta
1. Ogni giocatore sceglie **di nascosto** i suoi territori **cliccando le regioni sulla mappa**: su ogni regione scelta compare il suo segnalino, visibile solo a lui.
2. Quando tutti hanno confermato, le scelte vengono rivelate contemporaneamente.
3. I segnalini diventano le bandierine visibili a tutti.

> *Prototipo da tavolo: le liste venivano scritte su carta.*

### 1.3 Territori sicuri
- Un territorio scelto da **un solo giocatore** è suo: è un **territorio sicuro**.

### 1.4 Contestazioni
Un territorio scelto da **2 o più giocatori** è **conteso**.

**Il dado Boom**
- Dado a 6 facce: **2 facce "Boom"** (colpo a segno), 4 facce vuote.
- Probabilità di Boom per dado: 1/3.

**Numero di dadi**
- Ogni giocatore lancia tanti dadi Boom quanti sono i suoi **territori sicuri**.
- Il numero è **fisso**: si calcola una volta sola prima delle contestazioni e **non aumenta** vincendo territori contesi (per non amplificare il vantaggio di chi è già avanti).

**Risoluzione**
- Si fa **un solo lancio per ogni territorio conteso**, con tutti i contendenti che lanciano insieme, anche se sono 3 o più.
- Vince chi ottiene **più Boom**.
- **Pareggio:** rilanciano **solo i giocatori pareggiati in testa**, finché non c'è un vincitore.
  - Esempio: G1 fa 2 Boom, G2 fa 2, G3 fa 1 → rilanciano solo G1 e G2.
- **Pareggio 0 contro 0:** se nessun contendente ha dadi (tutti con 0 territori sicuri), **nessuno vince**. Il territorio finisce tra quelli liberi e tutti i contendenti lo contano come contestazione persa (1.5).
  - Il conteggio resta esatto: un territorio scelto da k giocatori lascia k−1 territori liberi altrove, più questo stesso = k territori liberi per k perdenti.

**Esempio completo (3 giocatori, 12 territori a testa)**
- G1: 8 sicuri, 4 contesi → lancia 8 dadi in ognuna delle sue 4 contestazioni.
- G2: 5 sicuri, 7 contesi → lancia 5 dadi in ognuna delle sue 7 contestazioni.
- Contestazione G1 vs G2: G1 lancia 8 dadi (media ≈ 2,7 Boom), G2 ne lancia 5 (media ≈ 1,7 Boom).
- Se G1 fa 1 Boom e G2 ne fa 2, il territorio va a G2: il vantaggio aiuta ma non garantisce la vittoria.

> **Intento di design:** chi ha "letto" meglio gli avversari nella scelta segreta ha più territori sicuri, quindi più potenza di fuoco nelle contestazioni. Viene premiato, ma la fortuna lascia spazio al ribaltamento.

### 1.5 Chi perde una contestazione: assegnazione casuale
- Chi perde una contestazione **non perde il territorio in quantità**: riceve **a caso** uno dei territori rimasti liberi (cioè non scelti da nessuno).
- Vale anche per chi ha **0 territori sicuri**: lancia 0 dadi, perde tutte le contestazioni e riceve tutti i suoi territori a caso.
- **Funziona sempre:** ogni giocatore sceglie lo stesso numero di territori e il totale delle scelte è uguale ai territori selezionabili, quindi ogni scelta "doppia" lascia per forza un territorio vuoto altrove. **Territori liberi = contestazioni perse**, sempre ed esattamente.
- **Risultato:** alla fine della Fase 1 tutti hanno **lo stesso numero di territori** (es. 3 giocatori → 12 a testa) e la mappa è **completamente occupata**, esclusi i territori non selezionabili.

> **Intento di design:** il territorio casuale è un **malus logistico e difensivo**. Chi ha letto male gli avversari ha meno territori sicuri e più territori sparsi e scollegati: per difendere anche quelli sperduti deve distribuire le truppe in modo più capillare, quindi è più esposto. Il vantaggio di chi ha giocato meglio passa dalla quantità alla **qualità della posizione**.

> *Prototipo da tavolo: nei playtest chi perdeva una contestazione perdeva il territorio e basta (squilibrio 12 contro 5–6, produzione doppia dal primo turno). Regola sostituita.*

---

## Struttura del turno di gioco
Dopo la Fase 1 inizia il primo turno. Ogni turno è composto da 2 fasi:
1. **Produzione**
2. **Movimento truppe**

Entrambe le fasi si giocano **in parallelo**: tutti i giocatori decidono contemporaneamente e di nascosto. A fine fase c'è lo **showdown**, in cui si rivelano le scelte di tutti.

---

## Fase 2 – Produzione

### 2.1 Punti Produzione (PP)
- A inizio fase ogni giocatore conta le regioni che possiede: **1 regione = 1 PP**.
- Si può spendere al massimo il numero di PP disponibili in quel turno.
- I **PP non spesi si accumulano** per i turni successivi.

> 🔓 **Porta aperta per l'economia:** la gestione dei PP (accumulo, risparmio, eventuali interessi, prestiti, scambi…) potrà essere ampliata dalla parte economica. La regola attuale è la base minima.

### 2.1b Situazione al primo turno
- Dopo la Fase 1 sui territori ci sono **solo le bandierine**, senza unità.
- Le prime unità entrano in gioco con la Produzione del primo turno, poi si passa al Movimento.

### 2.2 Unità

| Unità | Tipo | Costo |
|---|---|---|
| Carro armato | Terrestre | 1 PP |
| Cacciabombardiere | Aerea | 2 PP |
| Sottomarino | Navale | 5 PP |

*(Statistiche e regole di combattimento: da definire nelle fasi successive.)*

### 2.3 Piazzamento
- **Carri e aerei:** piazzamento libero su qualsiasi territorio proprio.
- **Sottomarino:** solo in una zona di mare adiacente a un proprio territorio costiero. Se un territorio si affaccia su più mari, si può scegliere uno qualsiasi di questi.
  - Esempio: un territorio sulla costa spagnola permette di piazzare nel Mediterraneo o nell'Atlantico.
- Nella stessa zona di mare possono stare **sottomarini di fazioni diverse**.

### 2.4 Showdown
- Quando tutti hanno confermato acquisti e piazzamenti, si rivelano le scelte.
- Segue un momento di ragionamento prima della fase di movimento.

### 2.5 Domande sulla Produzione
- ✅ **Territorio senza unità:** risolto, vedi 3.8 "La bandierina come HQ".
- ✅ **Sottomarini nemici nello stesso mare:** risolto, vedi 3.9.
- ✅ **Effetto valanga al primo turno:** risolto con l'assegnazione casuale (1.5): tutti partono con gli stessi territori e quindi gli stessi PP. Più avanti nella partita l'effetto valanga (più territori → più PP → più unità) resta e va osservato nei playtest.

---

## Fase 3 – Movimento e guerra

### 3.1 Ordini di movimento
- Ogni giocatore scrive i suoi **ordini di movimento**. Ogni ordine indica:
  - **da** quale regione si parte;
  - **verso** quale regione si va;
  - **quali unità** e **quante**.
- **Nessun obbligo di attaccare:** si possono dare solo movimenti interni, o nessun ordine.
- **Showdown simultaneo:** come nella Produzione, gli ordini si scrivono di nascosto e si rivelano tutti insieme.

### 3.2 Statistiche delle unità
| Unità | Costo | Gittata | Dadi Boom per lancio | Boom per distruggerla | Note |
|---|---|---|---|---|---|
| Carro armato | 1 PP | 1 regione | 1 | 1 | Gittata valida sia per i movimenti interni sia per gli attacchi |
| Cacciabombardiere | 2 PP | 2 regioni | 1 | 1 | Può sorvolare i mari; dà la superiorità aerea (3.7) |
| Sottomarino | 5 PP | 1 zona di mare | 2 | 2 **nello stesso lancio** | |
| Bandierina (HQ) | – | – | 2 (solo difesa) | 1 | Vedi 3.8 |

- **Sottomarino corazzato:** per distruggerlo servono **2 Boom insieme**, cioè nello stesso lancio. Un Boom isolato non lo danneggia.

> **Intento di design:** in combattimento l'aereo vale quanto un carro: il PP in più paga la gittata e l'iniziativa.

### 3.3 Movimenti interni
- Un movimento **tra regioni proprie** è di **massimo 1 spostamento** per unità.

### 3.4 Attacchi a catena (sfondamento)
- Un attacco può avere **ordini successivi**: il giocatore *ipotizza di vincere* lo scontro e indica già dove proseguire, come uno sfondamento attraverso le regioni nemiche.
- Ogni passo della catena specifica di nuovo **verso quale regione** e **con quante unità**.
  - Esempio: Argentina → Brasile (attacco). Se vinco il Brasile, ordine successivo: dal Brasile, con X unità, verso la regione seguente.
- Se uno scontro della catena viene **perso**, gli ordini successivi decadono (non ci sono più unità per eseguirli).
- **Nessun limite di passi:** la catena prosegue finché si continua a vincere.
- **Aerei nelle catene:** a ogni passo l'aereo può avanzare di **1 o 2 regioni**. Se non conquista la regione obiettivo viene **distrutto** e la sua catena si spezza in quel punto.

> **Intento di design:** una catena lunga che va a buon fine premia chi ha letto bene la mappa e le forze in campo.

### 3.5 Split e join
- **Split:** le unità di una regione possono dividersi verso più regioni confinanti, sia in attacco sia nei movimenti interni.
- **Join:** unità da **regioni diverse** possono attaccare **la stessa regione** insieme (o confluire nella stessa regione propria).
- Se l'attacco congiunto vince, le **unità sopravvissute si fondono** in un unico esercito nella regione conquistata.

### 3.6 Lo scontro
- Lo scontro è **obbligatorio fino alla fine**: non c'è ritirata. Finisce solo quando:
  - l'**attaccante perde tutte le unità** che assaltano → la regione resta al difensore;
  - oppure il **difensore perde la bandierina** → la regione passa all'attaccante.
- I lanci **non sono simultanei**: le parti lanciano **a turno**, una dopo l'altra.
- **Stessi dadi in attacco e in difesa:** ogni unità lancia gli stessi dadi Boom (3.2).
- **Scontri di terra e di mare sono separati:** carri e aerei combattono sulle regioni, i sottomarini nelle zone di mare. Carri e sottomarini non sono mai nello stesso scontro: sono ordini di attacco diversi.
- **Assegnazione dei colpi:** chi fa Boom sceglie quali unità nemiche distruggere.
  - Strategia tipica: si eliminano **prima gli aerei** (per togliere la superiorità aerea all'avversario), poi i carri.
- **La bandierina si colpisce per ultima:** finché nella regione ci sono unità difensive, i Boom dell'attaccante vanno sulle unità.

**Lo scontro è diviso in 2 step:**

**Step 1 – Esercito contro esercito**
1. Si calcola la **superiorità aerea** (3.7) e si decide chi lancia per primo.
2. Le parti lanciano a turno finché l'attaccante perde tutte le unità (scontro finito, vince il difensore) oppure il difensore perde tutte le sue unità (si passa allo step 2).
- Se nella regione c'è **solo la bandierina**, lo step 1 si salta.

**Step 2 – Assalto alla bandierina**
1. Si **ricalcola la superiorità aerea** con le unità rimaste all'attaccante.
2. Si procede come in 3.8: se l'attaccante ha ancora **almeno 1 aereo** lancia per primo; se ha perso tutti gli aerei, lancia per prima la **bandierina** con 2 dadi.
3. Le parti lanciano a turno: all'attaccante basta **1 Boom** per distruggere la bandierina e conquistare la regione.

### 3.7 Iniziativa: la superiorità aerea
- Lancia per primo chi ha **più aerei** nello scontro, che sia l'attaccante o il difensore.
- **Parità di aerei** (compreso 0 contro 0): lancia per primo il **difensore**.
- **Scontro uno contro uno:** l'iniziativa si calcola **all'inizio di ogni step** (3.6) e **non cambia durante lo step**, anche se una parte perde i suoi aerei. \*
- **Scontro con più attaccanti:** la superiorità aerea si ricalcola **a ogni giro**, duello per duello (3.9d).

> \* *Da sviluppare: possibile meccanica di ricalcolo dell'iniziativa durante lo step.*

> **Intento di design:** lanciare per primi permette di distruggere unità nemiche prima che possano rispondere. Per questo gli aerei costano il doppio di un carro (2 PP contro 1 PP): si paga l'iniziativa.

### 3.8 La bandierina come HQ
- La bandierina è l'**HQ della regione** e si difende anche quando non ci sono unità.
- **Difesa:** lancia **2 dadi Boom**; ogni Boom **distrugge 1 unità attaccante**.
- **Resistenza:** viene eliminata al **primo Boom dell'attaccante**.
- Si colpisce **solo per ultima**, nello step 2 dello scontro (3.6).
- Iniziativa (ricalcolata a inizio step 2): la bandierina non ha aerei, quindi:
  - se l'attaccante ha **almeno 1 aereo**, lancia per primo;
  - se l'attaccante **non ha aerei**, lancia per prima la bandierina.

### 3.9 Sottomarini nello stesso mare
- Sottomarini di fazioni diverse possono **coesistere** nella stessa zona di mare.
- Non sono obbligati a combattere tra loro, ma **possono attaccarsi** se un giocatore lo ordina.

### 3.9b Aerei in attacco
- In attacco l'aereo si comporta **come un carro armato**: se riceve un ordine di attacco verso una regione a 2 di distanza, ci arriva e combatte.
- Anche per lui lo scontro è **fino alla fine**: o conquista la regione, o viene abbattuto.
- Non deve rientrare in una regione amica: se vince, **resta nella regione conquistata**.

### 3.9c Sottomarini contro le coste
- Un sottomarino può attaccare una **regione costiera** che si affaccia sul suo mare **solo se ci sono truppe difensive** (carri o aerei).
- **Non può attaccare la sola bandierina** e **non può conquistare regioni**: non è un mezzo anfibio.
- Il suo attacco quindi si ferma allo **step 1** dello scontro (3.6): se distrugge tutte le unità difensive, la regione resta comunque al difensore con la sua bandierina.
- **Join:** un sottomarino può unirsi a un attacco da terra contro la stessa regione costiera.

> ❓ **Meccanica di attacco del sottomarino da definire** (da rileggere sul regolamento). Ipotesi: il sottomarino ha **un solo lancio** di dadi per attacco, e non è chiaro se la difesa possa rispondere. Vale per tutti e tre i casi: sub contro sub, sub contro costa, sub in join con un attacco di terra.

### 3.9d Risoluzione degli ordini simultanei
**Gli ordini puntano alle regioni, non ai giocatori.** Un ordine di attacco dice "conquista la regione X", non "attacca il giocatore Y". Se quando l'attacco arriva la regione è cambiata di proprietario, si combatte contro chi la possiede in quel momento.

**Rinforzi (movimenti interni).** Le unità che si spostano in una propria regione **arrivano in tempo e la difendono** anche se nello stesso turno la regione viene attaccata.
- Esempio: sposto 5 carri dal Cile all'Argentina e tu attacchi l'Argentina → i 5 carri difendono.

**Risoluzione a ondate.** Gli scontri si risolvono a passi, uguali per tutti: prima **tutti i primi passi** di tutti gli ordini, poi **tutti i secondi passi** delle catene, poi i terzi, e così via. Nessuna catena "arriva prima" delle altre.

**Attacchi incrociati.** Se A attacca la regione di B mentre B attacca quella di A, i due eserciti si scontrano ed **entrambi sono attaccanti**:
- lancia per primo chi ha **più aerei**;
- **parità di aerei:** lanciano **contemporaneamente**.
- **Chi vince prosegue:** il suo ordine resta "conquista quella regione", quindi avanza nella regione nemica e affronta la **bandierina** (step 2 dello scontro, 3.6).

**Più attaccanti sulla stessa regione.** Lo scontro si gioca come più **duelli intrecciati**, uno per ogni attaccante contro il difensore:
1. I duelli si giocano a giro, partendo dall'**attaccante con più aerei**.
2. In ogni duello lancia per primo chi ha **più aerei** tra i due (regola 3.7).
3. Il difensore lancia i suoi dadi **in ogni duello**, contro un attaccante alla volta.

Esempi con G1 difensore, G2 e G3 attaccanti (G2 ha più aerei di G3):
- **G1 ha più aerei di tutti:** G1 lancia contro G2 → G2 risponde → G1 lancia contro G3 → G3 risponde → si ricomincia.
- **G1 ha meno aerei di tutti:** G2 attacca → G1 risponde a G2 → G3 attacca → G1 risponde a G3 → si ricomincia.
- **G1 è la seconda forza aerea:** G2 attacca → G1 risponde a G2 → G1 lancia contro G3 → G3 risponde → si ricomincia. Con G2 subisce l'iniziativa, con G3 la prende.

**Divisione delle forze del difensore.** All'inizio di **ogni giro** di lanci, prima di lanciare, il difensore decide **quante unità** (e **quali**: carri e aerei) combattono contro ciascun attaccante.
- La superiorità aerea si calcola **duello per duello e giro per giro**, contando solo gli aerei assegnati a quel duello.
  - Esempio: G1 ha 2 aerei e li assegna entrambi contro G2 → contro G3 combatte con 0 aerei, quindi se G3 ha almeno 1 aereo lancia per primo.
- **Attaccanti con gli stessi aerei:** se dopo la divisione la superiorità aerea è pari tra più parti, queste lanciano **contemporaneamente**.
- Appena i livelli di superiorità aerea si differenziano, si torna all'ordine normale: precedenza a chi ha **più aerei**.

> **Intento di design:** dividere le forze **prima** del lancio è una scelta di rischio (concentrarsi su un nemico o dividersi), coerente con gli ordini nascosti. Assegnare i Boom dopo aver visto i dadi toglierebbe la decisione.

**Dopo la conquista.** Se G2 conquista la regione e a G3 restano delle truppe, queste hanno ancora l'ordine di conquistarla: parte un **nuovo scontro** G3 contro G2, con la superiorità aerea ricalcolata, fino alla fine.

### 3.10 Fine fase
- Risolti tutti gli scontri, si torna alla **Fase 2 – Produzione** del turno successivo.
- **Regioni conquistate:** danno PP **già dalla Produzione successiva**. Appena finisce la risoluzione degli scontri, il PP è già sul conto del conquistatore.

### ⚠ 3.11 Domande aperte sulla guerra
1. ✅ **Dadi per unità:** risolto, vedi 3.2 e 3.6.
2. ✅ **Ordine delle perdite e iniziativa:** risolto, vedi 3.6 e 3.7 (ricalcolo durante lo step segnato con \* da sviluppare).
3. ✅ **Catene:** nessun limite di passi; l'aereo avanza di 1 o 2 regioni per passo (3.4).
4. ✅ **Ordini simultanei:** risolto, vedi 3.9d.
   - ✅ **attacco incrociato:** parità di aerei → lancio simultaneo; chi vince prosegue e affronta la bandierina (3.9d).
   - ✅ **attaccanti con gli stessi aerei:** lancio simultaneo, con divisione delle forze del difensore (3.9d).
   - ✅ **ordine sulla mappa:** a ondate (3.9d).
5. ✅ **Aerei:** risolto, vedi 3.9b.
6. **Sottomarini:** ✅ possono attaccare altri sottomarini (3.9) e unirsi agli attacchi di terra (3.9c). ⚠ Da definire la **meccanica di attacco**: un solo lancio? La difesa (sub nemico o unità a terra) può rispondere? Da rivedere sul regolamento.
7. ✅ **Regione conquistata:** risolto, vedi 3.10.
