# Varianti simulate – registro delle modifiche

Simulatore: `sim.py` · Comando: `python sim.py varianti <partite> <lettera>`
Ogni variante è stata giocata su **E2 (edifici)** e **E3 (Monopoly)**, 3 giocatori, tetto di 40 turni, con 4 strategie bot (Rusher, Aviazione, Economista, Tartaruga).
Una strategia bilanciata vince circa il **33%**.

---

## Base comune (ipotesi della simulazione)
- Mappa: i 20 territori della lista, con i confini e i ponti confermati (`progettazione/mapa_test.jpeg`).
- Coste e mari per gli aerei: **ipotesi mia** (tabella `SEAS` in `sim.py`), un mare conta come 1 regione.
- Madagascar: nessun ponte.
- Territori non selezionabili: senza difesa.
- Sottomarini: esclusi.
- Scontri con più attaccanti: semplificati.
- Economie: E2 ed E3, descritte in dettaglio nella sezione seguente.

---

## Le due economie

### Cosa hanno in comune
- **Due risorse separate.**
  - **PP:** 1 per ogni territorio posseduto, a ogni Produzione. Servono solo per comprare unità. Quelli non spesi si accumulano.
  - **Soldi:** vengono dalla rendita delle carte territorio. Servono per gli edifici, oppure si convertono in PP.
- **Soldi iniziali:** 1.630 a testa (2×500, 4×100, 2×50, 4×20, 5×10).
- **Conversione:** 100 soldi = 1 PP. Si convertono solo centinaia intere; il resto (sotto 100) rimane in cassa per il turno dopo.
- **Le carte seguono la mappa.** Ogni territorio ha la sua carta, intestata a chi lo possiede. Se lo perdi, la carta passa al conquistatore. Le carte non si comprano: si conquistano.
- **I territori non selezionabili** hanno la carta ma nessun proprietario, quindi nessuno ne incassa la rendita finché non vengono conquistati.
- **Casette verdi:** massimo **3** per territorio. Ogni casetta aggiunge alla rendita del territorio un importo pari alla rendita base del suo gruppo.
- **Conquista:**
  - il territorio perde **1 casetta** (saccheggio), le altre passano al conquistatore;
  - fortezza, aeroporto e caserma passano intatti al conquistatore.
- **Ordine nella Produzione:**
  1. si incassano PP e rendita;
  2. si costruiscono gli edifici (in segreto);
  3. i soldi rimasti si convertono in PP;
  4. si comprano e piazzano le unità;
  5. showdown: si rivela tutto insieme.
- **Edifici aggiunti dalle varianti** (solo dove indicato):
  - **aeroporto** (varianti C, E, G–Q): 300 soldi, ospita 3 aerei, i nuovi aerei si piazzano solo lì;
  - **caserma** (varianti N–Q): 300 soldi, +50% del limite di unità del territorio per ogni caserma.

### E2 – Edifici
Tutti i territori valgono uguale. La scelta è tra **rendita** (casette) e **difesa** (fortezza).

| Voce | Valore |
|---|---|
| Rendita base per carta | **50** a turno, uguale per tutti i gruppi |
| Casetta verde | costa **200**, +**50** di rendita, massimo 3 per territorio |
| Tempo per ripagare una casetta | **4 turni** |
| Territorio al massimo (3 casette) | 50 + 3×50 = **200** a turno |
| Fortezza (casa rossa) | costa **400**, massimo 1 per territorio: la bandierina lancia **+1 dado** (3 invece di 2; nelle varianti con bandierina a 1 dado, 2 invece di 1) |
| Bonus gruppo completo | **nessuno** |

**Esempio:** con 7 territori e nessuna casetta incassi 350 a turno, cioè 3,5 PP se converti tutto. Una casetta da 200 equivale a rinunciare a 2 carri oggi per avere mezzo PP in più a ogni turno.

### E3 – Monopoly
I gruppi colore hanno **valori diversi** e possedere un gruppo intero raddoppia la rendita base. Non c'è la fortezza: l'unico edificio economico è la casetta.

