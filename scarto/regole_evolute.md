# Regole evolute — tracciamento da `proto_idee.txt`

> Registro vivo delle **decisioni consolidate**. Parte dalle decisioni già prese in
> `proto_idee.txt` e traccia come evolvono nelle sessioni di design.
> Le meccaniche rifinite in dettaglio vivono in `evoI_idee.md`; qui sta il quadro d'insieme.

**Bussola del progetto:** *"non voglio HOI4"* + *"il giocatore deve poter sbagliare e capire perché"*.
**Filo rosso:** la voce che frena ("quanto appesantisce?", "magari non troppe unità") ha quasi sempre ragione. Il peso non è il numero di sistemi, ma **il numero di decisioni per impulso** (riga 78).

---

## Decisioni-chiave già fissate (da proto_idee.txt)

| Area | Decisione | Rif. |
|------|-----------|------|
| **Concept** | Fusione Risiko+Monopoli: territori producono output economico **e** militare. Dilemma cannoni-vs-burro al centro. | 4–5 |
| **Tempo** | Modello a impulsi (WEGO): ordini accodati, risolti quando tutti pronti o scade timer. Multiplayer = una sola modalità simultanea. | 16–17 |
| **Architettura** | Command pattern + sim deterministica a timestep fisso. **Muro netto sim ↔ rendering.** | 22–23 |
| **IA** | Competente, non intelligente: Utility AI + influence maps + script-personalità. No reti neurali. Difficoltà = manopole (handicap, ritardo, qualità decisioni). Leggibilità = telegrafare le intenzioni. | 27–33 |
| **Networking** | Lockstep deterministico (modello AoE '97). Host = smistatore di comandi, non autorità. Godot: ENet+RPC, strato lockstep scritto a mano. | 37–47 |
| **Determinismo** | Matematica a **interi/fixed-point** (no float nella logica). Un solo RNG con seme condiviso. Checksum di stato a ogni impulso. Soldi in centesimi; frontend mostra la virgola. | 41–54 |
| **Pannello dati** | Solo dati **azionabili** ("vedendo questo, faccio una mossa diversa?"). Tre famiglie: tendenze, composizione/colli di bottiglia, confronto relativo. Con nebbia → stime, non onniscienza. | 58–61 |
| **Militare** | Att/dif **asimmetrici** (Axis & Allies): difensore usa valore difesa, attaccante valore attacco. Counter system (morra A>B>C>A) anti-doomstack. Combattimento deterministico: azzardo da info nascosta, non da dadi. | 65–68 |
| **Economia** | Affitto su territorio altrui. Catena edificio→unità (cuore). Miniera→stock→unità: 1–2 risorse, non 5. Banca/inflazione → v2.0. | 73–78 |
| **Logistica** | Solo la **soglia leggibile** (vicino alla caserma gratis; oltre tot caselle isolata e costosa). Niente ferrovie/mantenimento decrescente/sconti navali in v1. | 82–84 |
| **Estetica** | "L'impero vivo" (navi, aerei, ciminiere) è l'anima, **non** una meccanica → protetto, non tagliato. Quasi tutto rendering decorativo → il muro sim/rendering lo carica senza rischio desync. | 88–92 |
| **Ordine di build** | 1) loop in memoria, brutto → 2) backend+DB → 3) rete lockstep → 4) grafica. NON partire dal database. Traguardo: "che bello, funziona pur essendo brutto". | 96–98 |

---

## Le 4 meccaniche del loop minimo (riga 112)

Intrecciate generano già **rusher / mercante / turtle** senza progettarle:

1. Attacco/difesa asimmetrici
2. Soglia logistica
3. Edificio → unità
4. Affitto altrui

---

## Evoluzioni di questa sessione

### ✅ #1 — Affitto altrui → "Affitto & Presa"
La meccanica 4 viene chiusa con il modello **presidio difesa-solo + nebbia sul presidio + edificio danneggiato alla presa**. Risolve il buco di riga 74 dentro il layer militare.
→ Dettaglio completo in **`evoI_idee.md` § Meccanica 1**.

---

## Nodi di design ancora aperti (prossimi sul tavolo)

- [ ] **Triangolo a 3 unità** (riga 69): definire terra / anti-terra / rompi-stallo, i loro valori att/dif asimmetrici e le relazioni di counter.
- [ ] **Soglia logistica numerica** (riga 83): quante caselle dalla caserma; quanto costa l'isolamento; come si lega al mantenimento del presidio.
- [ ] **Risorse**: quante (1–2) e cosa producono; stock vs flusso (riga 76).
- [ ] **Catena edificio→unità**: quali edifici, quali unità, tempi/costi.

---

## Liste di disciplina (riga 110)

**IL LOOP (5 cose da costruire prima):**
1. Mappa a caselle con territori (stato in RAM)
2. Catena edificio→unità
3. Combattimento asimmetrico + counter
4. Soglia logistica
5. Affitto & Presa

**ESPERIMENTI PER DOPO (al sicuro, uno alla volta a playtest):**
- Ferrovie (candidata 2ª meccanica logistica — almeno è una scelta)
- Banca / inflazione (v2.0)
- Real-time-con-pausa contro IA (nasce gratis dal motore a impulsi)
- Unità oltre il triangolo (aerei, navi, missili...) — *6 unità = 15 relazioni da playtestare*
- Penalità reputazionale, stato prigioniero, presidio upgradabile (vedi tendril potati in `evoI_idee.md`)
