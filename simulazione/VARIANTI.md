# Varianti simulate – registro delle modifiche

Simulatore: `sim.py` · Comando: `python sim.py varianti <partite> <lettera>`
Usa tutti i core (`SIM_WORKERS` per cambiarli) e tiene la cache delle stime in `wp_cache_*.pkl`, che si può cancellare. A parità di regole l'output è identico a ogni esecuzione, con qualsiasi numero di processi.
Ogni variante è stata giocata su **E2 (edifici)** e **E3 (Monopoly)**, 3 giocatori, tetto di 40 turni, con 4 strategie bot (Rusher, Aviazione, Economista, Tartaruga).
Una strategia bilanciata vince circa il **33%**.

---

## Registro delle idee
Ogni idea ha un ID, un grado e una versione da cui parte. Il registro si aggiorna sul ramo base, non sui rami `idea/`.

| ID | Grado | Idea | Parte da | Stato | Ramo o etichetta | Risultati | Decisione |
|---|---|---|---|---|---|---|---|
| I-001 | Grande | Dadi netti: lancio simultaneo, conta la differenza di Boom | S | Scartata | `scartata/I-001` | `risultati_v10_S_dadi_netti.txt` | Rusher più forte, Contrattacco più debole, stalli uguali |
| I-002 | Grande | Dado per unità e somma contro somma | S | Proposta | `idea/dadi-somma` | – | Da decidere: costo per il vincitore, dado dell'aereo |
| I-003 | Grande | Dadi classici alla Risiko, solo negli scontri | S | Proposta | – | – | Da valutare dopo I-002 |
| I-004 | Media | Test bot bravo contro bot scarso, per misurare il peso del ragionamento | S | Proposta | – | – | – |
| I-005 | Media | Regola di fine partita per le partite bloccate | S | Proposta | – | – | – |
| I-006 | Media | Premio alla difesa per rendere giocabile la Tartaruga | S | Proposta | – | – | – |
| I-007 | Grande | Economia più sviluppata: partire dalle scelte del giocatore | S | Proposta | – | – | Dopo la decisione sugli scontri |
| I-008 | Piccola | Casetta a 250 soldi in E2 | S | Proposta | – | – | – |
| I-009 | Piccola | Massimo fisso alla mano di carte | S | Proposta | – | – | – |

**Gradi**
- **Piccola:** cambia un numero. Non serve un ramo: si prova come variante di `sim.py`.
- **Media:** cambia o aggiunge una regola. Ha un ramo `idea/`.
- **Grande:** cambia un sistema intero, come scontri o economia. Ha un ramo `idea/` e tocca GDD, simulatore e risultati.

**Stati:** proposta, in prova, adottata, scartata.

**Percorso**
1. Si registra l'idea con ID, grado e base.
2. Si apre il ramo dalla sua base, se il grado lo richiede.
3. Si modificano GDD e simulatore nel ramo e si salvano i risultati.
4. Si decide e si aggiorna il registro con il motivo.
5. Se è adottata, si unisce alla base. Se è scartata, si mette l'etichetta `scartata/I-xxx` e si chiude il ramo.