| Gruppo | Territori | Rendita base | Con gruppo completo | Costo casetta | + rendita per casetta | Tempo per ripagare | Territorio al massimo (3 casette) |
|---|---|---|---|---|---|---|---|
| 🔵 Blu (Africa) | Africa Occidentale, Sahara, Egitto, Africa Meridionale, Madagascar | 30 | 60 | 150 | +30 | 5 turni | 120 (150 con il gruppo) |
| 🟣 Viola (Asia) | Medio Oriente, Caucaso, India, Cina, Urali | 40 | 80 | 200 | +40 | 5 turni | 160 (200 con il gruppo) |
| 🔴 Rosso (Europa) | Europa Occidentale, Gran Bretagna, Europa Centro-Orientale, Russia, Scandinavia | 50 | 100 | 250 | +50 | 5 turni | 200 (250 con il gruppo) |
| 🟢 Verde (Oceania) | Indocina, Borneo, Nuova Guinea, Australia Occidentale, Australia Orientale | 60 | 120 | 300 | +60 | 5 turni | 240 (300 con il gruppo) |

- **Il bonus del gruppo raddoppia solo la rendita base**, non quella delle casette.
- **Fortezza:** non esiste in E3.
- **Ordine di valore:** Africa < Asia < Europa < Oceania. L'ordine è un'ipotesi mia, da decidere.
- **L'Oceania vale il doppio dell'Africa.** I territori non valgono più uguale: alcuni diventano bersagli più appetibili di altri.

**Esempio:** possedere tutta l'Oceania senza casette rende 5×120 = **600** a turno. Gli stessi 5 territori in Africa rendono 5×60 = **300**.

### Come usano le economie i bot
| Bot | E2 | E3 |
|---|---|---|
| **Economista** | Fino al turno 6 compra casette sui territori più sicuri, poi converte tutto in unità. | Uguale, preferisce i gruppi con rendita più alta. |
| **Tartaruga** | Compra fortezze sui territori di confine più minacciati, il resto in unità. | Niente fortezza: compra casette nei territori interni fino al turno 6. |
| **Rusher / Aviazione** | Convertono tutti i soldi in unità. | Uguale. |
| **Tutti** (varianti con aeroporti/caserme) | Costruiscono aeroporti per gli aerei che vogliono comprare e caserme quando al fronte manca spazio. | Uguale. |

### Differenze osservate nelle simulazioni
- E2 ed E3 danno risultati molto simili in tutte le varianti: la differenza tra le due economie pesa meno delle regole di guerra.
- In E3 la **Tartaruga** va un po' meglio (circa 10–17% contro 2–8% in E2), perché le casette interne le rendono più della fortezza.
- In E2 l'**Economista** va un po' meglio: casette economiche (200) con un ritorno rapido (4 turni).
- In media si costruiscono 12–14 casette a partita in tutte e due le economie; in E2 si aggiungono circa 3 fortezze.

---

## Prima serie – economie (`risultati_v1.txt`)
Regole di guerra del GDD così come sono, confronto tra 4 economie: **E0** solo PP, **E1** soldi = PP, **E2** edifici, **E3** Monopoly.
- **Risultato:** l'Aviazione vince il 75–86% in tutte le economie; il 70–89% delle partite si blocca. **E1 scartata.**

---

## Varianti

