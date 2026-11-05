# GDD – Regole di Guerra

> **Versione:** 2.0 – adattamento a videogioco web multiplayer
> **Stack:** React + TypeScript · Java Spring Boot · PostgreSQL su Supabase · grafica 3D con forme geometriche semplici
> **Stato:** le regole di gioco (Parti 1–3) derivano dal prototipo da tavolo; la parte tecnica (Parti 4–14) è nuova. I punti ancora aperti sono raccolti nella Parte 15.

## Indice
- **Parte A – Game design**
  - [0. Panoramica](#0-panoramica)
  - [1. Fase 1 – Assegnazione dei territori](#1-fase-1--assegnazione-dei-territori)
  - [Struttura del turno](#struttura-del-turno-di-gioco)
  - [2. Fase 2 – Produzione](#2-fase-2--produzione)
  - [3. Fase 3 – Movimento e guerra](#3-fase-3--movimento-e-guerra)
- **Parte B – Progettazione tecnica**
  - [4. Visione tecnica e principi](#4-visione-tecnica-e-principi)
  - [5. Struttura del repository](#5-struttura-del-repository)
  - [6. Backend (Java Spring)](#6-backend-java-spring)
  - [7. Database (PostgreSQL su Supabase)](#7-database-postgresql-su-supabase)
  - [8. Frontend (React + TypeScript)](#8-frontend-react--typescript)
  - [9. Grafica 3D](#9-grafica-3d)
  - [10. Multiplayer: sincronizzazione e segretezza](#10-multiplayer-sincronizzazione-e-segretezza)
  - [11. Sicurezza e anti-cheat](#11-sicurezza-e-anti-cheat)
  - [12. Test e bilanciamento](#12-test-e-bilanciamento)
  - [13. DevOps e ambienti](#13-devops-e-ambienti)
  - [14. Roadmap di sviluppo](#14-roadmap-di-sviluppo)
- [15. Estensioni in valutazione e domande aperte](#15-estensioni-in-valutazione-e-domande-aperte)

---

# PARTE A – GAME DESIGN

## 0. Panoramica
- **Formato:** videogioco **web multiplayer online**, partite a stanze (lobby con codice). Il prototipo è stato testato dal vivo come gioco da tavolo.
- **Giocatori:** da 3 a 6 (testato dal vivo a 3). Con mappe piccole conviene 3–4 giocatori (vedi 1.8).
- **Base di partenza:** regole ispirate a Futurisiko, modificate.
- **Territori:** tutti di valore uguale. La differenza la fa il giocatore con la gestione dell'economia di guerra, il piazzamento e la scelta delle truppe, e le infrastrutture.
- **Ritmo:** fasi **simultanee e segrete** con **showdown** (rivelazione contemporanea), come nel prototipo da tavolo. Nessun turno a sequenza fissa: tutti decidono insieme, il server rivela e risolve.
- **Mappa del prototipo digitale:** 20 territori su 4 gruppi (Africa, Europa, Asia, Oceania) con confini terrestri, ponti e zone di mare (`mapa_test.jpeg`). Il motore deve funzionare con **qualsiasi mappa** descritta come dati (vedi 7.2).
- **Resa grafica:** 3D con **solo forme geometriche semplici** (Parte 9).

---

## 1. Fase 1 – Assegnazione dei territori

> **Cosa cambia in questa versione.** L'assegnazione casuale dei territori a chi perde una contestazione (vecchia 1.5) è **sostituita** da un **riposizionamento delle pedine** con vincolo di territorio libero (1.5) e da una **clausola di recupero** per chi resta a 0 territori (1.7). Il caso "0 territori" ora è gestito in modo esplicito e **si esegue una sola volta**.

### 1.1 Preparazione
- Si divide il numero totale di territori della mappa per il numero di giocatori. Il risultato intero è la **quota** `n`: il numero di pedine che **ogni giocatore deve piazzare**.
  - Esempio: 3 giocatori, 36 territori → 12 pedine a testa.
- Se la divisione ha un **resto**, i territori avanzati diventano **non selezionabili** e vengono piazzati in posizioni **casuali** sulla mappa (un territorio bloccato per ogni unità di resto). Il posizionamento usa l'RNG del server (6.6).
  - Esempio: 42 territori, 5 giocatori → 8 pedine a testa, 2 territori non selezionabili.
- Se la divisione è esatta, non ci sono territori non selezionabili.
- I territori non selezionabili **non appartengono a nessuno** per tutta la Fase 1 e non si possono scegliere, né contendere, né cedere.

> **Intento di design:** i territori non selezionabili diventano bersagli facili nelle fasi successive. I giocatori sono spinti a scegliere regioni confinanti con essi, il che aggiunge lettura degli avversari e profondità alla scelta.

### 1.2 Scelta segreta (round 1)
1. Ogni giocatore piazza di **nascosto** le sue `n` pedine **cliccando le regioni sulla mappa 3D**: su ogni regione scelta compare il suo segnalino (forma e colore del giocatore), visibile solo a lui. Può spostare i segnalini finché non conferma.
2. Quando tutti hanno confermato (o scade il timer, vedi 10.4), le scelte vengono **rivelate contemporaneamente**.
3. I segnalini diventano le bandierine visibili a tutti.

> *Prototipo da tavolo: le liste venivano scritte su carta.*

### 1.3 Territori sicuri
- Un territorio scelto da **un solo giocatore** è suo: è un **territorio sicuro**.

### 1.4 Contestazioni del round 1
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
- **Pareggio 0 contro 0:** se nessun contendente ha dadi (tutti con 0 territori sicuri), **nessuno vince**. Il territorio resta **libero** e tutti i contendenti lo contano come contestazione persa.

**Esempio completo (3 giocatori, 12 pedine a testa)**
- G1: 8 sicuri, 4 contesi → lancia 8 dadi in ognuna delle sue 4 contestazioni.
- G2: 5 sicuri, 7 contesi → lancia 5 dadi in ognuna delle sue 7 contestazioni.
- Contestazione G1 vs G2: G1 lancia 8 dadi (media ≈ 2,7 Boom), G2 ne lancia 5 (media ≈ 1,7 Boom).
- Se G1 fa 1 Boom e G2 ne fa 2, il territorio va a G2: il vantaggio aiuta ma non garantisce la vittoria.

**Chi perde una contestazione** ritira la pedina: ora ha una **pedina da riposizionare** (1.5). Non riceve alcun territorio a caso.

> **Intento di design:** chi ha "letto" meglio gli avversari nella scelta segreta ha più territori sicuri, quindi più potenza di fuoco nelle contestazioni. Viene premiato, ma la fortuna lascia spazio al ribaltamento.

### 1.5 Riposizionamento delle pedine (round 2, una sola volta)
Dopo il round 1 ogni giocatore possiede `p` territori e ha `n − p` **pedine da riposizionare** (zero per chi ha vinto o evitato ogni contestazione).

**Regole di piazzamento**
1. Ogni giocatore con pedine da riposizionare le piazza **a piacimento**, di nascosto e in simultanea, su qualsiasi territorio **selezionabile** che non sia già suo.
2. **Vincolo del territorio libero:** **almeno una** delle pedine riposizionate deve andare su un **territorio libero** (non occupato da nessuno), **se ne esiste almeno uno**. Il client e il server rifiutano la conferma se il vincolo non è rispettato.
3. Le altre pedine possono andare su territori liberi **oppure su territori occupati da altri**.

**Territori liberi contesi.** Se più giocatori puntano lo stesso territorio libero, si risolve come in 1.4 (un lancio per territorio, vince chi fa più Boom, pareggio → rilancio tra i primi).

**Territori occupati: il giocatore deve contenderseli.** Se una pedina viene piazzata su un territorio occupato, **il proprietario difende** e si risolve un lancio contro tutti gli sfidanti:
- Ogni parte lancia tanti dadi Boom quanti sono i **territori che possiede all'inizio del round 2** (numero fisso, come in 1.4). Il difensore lancia **in ogni sua difesa**.
- Vince chi ottiene **più Boom**. Pareggio → rilanciano solo i primi a pari merito.
- Se vince uno sfidante, il territorio passa a lui: il vecchio proprietario perde un territorio e **non può recuperarlo** in questo round.
- Se vince il difensore, le pedine sfidanti sono **perse** (non vengono riposizionate altrove).
- Se **più sfidanti** puntano lo stesso territorio occupato, tutti lanciano insieme al difensore.

**Esito del round 2.** Le pedine che non hanno ottenuto un territorio vengono ritirate: alcuni giocatori possono ora avere **meno** di `n` territori, altri **più** (se hanno strappato territori occupati).

> **Intento di design:** il riposizionamento trasforma lo "sfortunato" in un giocatore che può **scegliere dove ripartire**: punta su territori liberi (sicuro ma magari sperduto) o rischia contro un avversario. Il vincolo del territorio libero impedisce che tutti si accaniscano solo l'uno sull'altro e lascia sempre un'uscita.

### 1.6 Territori liberi rimasti
- Se alla fine del round 2 restano **territori liberi** e qualche giocatore ha **0 territori**, ciascuno di loro (in ordine casuale deciso dal server) **sceglie un territorio libero** tra quelli rimasti. Nessun lancio.
- I territori liberi che restano dopo questo passaggio (nessun giocatore a 0) rimangono **senza proprietario** e si comportano come i non selezionabili (bersagli neutri senza difesa; vedi 3.8).

> ⚠ *Estensione di design proposta in questa versione: lo stesso scopo della clausola 1.7 quando i territori liberi esistono ancora.*

### 1.7 Clausola di recupero: cessione per chi ha 0 territori (una sola volta)
Si attiva **solo** se, dopo 1.5 e 1.6, **non ci sono territori liberi** ma almeno un giocatore ha **0 territori**.

1. **Donatori:** tutti i giocatori con **più di un territorio** lanciano **1 dado a 6 facce (d6)** ciascuno. Il giocatore con il **valore più basso** deve **cedere un territorio** a un giocatore con 0 territori.
2. **Scelta del territorio:** è il **beneficiario** (il giocatore a 0) a scegliere **quale** territorio del donatore ricevere.
3. **Pareggio sul valore più basso:** rilanciano **solo i giocatori pareggiati**, finché non c'è un solo più basso. Il rilancio fa parte della stessa operazione.
4. **Più giocatori a 0:** i beneficiari vengono serviti in ordine casuale; il k-esimo valore più basso (dopo i rilanci per pareggio) cede al k-esimo beneficiario. **Ogni donatore cede al massimo un territorio** e non scende mai sotto 1 territorio.
5. **Una sola volta:** l'operazione è eseguita **un'unica volta** per partita, **a prescindere dal risultato**. Dopo di essa **si prosegue con il gioco**, anche se restano differenze di quota o qualcuno è ancora a 0.
6. **Giocatore ancora a 0:** se i donatori disponibili sono meno dei giocatori a 0, i giocatori rimasti senza territori sono **eliminati** (diventano spettatori). *Regola provvisoria, vedi 15.2.*
7. **Nessun donatore:** se nessun giocatore ha più di un territorio, la clausola non si applica.

> **Intento di design:** chi ha giocato peggio non viene eliminato al primo passo, ma paga un prezzo: ripartire da un solo territorio ceduto. Il donatore è scelto dal caso (il più basso) e non dal giocatore, per evitare accordi o ricatti.

### 1.8 Quanto è frequente il caso "0 territori"?
Stima Monte Carlo (100.000 simulazioni per riga, ogni giocatore sceglie `n` territori **a caso**: è un limite alto per un giocatore attento, ma utile come ordine di grandezza). Valore = probabilità che **almeno un giocatore** abbia **0 territori sicuri** dopo il round 1:

| Giocatori | Territori | `n` | Probabilità |
|---|---|---|---|
| 3 | 36 | 12 | 0,05 % |
| 3 | 20 | 6 | 4,2 % |
| 5 | 42 | 8 | 4,8 % |
| 6 | 42 | 7 | 11,9 % |
| 4 | 20 | 5 | 17,0 % |
| 6 | 20 | 3 | 71,2 % |

- Con mappe grandi e pochi giocatori il caso è raro: la clausola è una **rete di sicurezza**.
- Con la **mappa di test a 20 territori** conviene giocare in **3 (al massimo 4)**: a 6 giocatori quasi sempre qualcuno parte da 0 e il round 2 diventa la parte principale della Fase 1.
- Un giocatore a 0 territori sicuri **non** equivale a un giocatore a 0 finali: dopo il round 2 il caso diventa molto più raro.

### 1.9 Riepilogo del flusso della Fase 1
```
PREPARAZIONE ──► SCELTA SEGRETA (r.1) ──► RIVELAZIONE ──► CONTESTAZIONI (r.1)
                                                              │
         ┌────────────────────────────────────────────────────┘
         ▼
RIPOSIZIONAMENTO (r.2, vincolo "almeno 1 libero") ──► LANCI per liberi e occupati
         │
         ▼
Restano liberi e c'è chi ha 0?  ──sì──► 1.6 scelta libera per i giocatori a 0
         │no
         ▼
Non ci sono liberi e c'è chi ha 0? ──sì──► 1.7 CESSIONE (d6, una sola volta)
         │no                                         │
         └─────────────────────────┬─────────────────┘
                                   ▼
                      INIZIO TURNO 1 (Produzione)
```

> *Prototipo da tavolo: nei playtest chi perdeva una contestazione perdeva il territorio e basta (squilibrio 12 contro 5–6, produzione doppia dal primo turno). Un'assegnazione casuale ai perdenti aveva risolto lo squilibrio ma toglieva ogni scelta; il riposizionamento con la clausola di recupero la sostituisce.*

---

## Struttura del turno di gioco
Dopo la Fase 1 inizia il primo turno. Ogni turno è composto da 2 fasi:
1. **Produzione**
2. **Movimento truppe**

Entrambe le fasi si giocano **in parallelo**: tutti i giocatori decidono contemporaneamente e di nascosto. A fine fase c'è lo **showdown**, in cui si rivelano le scelte di tutti.

---

## 2. Fase 2 – Produzione

### 2.1 Punti Produzione (PP)
- A inizio fase ogni giocatore conta le regioni che possiede: **1 regione = 1 PP**.
- Si può spendere al massimo il numero di PP disponibili in quel turno.
- I **PP non spesi si accumulano** per i turni successivi.

> 🔓 **Porta aperta per l'economia:** la gestione dei PP (accumulo, risparmio, eventuali interessi, prestiti, scambi…) potrà essere ampliata dalla parte economica. La regola attuale è la base minima. Il codice la isola dietro l'interfaccia `EconomyRules` (6.5), vedi anche 15.1.

### 2.1b Situazione al primo turno
- Dopo la Fase 1 sui territori ci sono **solo le bandierine**, senza unità.
- Le prime unità entrano in gioco con la Produzione del primo turno, poi si passa al Movimento.

### 2.2 Unità

| Unità | Tipo | Costo |
|---|---|---|
| Carro armato | Terrestre | 1 PP |
| Cacciabombardiere | Aerea | 2 PP |
| Sottomarino | Navale | 5 PP |

### 2.3 Piazzamento
- **Carri e aerei:** piazzamento libero su qualsiasi territorio proprio.
- **Sottomarino:** solo in una zona di mare adiacente a un proprio territorio costiero. Se un territorio si affaccia su più mari, si può scegliere uno qualsiasi di questi.
  - Esempio: un territorio sulla costa spagnola permette di piazzare nel Mediterraneo o nell'Atlantico.
- Nella stessa zona di mare possono stare **sottomarini di fazioni diverse**.

### 2.4 Showdown
- Quando tutti hanno confermato acquisti e piazzamenti (o scade il timer), il server rivela le scelte.
- Segue un momento di ragionamento prima della fase di movimento.

### 2.5 Domande sulla Produzione
- ✅ **Territorio senza unità:** risolto, vedi 3.8 "La bandierina come HQ".
- ✅ **Sottomarini nemici nello stesso mare:** risolto, vedi 3.9.
- ⚠ **Effetto valanga al primo turno:** la Fase 1 punta a quote simili ma **non le garantisce più** (un giocatore può avere più o meno di `n` territori dopo 1.5 e 1.7). Resta da osservare nei playtest quanto pesa la differenza di PP iniziali; più avanti nella partita l'effetto valanga (più territori → più PP → più unità) resta.

---

## 3. Fase 3 – Movimento e guerra

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
  - *Implementazione:* la scelta del bersaglio è una **politica configurabile** (`TargetingPolicy`, 6.5). Nel gioco online la scelta è **automatica** (prima gli aerei, poi i carri) per non bloccare la partita con decisioni a metà scontro; una scelta manuale resta un'estensione (15.3).
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
- **Territori senza proprietario** (non selezionabili o rimasti liberi dopo la Fase 1): **non hanno bandierina**, quindi non si difendono; chi li raggiunge li conquista senza scontro. *(Da confermare nei playtest, 15.2.)*

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
- *Online:* la divisione è una **mini-fase di ordini nascosti** a inizio di ogni giro di scontro multi-attaccante, con timer breve e **divisione di default** (proporzionale) se il giocatore non risponde (10.4).

> **Intento di design:** dividere le forze **prima** del lancio è una scelta di rischio (concentrarsi su un nemico o dividersi), coerente con gli ordini nascosti. Assegnare i Boom dopo aver visto i dadi toglierebbe la decisione.

**Dopo la conquista.** Se G2 conquista la regione e a G3 restano delle truppe, queste hanno ancora l'ordine di conquistarla: parte un **nuovo scontro** G3 contro G2, con la superiorità aerea ricalcolata, fino alla fine.

### 3.10 Fine fase
- Risolti tutti gli scontri, si torna alla **Fase 2 – Produzione** del turno successivo.
- **Regioni conquistate:** danno PP **già dalla Produzione successiva**. Appena finisce la risoluzione degli scontri, il PP è già sul conto del conquistatore.

### 3.11 Condizione di vittoria
> ⚠ **Non ancora definita nel GDD.** Le simulazioni (`simulazione/VARIANTI.md`) hanno usato "dominio completo", "3 gruppi colore su 4" e "14 territori su 20"; quest'ultima dava le partite più giocabili. Il motore la tratta come regola configurabile (`VictoryCondition`, 6.5). Decisione in 15.2.

### ⚠ 3.12 Domande aperte sulla guerra
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

---

# PARTE B – PROGETTAZIONE TECNICA

## 4. Visione tecnica e principi

### 4.1 Stack
| Livello | Tecnologia | Note |
|---|---|---|
| Frontend | **React 18 + TypeScript** (Vite) | SPA, strict mode TS |
| Grafica 3D | **three.js** via **@react-three/fiber** + **@react-three/drei** | Solo geometrie primitive (Parte 9) |
| Stato client | **Zustand** (+ **TanStack Query** per le chiamate REST) | |
| UI | **Tailwind CSS** + componenti HTML sopra il canvas | |
| Backend | **Java 21 + Spring Boot 3** | Maven multi-modulo |
| Tempo reale | **WebSocket + STOMP** (Spring Messaging) | Client: `@stomp/stompjs` |
| Database | **PostgreSQL su Supabase** | Accesso solo dal backend |
| Autenticazione | **Supabase Auth** (JWT) | Il backend valida il token |
| Migrazioni DB | **Flyway** | |
| Contratto API | **springdoc-openapi** → tipi TypeScript con `openapi-typescript` | |

### 4.2 Principi guida
1. **Server autoritativo.** Tutta la logica di gioco, i dadi e le regole stanno nel backend. Il client **non calcola mai** un esito: mostra ciò che il server comunica.
2. **Motore di gioco puro e deterministico.** Il cuore delle regole è una libreria Java **senza dipendenze da Spring, DB o rete**: stessa partita + stesso seme + stessi ordini = stesso risultato. Questo permette test, replay e confronto con `sim.py`.
3. **Segretezza per costruzione.** Le scelte nascoste (pedine, acquisti, ordini) non lasciano mai il server prima dello showdown (10.2).
4. **Regole come dati e strategie.** Costi, statistiche, mappa, condizione di vittoria, economia sono configurazione o strategie sostituibili: le varianti simulate (`VARIANTI.md`) diventano profili di regole, non fork del codice.
5. **Ordine di costruzione:** prima il ciclo di gioco **in memoria, anche brutto**, poi il database, poi la rete, poi la grafica. *Non si parte dal database.*
6. **Separazione netta tra simulazione e rendering.** Il client riceve **eventi di risoluzione** ordinati e li anima: la grafica non influenza mai lo stato.

### 4.3 Architettura a colpo d'occhio
```
┌────────────────────────────── Browser ───────────────────────────────┐
│ React UI (lobby, pannelli, ordini)   R3F Scene (mappa 3D, unità, dadi)│
│        Zustand store  ◄── eventi ◄──  StompClient / REST client       │
└───────────────▲────────────────────────────────────┬─────────────────┘
        eventi  │ (WebSocket/STOMP)           comandi │ (WebSocket) / REST
┌───────────────┴────────────────────────────────────▼─────────────────┐
│ Spring Boot                                                          │
│  api  ─►  application (use case, MatchActor, timer)  ─►  engine      │
│  (REST, WS, security)        │ porte (interfacce)        (dominio    │
│                              ▼                            puro)      │
│                    infrastructure (JPA, Flyway, RNG, clock)          │
└──────────────────────────────┬───────────────────────────────────────┘
                               ▼
                  PostgreSQL (Supabase) – Auth JWT (JWKS)
```

---

## 5. Struttura del repository

Monorepo, un unico `git`:

```
rs/
├── progettazione/            # GDD, immagini di riferimento
├── simulazione/              # sim.py e risultati (oracolo di bilanciamento)
├── scarto/                   # idee scartate
├── backend/
│   ├── pom.xml               # parent (Java 21, BOM Spring Boot)
│   ├── rg-engine/            # DOMINIO PURO – nessuna dipendenza Spring/DB
│   │   └── src/main/java/it/regoleguerra/engine/
│   │       ├── model/        # Match, Player, Territory, Army, Order, ...
│   │       ├── map/          # GameMap, Adjacency, SeaZone
│   │       ├── rules/        # RuleSet, UnitCatalog, VictoryCondition, EconomyRules
│   │       ├── phase/        # state machine: SetupPhase, ProductionPhase, ...
│   │       ├── combat/       # BattleResolver, InitiativeCalculator, TargetingPolicy
│   │       ├── command/      # Command, CommandHandler, validator
│   │       ├── event/        # DomainEvent (sealed interface)
│   │       └── random/       # DiceRoller (porta), SeededDiceRoller
│   ├── rg-server/            # APPLICAZIONE SPRING
│   │   └── src/main/java/it/regoleguerra/server/
│   │       ├── api/          # REST controller, WS controller, DTO, mapper
│   │       ├── application/  # use case, MatchActor, MatchRegistry, PhaseTimer
│   │       ├── infrastructure/
│   │       │   ├── persistence/   # entity JPA, repository, adapter
│   │       │   ├── security/      # config JWT Supabase, STOMP interceptor
│   │       │   └── config/
│   │       └── RgServerApplication.java
│   │   └── src/main/resources/db/migration/   # Flyway V1__...sql
│   └── rg-sim-cli/           # (opzionale) CLI headless: partite bot-vs-bot per il bilanciamento
├── frontend/
│   ├── package.json  vite.config.ts  tsconfig.json
│   └── src/
│       ├── app/              # router, provider, layout
│       ├── api/              # client REST, tipi generati, client STOMP
│       ├── features/
│       │   ├── auth/  lobby/  setup/  production/  movement/  showdown/  endgame/
│       ├── game/
│       │   ├── store/        # Zustand: matchStore, draftStore, uiStore
│       │   ├── events/       # EventPlayer: coda e animazione degli eventi
│       │   └── domain/       # tipi e helper solo-lettura (adiacenze, validazioni UX)
│       ├── scene/            # componenti R3F (Parte 9)
│       ├── ui/               # componenti HTML riusabili
│       └── shared/           # utilità, i18n (it, en)
├── docs/                     # ADR (architecture decision records), diagrammi
└── .github/workflows/        # CI
```

**Regola di dipendenza:** `rg-server → rg-engine`, mai il contrario. Lato frontend, `scene/` dipende da `game/` ma **non viceversa**.

---

## 6. Backend (Java Spring)

### 6.1 Stile architetturale
**Architettura esagonale (porte e adattatori)** dentro un **monolite modulare**:
- `engine` = dominio, nessuna dipendenza esterna;
- `application` = casi d'uso e orchestrazione; definisce le **porte** (`MatchRepository`, `EventStore`, `Clock`, `DiceRoller`, `Notifier`);
- `infrastructure` e `api` = adattatori (JPA, WebSocket, REST, Supabase JWT).

Un solo deployable; niente microservizi.

### 6.2 Modello di dominio (motore)
| Concetto | Tipo | Note |
|---|---|---|
| `Match` | aggregate root | Stato completo di una partita, versione monotona |
| `PlayerId`, `TerritoryId`, `SeaId`, `MatchId` | value object (record) | Tipi forti, niente `String`/`long` nudi |
| `GameMap` | immutabile | Territori, gruppi, adiacenze terrestri, ponti, zone di mare e coste |
| `TerritoryState` | entità | proprietario (opzionale), bandierina viva, eserciti per giocatore |
| `Army` | value object | `tanks`, `jets`; sottomarini in `SeaState` per zona di mare |
| `Order` | sealed interface | `PlacePawn`, `Purchase`, `PlaceUnit`, `MoveOrder` (con catena) |
| `Battle` / `Duel` | oggetti di risoluzione | Producono eventi, non modificano lo stato altrove |
| `DomainEvent` | sealed interface | Unica fonte di verità dei cambiamenti di stato (6.4) |

Il tipo `Match` è **mutato solo applicando eventi** (`match.apply(event)`); i comandi producono eventi, non cambiano lo stato direttamente.

### 6.3 Macchina a stati della partita
```
LOBBY
  └► SETUP_PICKING        (scelta segreta round 1)
      └► SETUP_CONTESTS   (rivelazione + lanci round 1)
          └► SETUP_REPOSITION   (round 2, vincolo territorio libero)
              └► SETUP_RESOLVE  (lanci round 2 → 1.6 → 1.7, una volta)
                  └► TURN[n]
                       ├► PRODUCTION_ORDERS ─► PRODUCTION_SHOWDOWN
                       └► MOVEMENT_ORDERS   ─► MOVEMENT_SHOWDOWN ─► RESOLUTION(wave 1..k)
                              └► (vittoria?) ─► FINISHED     (altrimenti TURN[n+1])
```
- Ogni stato è un oggetto `Phase` (pattern **State**) con: `accepts(Command)`, `onEnter`, `isComplete()` (tutti hanno confermato o timer scaduto), `advance()`.
- Gli stati sono **tutti simultanei** tranne `RESOLUTION`, interamente eseguita dal server.
- Le transizioni sono **deterministiche**: ogni lancio di dadi usa il `DiceRoller` e viene registrato nell'evento corrispondente.

### 6.4 Comandi ed eventi
**Comandi** (da client a server, tutti con `commandId` UUID per l'idempotenza e `expectedVersion`):

| Comando | Fase | Contenuto |
|---|---|---|
| `JoinMatch` / `LeaveMatch` / `StartMatch` | Lobby | – |
| `SetPawns` | Setup r.1, r.2 | elenco di `TerritoryId` (sostituisce la bozza precedente) |
| `ConfirmSetup` | Setup | blocca la scelta |
| `PickCededTerritory` | Setup 1.6 / 1.7 | `TerritoryId` scelto dal beneficiario |
| `SetProductionPlan` | Produzione | acquisti e piazzamenti (carri, aerei, sottomarini + dove) |
| `ConfirmProduction` | Produzione | blocca il piano |
| `SetMoveOrders` | Movimento | lista di `MoveOrder` con catene, split e join |
| `ConfirmMovement` | Movimento | blocca gli ordini |
| `SetDefenseSplit` | Risoluzione 3.9d | assegnazione delle forze del difensore per duello |
| `Resign` | sempre | abbandono |

**Eventi** (dal server a tutti, o solo a un giocatore): sono l'**unico canale** con cui il client apprende lo stato. Esempi: `PlayerJoined`, `PhaseStarted`, `PlayerConfirmed` (senza contenuto), `PawnsRevealed`, `TerritoryAssigned`, `DiceRolled{who, dice[], booms}`, `ContestResolved`, `PawnReturned`, `CessionRolled`, `TerritoryCeded`, `PpGranted`, `UnitsPurchased`, `OrdersRevealed`, `WaveStarted`, `BattleStepStarted`, `UnitsDestroyed`, `TerritoryConquered`, `FlagDestroyed`, `PlayerEliminated`, `MatchFinished`.
Ogni evento ha: `matchId`, `seq` (progressivo), `type`, `visibility` (`PUBLIC` | `PLAYER(id)`), `payload`, `turn`, `phase`.

### 6.5 Design pattern adottati

| Pattern | Dove | Perché |
|---|---|---|
| **Hexagonal / Ports & Adapters** | Tutto il backend | Il dominio non conosce Spring né il DB; si testa a freddo |
| **Command** | `Command` + `CommandHandler` | Ogni azione del giocatore è un oggetto validabile, loggabile e ripetibile |
| **State** | `Phase` della partita | Ogni fase decide quali comandi accetta e quando finisce |
| **Domain Events / Event Log** | `DomainEvent` | Stato ricostruibile, replay, animazione lato client, audit |
| **Strategy** | `RuleSet`, `EconomyRules`, `VictoryCondition`, `TargetingPolicy`, `InitiativeCalculator`, `BotStrategy` | Le varianti simulate diventano implementazioni sostituibili |
| **Factory / Abstract Factory** | `MatchFactory`, `RuleSetFactory`, `UnitFactory` | Creazione partita da configurazione e mappa |
| **Repository** | `MatchRepository`, `EventStore`, `MapRepository` | Persistenza dietro interfaccia |
| **Chain of Responsibility** | Validazione degli ordini; pipeline di risoluzione delle ondate | Passi indipendenti e componibili |
| **Template Method** | `AbstractBattleStep` (Step 1, Step 2) | Struttura comune dello scontro con passi specifici |
| **Observer / Pub-Sub** | `Notifier` → STOMP | Il motore emette eventi, il trasporto li distribuisce |
| **Actor (single-writer)** | `MatchActor` per partita | Un solo thread modifica una partita: niente lock |
| **Memento / Snapshot** | `MatchSnapshot` a fine fase | Recupero dopo crash e riconnessione veloce |
| **DTO + Mapper** | `api/dto`, MapStruct | Il dominio non è mai esposto direttamente |
| **Builder** | `MatchConfig`, scenari di test | Costruzione leggibile di stati complessi |
| **Specification** | `OrderValidator` (regole di legalità) | Regole combinabili e testabili singolarmente |
| **Null Object** | `NoEconomy`, `NoCards` | Funzioni opzionali senza `if` sparsi |

Interfacce chiave (indicative):
```java
public interface DiceRoller {
    int boomDice(int n);            // numero di Boom su n dadi (1/3 per dado)
    int d6();                       // dado a 6 facce (clausola 1.7)
    <T> T pick(List<T> items);      // scelta casuale (territori non selezionabili)
}

public interface RuleSet {
    UnitCatalog units();
    EconomyRules economy();
    VictoryCondition victory();
    TargetingPolicy targeting();
    SetupRules setup();             // 1.4–1.7 incapsulate
}

public sealed interface Command permits SetPawns, ConfirmSetup, SetProductionPlan,
        ConfirmProduction, SetMoveOrders, ConfirmMovement, SetDefenseSplit, PickCededTerritory, Resign {
    CommandId id();
    PlayerId player();
}

public interface Phase {
    PhaseId id();
    ValidationResult validate(Match m, Command c);
    List<DomainEvent> handle(Match m, Command c, DiceRoller dice);
    boolean isComplete(Match m);
    List<DomainEvent> advance(Match m, DiceRoller dice);   // showdown, lanci, passaggio di fase
}
```

### 6.6 Casualità e determinismo
- Ogni partita ha un **seme** (`long`) generato con `SecureRandom` alla creazione e **mai inviato ai client** finché la partita è in corso.
- `SeededDiceRoller` usa un PRNG deterministico (es. `SplittableRandom`); ogni chiamata è registrata nell'evento relativo.
- La logica non usa mai `Math.random`, `new Random()` o l'orologio di sistema: tutto passa dalle porte `DiceRoller` e `Clock`.
- **Replay:** dato seme + log dei comandi, la partita si ricostruisce identica. A fine partita seme e log sono visibili (verifica pubblica dell'equità).

### 6.7 Gestione concorrente delle partite
- `MatchRegistry` mantiene le partite attive in memoria; ogni partita ha un **`MatchActor`** con una coda e un solo thread logico (executor a thread virtuali Java 21 o singolo thread per partita).
- Tutti i comandi di una partita passano dalla sua coda: serializzazione senza lock, ordine di arrivo = ordine di applicazione.
- **Idempotenza:** `commandId` già visto → risposta cached, nessun effetto doppio.
- **Persistenza:** a ogni evento `append` in `match_event`; a fine fase `snapshot` in `match_snapshot`. In caso di riavvio il server ricarica l'ultimo snapshot e riapplica gli eventi successivi.
- **Scalabilità:** v1 con **una sola istanza**. Per più istanze: routing sticky per `matchId` o lock distribuito (advisory lock Postgres) per garantire un solo proprietario per partita. Non necessario all'inizio.

### 6.8 API

**REST** (JSON, `/api/v1`):
| Metodo | Percorso | Scopo |
|---|---|---|
| `POST` | `/matches` | Crea partita (mappa, n. giocatori, profilo regole, timer) |
| `GET` | `/matches?status=lobby` | Elenco partite aperte |
| `POST` | `/matches/{id}/join` | Entra (anche con codice stanza) |
| `GET` | `/matches/{id}/view` | **Vista redatta** dello stato per il giocatore autenticato (per la riconnessione) |
| `GET` | `/matches/{id}/events?after={seq}` | Eventi visibili al giocatore dopo `seq` |
| `GET` | `/maps`, `/maps/{id}` | Mappe disponibili e dati geometrici |
| `GET` | `/me`, `PATCH /me` | Profilo e statistiche |

**WebSocket (STOMP)** su `/ws`:
- Invio comandi: `SEND /app/matches/{id}/command`
- Eventi pubblici: `SUBSCRIBE /topic/matches/{id}`
- Eventi privati (visibili al solo giocatore): `SUBSCRIBE /user/queue/matches/{id}`
- Errori di comando: `SUBSCRIBE /user/queue/errors`

Formato dei messaggi (envelope):
```json
{ "commandId": "uuid", "expectedVersion": 42, "type": "SetPawns", "payload": { "territories": ["EurOcc","GB"] } }
```
Il tipo del payload è un'unione discriminata (`type`) mappata da Jackson su record Java e da tipi TypeScript generati.

### 6.9 Pipeline di risoluzione del movimento
Esegue **solo** `MovementResolution` (3.9d), in modo deterministico:
1. **Validazione** di tutti gli ordini confermati (gittata, proprietà delle unità, adiacenza, catene coerenti).
2. **Rinforzi:** applica i movimenti interni, che arrivano in tempo (3.9d).
3. **Ondate:** `wave = 1..k`; per ogni regione bersaglio raccoglie gli attaccanti di quell'ondata.
4. Per ogni regione: se un solo attaccante → `Battle` (Step 1 + Step 2); se più attaccanti → duelli intrecciati con **mini-fase `SetDefenseSplit`** a inizio giro; attacchi incrociati → scontro con entrambi attaccanti.
5. Dopo ogni scontro aggiorna proprietà e catene (le catene perse decadono).
6. Alla fine: assegna i PP delle regioni conquistate (3.10) e controlla la **condizione di vittoria**.
Ogni passo emette eventi; il client riproduce la sequenza.

---

## 7. Database (PostgreSQL su Supabase)

### 7.1 Principi
- **Il database è accessibile solo dal backend.** Il frontend usa Supabase **solo per l'autenticazione**; nessuna chiamata diretta alle tabelle di gioco (niente PostgREST, niente Realtime per la logica di gioco).
- Su **tutte** le tabelle di gioco: `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` **senza policy** per `anon`/`authenticated`, così l'API automatica di Supabase non può leggerle o scriverle. Il backend si collega con un ruolo dedicato (non `anon`).
- **Connessione:** Hikari verso il pooler Supabase in **session mode** (porta 5432) oppure connessione diretta; per **Flyway** sempre connessione diretta. Se si usa il pooler in *transaction mode* (6543) vanno disattivati i prepared statement (`prepareThreshold=0`).
- **Migrazioni:** solo con Flyway (`V1__init.sql`, …), mai modifiche manuali dalla dashboard.
- **Tre ambienti Supabase:** `dev` (locale con Supabase CLI), `staging`, `prod`.

### 7.2 Schema (principale)
```
auth.users (Supabase)           ← gestita da Supabase Auth
profile        (id uuid PK → auth.users.id, nickname, created_at)

game_map       (id, code, name, version, data jsonb)          ← mappa come dati
  data = { territories[{code,name,group,polygon[],centroid}],
           adjacency[{a,b,kind:"land|bridge"}],
           seas[{code,name,polygon[]}], coasts[{sea,territory}] }

match          (id uuid PK, map_id, status, phase, turn, seed bigint,
                ruleset jsonb, version int, created_by, created_at, finished_at, winner_id)
match_player   (match_id, player_id, seat, color, shape, status, pp int, joined_at)
match_snapshot (match_id, version, phase, state jsonb, created_at)  PK(match_id, version)
match_event    (match_id, seq bigint, type, visibility, player_id null,
                payload jsonb, created_at)                           PK(match_id, seq)
match_order    (match_id, turn, phase, player_id, payload jsonb, confirmed_at)
```
Esempio di DDL (estratto):
```sql
create table match (
  id          uuid primary key default gen_random_uuid(),
  map_id      uuid not null references game_map(id),
  status      text not null check (status in ('LOBBY','RUNNING','FINISHED','ABORTED')),
  phase       text not null,
  turn        int  not null default 0,
  seed        bigint not null,
  ruleset     jsonb not null,
  version     int  not null default 0,
  created_by  uuid not null references profile(id),
  created_at  timestamptz not null default now(),
  finished_at timestamptz,
  winner_id   uuid references profile(id)
);
alter table match enable row level security;   -- nessuna policy: solo il ruolo del backend accede

create table match_event (
  match_id   uuid   not null references match(id) on delete cascade,
  seq        bigint not null,
  type       text   not null,
  visibility text   not null check (visibility in ('PUBLIC','PLAYER')),
  player_id  uuid,
  payload    jsonb  not null,
  created_at timestamptz not null default now(),
  primary key (match_id, seq)
);
alter table match_event enable row level security;
create index on match_event (match_id, visibility, player_id, seq);
```
- **Stato attivo:** vive in memoria nel `MatchActor`; il DB contiene **log degli eventi + snapshot** (modello *event sourcing leggero*). Le tabelle "stato corrente" non servono: la vista corrente si ricava da snapshot + eventi.
- **Ordini segreti:** `match_order` conserva gli ordini confermati per sopravvivere a un riavvio; non sono mai restituiti ad altri giocatori prima dello showdown.
- **Mappe:** i dati geometrici (poligoni 2D) stanno in JSONB; il client li usa per estrudere i territori in 3D.

### 7.3 Autenticazione con Supabase
- Il frontend usa `@supabase/supabase-js` (email/magic link, eventualmente OAuth).
- Ogni richiesta REST ha `Authorization: Bearer <access_token>`; la connessione WebSocket passa il token nell'header `CONNECT` di STOMP.
- Il backend valida il JWT con **Spring Security OAuth2 Resource Server**, issuer `https://<project>.supabase.co/auth/v1` e **JWKS** (se il progetto usa chiavi asimmetriche; altrimenti segreto HS256 condiviso). `sub` = `player_id`.
- Un `ChannelInterceptor` STOMP autentica `CONNECT`, associa `Principal` e verifica a ogni `SUBSCRIBE`/`SEND` che l'utente **appartenga alla partita**.

---

## 8. Frontend (React + TypeScript)

### 8.1 Organizzazione
- **Feature-based** (`features/lobby`, `features/setup`, …): ogni feature ha componenti, hook e logica locale.
- Il codice 3D vive in `scene/` ed è **solo di presentazione**: riceve dati dallo store e invia intenzioni (click) al livello `features`.
- **TypeScript `strict`**, niente `any`; tipi di API e messaggi **generati** dal contratto OpenAPI e validati a runtime con **zod** in ingresso dai WebSocket.

### 8.2 Gestione dello stato
| Store / strumento | Contenuto | Note |
|---|---|---|
| `matchStore` (Zustand) | Vista del gioco, **derivata dagli eventi** ricevuti | Riduttore puro `applyEvent(state, event)` |
| `draftStore` | Bozze locali non confermate (pedine, acquisti, ordini) | Mai trattate come verità; si inviano al server a ogni modifica e alla conferma |
| `uiStore` | Selezione, camera, pannelli, impostazioni | |
| TanStack Query | Dati REST (lobby, profilo, mappe) | Cache, retry |

**Flusso eventi:** `StompClient` → `EventQueue` → `EventPlayer`. L'`EventPlayer` applica gli eventi allo store e, per gli eventi di risoluzione, **li serializza in un'animazione** (lanci di dadi, esplosioni, avanzate) prima di passare al successivo. La vista "finale" è sempre coerente con la vista del server: se il client è in ritardo, può saltare l'animazione.

### 8.3 Schermate e flussi
1. **Accesso** (Supabase Auth) e **profilo**.
2. **Lobby:** elenco partite, crea/entra con codice, scelta mappa, numero giocatori, profilo regole, durata timer.
3. **Fase 1 – Setup:** mappa con le tue pedine (forma/colore); contatore "pedine da piazzare"; in round 2 evidenziazione dei territori liberi e avviso **"almeno 1 su territorio libero"**; pannello cessione per 1.6/1.7.
4. **Produzione:** pannello PP, acquisti per tipo, piazzamento su mappa/mare; riepilogo prima di confermare.
5. **Movimento:** creazione ordini per **trascinamento** da un territorio a un altro (frecce 3D), catene a più passi, split e join; stato "confermato" di ciascun giocatore (senza contenuto).
6. **Showdown e risoluzione:** rivelazione ordini, ondate, scontri animati; log scorrevole in lato.
7. **Fine partita:** vincitore, replay con seme pubblico, statistiche.

### 8.4 Pattern frontend
| Pattern | Uso |
|---|---|
| **Reducer / event-sourcing client** | `applyEvent` puro e testabile |
| **Observer** | Subscription STOMP → store |
| **Command (lato UI)** | Le azioni utente sono oggetti `Intent` → inviati come `Command` al server |
| **Adapter** | `StompClient`, `RestClient` nascosti dietro interfacce |
| **State machine** (XState opzionale) | Flusso UI per fase (bozza → confermato → showdown) |
| **Container / Presentational** | Feature = logica, `scene/` e `ui/` = presentazione |
| **Strategy** | Selettori di visualizzazione (palette, forme, modalità daltonici) |

### 8.5 Accessibilità e localizzazione
- Ogni giocatore ha **colore + forma** (sfera, cubo, cono, toro, ottaedro, cilindro): il gioco non dipende dal solo colore.
- Testi in **italiano** (default) e inglese tramite i18n; nessuna stringa nel codice dei componenti.
- Controlli da tastiera per conferme e navigazione; scala UI regolabile.

---

## 9. Grafica 3D

### 9.1 Stile
**Forme geometriche semplici**, stile "tavolo da guerra astratto": superfici piatte (flat shading), pochi colori saturi, ombre morbide, nessuna texture complessa. Obiettivo: leggibilità prima di tutto, **60 fps** su GPU integrate.

### 9.2 Il tavolo e la mappa
- **Mare:** un grande piano blu semitrasparente con griglia sottile; le **zone di mare** sono aree delimitate da linee tratteggiate (rilievo di una geometria piatta).
- **Territori:** poligoni 2D dal JSON della mappa → `THREE.Shape` → `ExtrudeGeometry` con **altezza uguale per tutti** (coerente con "tutti i territori valgono uguale"). Colore = proprietario; bordo chiaro del colore del gruppo (Africa, Europa, Asia, Oceania).
- **Ponti:** parallelepipedi sottili tra due territori.
- **Selezione e hover:** contorno luminoso e leggero sollevamento (animazione di scala/posizione).

### 9.3 Catalogo delle forme
| Elemento | Forma |
|---|---|
| **Pedina di scelta (Fase 1)** | Una primitiva diversa per giocatore: sfera, cubo, cono, toro, ottaedro, cilindro |
| **Bandierina / HQ** | Asta (cilindro sottile) + vessillo (parallelepipedo piatto) del colore e con la forma-simbolo del giocatore sulla cima; si abbatte (rotazione) quando viene distrutta |
| **Carro armato** | Parallelepipedo (scafo) + cilindro piccolo (torretta) + cilindro lungo e sottile (cannone) |
| **Cacciabombardiere** | Cono allungato (fusoliera) + due parallelepipedi piatti (ali) + piccolo parallelepipedo (coda); si "libra" sopra il territorio |
| **Sottomarino** | Capsula/ellissoide scuro con piccolo cilindro (torre), semi-immerso nella zona di mare |
| **Pila di unità** | Gruppi con **conteggio numerico** sopra (sprite/HTML), per non disegnare decine di modelli |
| **Dado Boom** | Cubo con 2 facce luminose (simbolo "boom" a stella a punte) e 4 facce neutre |
| **Esplosione** | Icosaedri che si espandono e svaniscono + anello (toro) che si dilata |
| **Ordini di movimento** | Archi (`TubeGeometry` su curva) con cono come punta di freccia, colore del giocatore; catene come archi consecutivi numerati |
| **Edifici (estensioni 15.1)** | Cubi/prismi sovrapposti (casette), prisma più massiccio per la fortezza |

### 9.4 Camera, luci e interazione
- **Camera prospettica** inclinata, **OrbitControls** con limiti (zoom, angolo, panoramica); preset "alto" e "inclinato".
- Luce direzionale + ambiente; ombre solo sul tavolo.
- **Raycasting** per il click sui territori; **drag & drop** da territorio a territorio per creare ordini; click destro/pressione lunga per annullare.
- Overlay HTML con `drei/Html` per etichette e contatori.

### 9.5 Animazioni
- Libreria: `@react-spring/three` o `gsap`; animazioni **guidate dagli eventi** (8.2).
- Dadi: lancio con fisica semplificata (solo cinematica, risultato noto dal server).
- Scontro: carri e aerei si avvicinano, esplosione, rimozione dell'unità; l'iniziativa è resa visibile (chi lancia per primo ha un'illuminazione sul bordo).
- Opzione **"salta animazioni"** e velocità regolabile.

### 9.6 Prestazioni
- **`InstancedMesh`** per unità e pedine dello stesso tipo; geometrie e materiali condivisi.
- Budget: < 200 draw call, < 100k triangoli, nessun post-processing pesante.
- `frameloop="demand"` quando non ci sono animazioni; DPR limitato su dispositivi mobili.
- **Fallback** a qualità ridotta (senza ombre) e, in futuro, vista 2D piatta di emergenza.

---

## 10. Multiplayer: sincronizzazione e segretezza

### 10.1 Modello di rete
- **Client → server:** comandi (WebSocket). **Server → client:** eventi (WebSocket). Il client **non** simula il gioco.
- Il gioco è a fasi simultanee, quindi **non serve prediction** né bassa latenza: bastano decine/centinaia di millisecondi.

### 10.2 Segretezza (commit–reveal)
- Le scelte e gli ordini sono **inviati subito** al server come bozza e **conservati redatti**: gli altri ricevono solo `PlayerConfirmed(playerId)` o `PlayerDraftUpdated(playerId)` senza contenuto.
- Allo showdown il server emette `…Revealed` **pubblico** con il contenuto di tutti.
- La vista di un giocatore (`/view`) è una **proiezione**: contiene tutto ciò che è pubblico + i **suoi** dati privati. Nessun campo segreto altrui nei payload.
- Il **seme** non è mai presente fino a fine partita.

### 10.3 Riconnessione
1. Il client riapre il WebSocket e invia `GET /view` per l'istantanea.
2. Poi `GET /events?after=seq` per recuperare gli eventi persi, oppure riceve di nuovo gli ultimi.
3. Il client confronta `version`; se c'è un buco, riprende dall'istantanea.
- Il server segna il giocatore `DISCONNECTED` ma **non ferma la partita** (10.4).

### 10.4 Timer e giocatori assenti
- Ogni fase simultanea ha un **timer configurabile** (es. Setup 120 s, Produzione 90 s, Movimento 180 s, Divisione forze 20 s).
- Allo scadere, i giocatori non confermati ricevono un **default**: la bozza attuale se valida, altrimenti nulla (nessun acquisto, nessun ordine; in Setup, pedine casuali valide).
- Se il giocatore è disconnesso per più di *N* turni consecutivi: passa al controllo di un **bot** (`BotStrategy`) oppure viene dichiarato abbandono (`Resign`).
- Il timer vive nel server (`PhaseTimer` con `ScheduledExecutorService`); il client mostra il tempo ricavato dalla scadenza assoluta (`deadlineAt`) inviata dal server, non un proprio conteggio.

### 10.5 Bot
- Interfaccia `BotStrategy { Command[] decide(MatchView view) }` che usa **la stessa vista redatta** di un giocatore umano: il bot non può barare.
- Le strategie del simulatore (Rusher, Aviazione, Economista, Tartaruga) sono il punto di partenza per i bot; serviranno anche per i test e per riempire le stanze.

---

## 11. Sicurezza e anti-cheat
- **Mai fidarsi del client:** ogni comando è validato in base a fase, proprietà, quantità, PP disponibili, gittata e adiacenza. Il vincolo "almeno una pedina su territorio libero" (1.5) è verificato **anche sul server**.
- **Autorizzazione:** ogni comando e sottoscrizione controlla che l'utente appartenga alla partita e sia il giocatore indicato nel comando.
- **Redazione dei dati:** unico punto di proiezione `MatchViewProjector`, con test automatici che verificano l'assenza di dati segreti nelle viste altrui.
- **Rate limiting** su REST e WebSocket (es. Bucket4j) e dimensione massima dei messaggi.
- **Validazione input:** Bean Validation sui DTO; limiti su catene di ordini (anche se il gioco non ha limiti di passi, il server impone un tetto tecnico alto per evitare abusi).
- **Segreti:** chiavi Supabase e credenziali DB solo nel backend (variabili d'ambiente / secret manager), mai nel bundle del frontend.
- **CORS** ristretto al dominio del frontend; **HTTPS/WSS** obbligatori.
- **Log e audit:** il log eventi completo permette di ricostruire e verificare ogni partita.
- **Privacy:** dati personali minimi (email in Supabase Auth, nickname pubblico); possibilità di cancellare l'account.

---

## 12. Test e bilanciamento

| Livello | Strumenti | Cosa si verifica |
|---|---|---|
| **Unit (engine)** | JUnit 5, AssertJ | Ogni regola: 1.4–1.7, iniziativa 3.7, bandierina 3.8, catene 3.4, ondate 3.9d |
| **Property-based** | jqwik | Invarianti: nessun giocatore sotto 1 territorio dopo la cessione 1.7; somma dei territori = territori selezionabili; l'operazione 1.7 avviene **al massimo una volta**; stesso seme = stesso risultato |
| **Golden / replay** | File di partite con seme | Il replay riproduce gli stessi eventi (non regressione) |
| **Statistici** | Monte Carlo in test | Distribuzione dei Boom ≈ 1/3; esiti degli scontri coerenti con `simulazione/sim.py` |
| **Integrazione backend** | Spring Boot Test + **Testcontainers (PostgreSQL)** | Migrazioni Flyway, persistenza eventi, recupero da snapshot |
| **WebSocket** | Test STOMP con più client | Segretezza (un client non vede i dati altrui), riconnessione, idempotenza |
| **Sicurezza** | Test su JWT, ruoli, sottoscrizioni | Accesso non autorizzato rifiutato |
| **Frontend unit** | Vitest + Testing Library | Riduttore eventi, validazioni UX, store |
| **E2E** | Playwright (2–3 browser) | Partita completa in lobby → Fase 1 → 3 turni |
| **Visual** | Screenshot della scena in casi noti | Regressioni grafiche principali |

**Bilanciamento:** `sim.py` resta l'**oracolo**. A ogni modifica di regole si rieseguono le simulazioni; il porting in Java (`rg-sim-cli`) permette di confrontare i risultati (percentuali di vittoria per strategia, partite bloccate, valanga) tra le due implementazioni. Le varianti scelte (`VARIANTI.md`) diventano **profili di regole** selezionabili in lobby.

**Playtest:** sessioni a 3 giocatori della Fase 1 con il nuovo flusso (1.5–1.7) per verificare: quante volte scatta il riposizionamento, quante volte la clausola di cessione, se il vincolo "almeno un territorio libero" è percepito come equo.

---

## 13. DevOps e ambienti
- **CI (GitHub Actions):** build e test backend (Maven + Testcontainers), lint/typecheck/test/build frontend, controllo del contratto OpenAPI (tipi TS rigenerati devono coincidere).
- **Ambienti:** locale (Docker Compose per il backend + Supabase CLI), staging, produzione.
- **Deploy backend:** immagine Docker (Spring Boot layered jar) su una piattaforma con **WebSocket persistenti** (Fly.io, Railway, Render o VPS). **Una sola istanza** all'inizio.
- **Deploy frontend:** hosting statico con CDN (Vercel, Netlify, Cloudflare Pages). Il frontend parla con `VITE_API_URL` e `VITE_WS_URL`.
- **Osservabilità:** Spring Actuator + Micrometer (metriche: partite attive, comandi/s, latenza fase), **log JSON** con `matchId` e `commandId`, tracciamento errori (Sentry su frontend e backend).
- **Configurazione:** variabili d'ambiente (12-factor); nessun segreto nel repository.
- **Versionamento:** *Conventional Commits*, versione semantica del **contratto** (`/api/v1`) e del **profilo di regole** (salvato nella partita: partite vecchie restano giocabili/rigiocabili).
- **ADR:** ogni scelta tecnica importante ha una nota in `docs/adr/`.

---

## 14. Roadmap di sviluppo

| Tappa | Obiettivo | Esito verificabile |
|---|---|---|
| **M0 – Fondamenta** | Repo, build, CI, `rg-engine` vuoto, mappa di test come JSON | Pipeline verde |
| **M1 – Motore headless, Fase 1** | Preparazione, scelta segreta, contestazioni, riposizionamento 1.5, 1.6, clausola 1.7, tutto in memoria | Test e property test verdi; simulazione di centinaia di Fasi 1 da CLI |
| **M2 – Motore headless, Fasi 2–3** | Produzione, movimento, ondate, scontri, catene, bandierina | Confronto statistico con `sim.py` |
| **M3 – Backend** | Spring, persistenza eventi, REST + STOMP, auth Supabase, timer | Due client di test giocano una partita completa |
| **M4 – Client "brutto"** | React + vista 2D/griglia di debug, lobby, ordini | Partita giocabile da browser (anche in locale) |
| **M5 – 3D** | Scena R3F con mappa estrusa, pedine, unità, dadi, ordini ad arco | Fase 1 e Movimento giocabili in 3D |
| **M6 – Animazione e UX** | `EventPlayer`, showdown, suoni, accessibilità, i18n | Partita completa fluida a 3–4 giocatori |
| **M7 – Bot e bilanciamento** | `BotStrategy`, profili di regole, riconnessione robusta | Partite con stanze miste umani/bot |
| **M8 – Beta chiusa** | Hosting, osservabilità, playtest con amici | Raccolta dati per le Domande aperte |
| **Dopo** | Economia/carte (15.1), sottomarini completi, spettatori, classifiche | – |

Traguardo di ogni tappa: *"che bello, funziona pur essendo brutto"*, e solo dopo si rifinisce.

---

## 15. Estensioni in valutazione e domande aperte

### 15.1 Estensioni in valutazione (non ancora adottate)
Le simulazioni in `simulazione/VARIANTI.md` hanno esplorato modifiche **non** incluse nel GDD. Restano disponibili come **profili di regole** (pattern *Strategy*, 6.5):
- **Economia a due risorse** (PP + soldi da rendita territori, casette e fortezza; oppure gruppi colore tipo Monopoly): E2/E3 danno risultati simili tra loro.
- **Aeroporti** (aerei solo con aeroporto) e **l'aereo da solo non conquista**: riducono il predominio dell'Aviazione.
- **Limite di unità per territorio** (consigliato 20, +50% per caserma) per evitare gli stalli.
- **Carte** (Scudo Spaziale, Missili Balistici, Tradimento, Tregua, Sfondamento anfibio, Siluro Killer, Super Produzione, Arma Segreta; vedi `7carteor.jpeg`).
- **Iniziativa a parità di aerei all'attaccante** invece che al difensore.
- Configurazione "Q" consigliata finora: duello aereo, aeroporti, bandierina a 1 dado (2 con fortezza), carte mazzo d, vittoria a 14 territori su 20, limite 20 unità.

Nulla di questo entra nel motore base finché non verrà deciso nella Parte 15.2.

### 15.2 Domande aperte (da decidere)
1. **Condizione di vittoria** (3.11): dominio completo, 3 gruppi su 4, numero di territori? Valore proposto: **maggioranza assoluta di territori** (es. 14 su 20) mantenuta per un turno.
2. **Giocatore ancora a 0 dopo la clausola 1.7** (1.7 punto 6): eliminato subito (regola provvisoria) oppure riceve un territorio neutro? Con mappe grandi non capita quasi mai (1.8).
3. **Territori senza proprietario dopo la Fase 1** (1.6, 3.8): senza difesa (ipotesi attuale) oppure con una bandierina neutra con difesa fissa?
4. **Dadi del round 2** (1.5): uso dei "territori posseduti all'inizio del round 2" come numero di dadi: va verificato nei playtest che non favorisca troppo chi è già avanti.
5. **Sottomarini** (3.9c): meccanica di attacco e risposta della difesa.
6. **Ricalcolo dell'iniziativa durante uno step** (3.7).
7. **Economia e carte** (15.1): quali profili e in che ordine entrano.
8. **Scelta manuale dei bersagli** (3.6): resta automatica online, o diventa una scelta con timer?
9. **Numero minimo di territori per giocatore** (`n`): consigliato ≥ 5 per ridurre l'impatto della clausola di recupero (1.8).
10. **Mappe aggiuntive** oltre ai 20 territori di test (es. mappa a 42 territori).