**Rami:** `main` contiene solo le regole approvate; `variante/...` è una configurazione completa da cui partire; `idea/...` è una singola modifica. Il GDD ufficiale non si tocca finché un'idea non è adottata.

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
| **Contrattacco** | Converte tutti i soldi in unità. | Uguale. |
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
| **H** = G + b | Bandierina 1 dado (fortezza 2). | Nessun effetto (98% bloccate; rifatta, vedi nota). |
| **I** = G + c (3 gruppi) | Vittoria con 3 gruppi colore su 4. | 95% bloccate. |
| **J** = G + d | Mazzo: Super Produzione 6 (era 12), Tradimento 12 (era 6). Mano = territori ÷ 2 (era ÷ 3). | Le carte eliminano il doppio delle unità, ma 94–96% bloccate (rifatta, vedi nota). |
| **K** = G + b + c (3 gruppi) + d | Le tre modifiche insieme. | 89% bloccate. |
| **L** = G + b + c (14 territori) + d | Come K, ma vittoria con **14 territori su 20**. | 72% bloccate, durata 34 turni. |
| **M** = L + a | A parità di aerei lancia per primo l'**attaccante** (anche contro la bandierina). | 64% bloccate, buon equilibrio. |
| **N** = M + limite 10 + caserma | Massimo 10 unità per territorio. Caserma (300 soldi) = +50% del limite in quel territorio, per ogni caserma. L'eccesso a fine turno va in un territorio vicino con spazio, altrimenti è perso. | Sbloccata (8%, 15 turni), ma Rusher 85%. |
| **O** = M + limite 6 + caserma | Come N, limite 6. | 6% bloccate, Rusher 92%. |
| **P** = M + limite 15 + caserma | Come N, limite 15. | 8% bloccate, Rusher 80%. |
| **Q** = M + limite 20 + caserma | Come N, limite 20. | 8–12% bloccate, 18–19 turni, valanga 69%; Rusher 70–72%. |
| **R** = M + limite 25 + caserma | Come N, limite 25. | 10–12% bloccate, 19–20 turni, valanga 64–67%; Rusher 67–68%. |
| **S** = M + limite 30 + caserma | Come N, limite 30. | **Miglior compromesso:** 12–18% bloccate, 21–22 turni, valanga 61–67%; Rusher 58–61% (rifatta con il simulatore veloce, `risultati_v8_sim_veloce.txt`). |
| **T** = Q + limite sugli attacchi | Un'armata che attacca non supera il limite del bersaglio. | Peggiore: 21–26% bloccate, caserme raddoppiate, Rusher 68–74%. Scartata. |

**Nota sul bug (corretto il 2026-11-04):** nelle prime esecuzioni di H e J la condizione di vittoria risultava disattivata, quindi il 100% di bloccate era un artefatto. I valori di `risultati_v4_stallo.txt` per H e J non sono validi: quelli corretti sono in `risultati_v7_limite_30.txt`. Le conclusioni non cambiano.

---

## Bot Contrattacco (dal 2026-11-04)
- **Di norma:** guardia alta e attacca solo con almeno l'80% di probabilità di vittoria.
- **Territorio nemico scoperto:** conquistato nell'ultimo turno, oppure con almeno 4 unità il turno prima e ora dimezzate o meno.
- **Se ne vede uno a portata:** abbassa la guardia, lo attacca per primo con soglia 55% e può proseguire in catena.
- **Parametri:** primo tentativo, senza taratura.

Prova sulla variante S (`risultati_v9_contrattacco.txt`), 100 partite per combinazione:

| Bot | E2 con / senza Contrattacco | E3 con / senza Contrattacco |
|---|---|---|
| Rusher | 43,3% / 58,0% | 41,3% / 61,0% |
| Aviazione | 21,3% / 16,0% | 29,7% / 24,0% |
| Economista | 52,0% / 54,7% | 38,7% / 38,7% |
| Tartaruga | 2,0% / 3,3% | 10,7% / 8,7% |

Contrattacco vince il 38,7% in E2 e il 37,0% in E3. Il dominio del Rusher dipendeva in buona parte dai bot, ma resta un vantaggio moderato. Partite bloccate 18–22% sul totale; tra soli Contrattacco 36–49%.

`SIM_BOTS` sceglie le strategie in gioco, per esempio `SIM_BOTS=Rusher,Aviazione,Economista,Tartaruga` per riprodurre i risultati a 4 bot.

---

## S_dadi_netti – scontri a lancio simultaneo (scartata, 2026-11-05)
Idea dell'utente: si lancia insieme e chi fa meno Boom perde solo la differenza. Prova con 5 bot, 100 partite per combinazione (`risultati_v10_S_dadi_netti.txt`).