| Variante | Cosa cambia rispetto alla precedente | Risultato principale |
|---|---|---|
| **A** – base | Regole del GDD, economie E2 ed E3. | Aviazione 86–88%, 72% bloccate. |
| **B** = A + duello aereo | Prima dello scontro combattono solo gli aerei; chi resta padrone del cielo ha l'iniziativa. | Nessun effetto. |
| **C** = A + aeroporti | Aerei solo con aeroporto (300 soldi, 3 aerei ciascuno); si piazzano lì. | Gli aerei calano dal 25% al 7%, ma l'Aviazione vince ancora il 75–79%. |
| **D** = A + aereo non conquista + anfibio | Senza almeno un carro non si conquista. Carta sfondamento anfibio, 1 a testa: dalla costa, carri verso un territorio sullo stesso mare; il difensore lancia sempre per primo. | Strategie bilanciate, ma il 99% delle partite si blocca. |
| **E** = B + C + D | Tutte e tre le correzioni sugli aerei insieme. | Bilanciata, 99% bloccate, valanga scende al 62%. |
| **F** = A + carte | Mazzo delle carte (vedi sotto) sulle regole del GDD. | Aviazione domina ancora (83–86%); bloccate 55–59%. |
| **G** = E + carte | Mazzo delle carte sopra tutte le correzioni sugli aerei. | **Più bilanciata** (circa 35% a testa), ma 98% bloccate. |
| **H** = G + b | Bandierina 1 dado (fortezza 2). | Nessun effetto (100% bloccate). |
| **I** = G + c (3 gruppi) | Vittoria con 3 gruppi colore su 4. | 95% bloccate. |
| **J** = G + d | Mazzo: Super Produzione 6 (era 12), Tradimento 12 (era 6). Mano = territori ÷ 2 (era ÷ 3). | Le carte eliminano il doppio delle unità, ma 100% bloccate. |
| **K** = G + b + c (3 gruppi) + d | Le tre modifiche insieme. | 89% bloccate. |
| **L** = G + b + c (14 territori) + d | Come K, ma vittoria con **14 territori su 20**. | 72% bloccate, durata 34 turni. |
| **M** = L + a | A parità di aerei lancia per primo l'**attaccante** (anche contro la bandierina). | 64% bloccate, buon equilibrio. |
| **N** = M + limite 10 + caserma | Massimo 10 unità per territorio. Caserma (300 soldi) = +50% del limite in quel territorio, per ogni caserma. L'eccesso a fine turno va in un territorio vicino con spazio, altrimenti è perso. | Sbloccata (8%, 15 turni), ma Rusher 85%. |
| **O** = M + limite 6 + caserma | Come N, limite 6. | 6% bloccate, Rusher 92%. |
| **P** = M + limite 15 + caserma | Come N, limite 15. | 8% bloccate, Rusher 80%. |
| **Q** = M + limite 20 + caserma | Come N, limite 20. | **Miglior compromesso:** 10% bloccate, 19 turni, valanga 69%; Rusher ancora 71%. |

---

## Carte (dalla variante F in poi)
- **Mazzo:** 6 Scudo Spaziale, 6 Missili Balistici, 6 Tradimento, 6 Tregua, 6 Sfondamento anfibio, 12 Siluro Killer (inutile senza sottomarini), 12 Super Produzione, 12 Arma Segreta. Gli scarti si rimescolano quando il mazzo finisce.
- **Mano:** territori ÷ 3, arrotondato per difetto. All'inizio della Produzione si completa la mano. Le trappole piazzate contano nel limite.
- **Arma Segreta e Tradimento:** al massimo 1 per scontro per giocatore.
  - **Trappola:** piazzata dopo lo showdown della Produzione. Scatta quando il territorio attacca o viene attaccato, con precedenza su tutto, anche sugli aerei.
  - **Magia:** dalla mano, dopo l'iniziativa aerea; prima l'effetto della carta, poi il lancio normale.
- **Bot:** Economista e Tartaruga usano le carte come trappole, Rusher e Aviazione come magia. I Missili colpiscono il giocatore con più territori.

---

## Configurazione consigliata finora (Q)
- **Iniziativa:** duello aereo; a parità di aerei lancia per primo l'attaccante.
- **Aerei:** aeroporti (300 soldi, 3 aerei); l'aereo da solo non conquista.
- **Bandierina:** 1 dado (2 con la fortezza).
- **Carte:** mazzo d (Super Produzione 6, Tradimento 12), mano = territori ÷ 2.
- **Vittoria:** 14 territori su 20.
- **Limite:** 20 unità per territorio, +50% per ogni caserma.

## Da provare
- Limite 25 o 30.
- Limite 20 + limite anche per gli attacchi (un'armata che attacca non supera il limite del bersaglio).
- Sottomarini e Siluro Killer, quando la loro meccanica sarà definita.
- Riportare nel GDD le regole scelte.