- **Puri:** chi fa meno Boom perde la differenza, chi ne fa di più non perde nulla.
- **Costo:** come puri, ma il vincitore perde un terzo dei Boom nemici, per difetto. A parità ognuno perde un terzo dei Boom dell'altro.
- **Simultaneo:** ognuno perde tanti Boom quanti ne fa l'altro.
- **Regole provvisorie comuni:** niente iniziativa né duello aereo; chi ha più aerei fa +1 Boom; nell'anfibio il +1 Boom va al difensore; bandierina invariata.

| Misura (E2 / E3) | S | Puri | Costo | Simultaneo |
|---|---|---|---|---|
| Rusher | 50,7 / 51,2% | 56,0 / 55,2% | 55,3 / 52,0% | 55,8 / 56,5% |
| Rusher con Contrattacco | 43,3 / 41,3% | 48,7 / 49,0% | 48,0 / 42,0% | 47,7 / 49,7% |
| Contrattacco | 38,7 / 37,0% | 34,8 / 32,7% | 34,8 / 34,3% | 34,2 / 32,7% |
| Tartaruga | 2,7 / 9,7% | 2,0 / 4,7% | 2,0 / 6,2% | 1,7 / 7,3% |
| Aviazione | 18,7 / 26,8% | 20,3 / 32,0% | 21,8 / 32,0% | 16,5 / 24,5% |
| Bloccate | 18,5 / 22,4% | 19,5 / 24,7% | 18,5 / 23,1% | 19,7 / 24,3% |
| Valanga | 61 / 66% | 63 / 67% | 66 / 66% | 63 / 65% |

**Esito:** nessuna delle tre aiuta. Il Rusher sale, Contrattacco e Tartaruga scendono, stalli e valanga non migliorano. Il vantaggio di chi lancia per primo a forze pari è reale nei singoli scontri (87% su 20 contro 20), ma toglierlo non cambia l'equilibrio.

---

## Carte (dalla variante F in poi)
- **Mazzo:** 6 Scudo Spaziale, 6 Missili Balistici, 6 Tradimento, 6 Tregua, 6 Sfondamento anfibio, 12 Siluro Killer (inutile senza sottomarini), 12 Super Produzione, 12 Arma Segreta. Gli scarti si rimescolano quando il mazzo finisce.
- **Mano:** territori ÷ 3, arrotondato per difetto. All'inizio della Produzione si completa la mano. Le trappole piazzate contano nel limite.
- **Arma Segreta e Tradimento:** al massimo 1 per scontro per giocatore.
  - **Trappola:** piazzata dopo lo showdown della Produzione. Scatta quando il territorio attacca o viene attaccato, con precedenza su tutto, anche sugli aerei.
  - **Magia:** dalla mano, dopo l'iniziativa aerea; prima l'effetto della carta, poi il lancio normale.
- **Bot:** Economista e Tartaruga usano le carte come trappole, Rusher e Aviazione come magia. I Missili colpiscono il giocatore con più territori.

---

## Configurazione consigliata finora (S)
- **Iniziativa:** duello aereo; a parità di aerei lancia per primo l'attaccante.
- **Aerei:** aeroporti (300 soldi, 3 aerei); l'aereo da solo non conquista.
- **Bandierina:** 1 dado (2 con la fortezza).
- **Carte:** mazzo d (Super Produzione 6, Tradimento 12), mano = territori ÷ 2.
- **Vittoria:** 14 territori su 20.
- **Limite:** 30 unità per territorio, +50% per ogni caserma.

## Da provare
- Rivedere la Tartaruga, troppo debole in tutte le prove, e l'Economista, forte in E2.
- Ridurre le partite bloccate.
- Dadi classici: da scegliere tra confronto alla Risiko e colpo su soglia.
- Sottomarini e Siluro Killer, quando la loro meccanica sarà definita.
- Riportare nel GDD le regole scelte.
