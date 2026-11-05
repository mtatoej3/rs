# Sommario globale delle regole

Tiene traccia di tutte le versioni e le idee del gioco. I dettagli delle simulazioni sono in `../simulazione/VARIANTI.md`.

## Struttura
```text
mainGamesRules/
├── GDD_ufficiale.md      regole approvate
├── SOMMARIO.md           questo file
└── S/                    variante grande, base di lavoro
    ├── GDD_S.md          GDD completo
    ├── S_dadi_netti/     sottovariante scartata
    └── S_dadi_somma/     sottovariante proposta
```

- **Variante grande:** una versione giocabile per intero, con il GDD completo, come `S/`.
- **Sottovariante:** sta dentro la cartella della sua base. Il suo GDD contiene solo ciò che cambia rispetto alla base. Se viene adottata, le modifiche entrano nel GDD della base.
- **Nome della cartella:** `<base>_<idea>`, così si vede subito da dove parte.

## Versioni
| Versione | Cartella | Parte da | Stato |
|---|---|---|---|
| Ufficiale | `GDD_ufficiale.md` | – | Riferimento, si cambia solo con un'idea adottata |
| S | `S/` | Ufficiale | In prova, base di lavoro |

## Idee
| ID | Grado | Idea | Parte da | Stato | Cartella | Risultati | Decisione |
|---|---|---|---|---|---|---|---|
| I-001 | Grande | Dadi netti: lancio simultaneo, conta la differenza di Boom | S | Scartata | `S/S_dadi_netti/` | `risultati_v10_S_dadi_netti.txt` | Rusher più forte, Contrattacco più debole, stalli uguali |
| I-002 | Grande | Dado per unità e somma contro somma | S | Proposta | `S/S_dadi_somma/` | – | Da decidere: costo per il vincitore, dado dell'aereo |
| I-003 | Grande | Dadi classici alla Risiko, solo negli scontri | S | Proposta | – | – | Da valutare dopo I-002 |
| I-004 | Media | Test bot bravo contro bot scarso, per misurare il peso del ragionamento | S | Proposta | – | – | – |
| I-005 | Media | Regola di fine partita per le partite bloccate | S | Proposta | – | – | – |
| I-006 | Media | Premio alla difesa per rendere giocabile la Tartaruga | S | Proposta | – | – | – |
| I-007 | Grande | Economia più sviluppata: partire dalle scelte del giocatore | S | Proposta | – | – | Dopo la decisione sugli scontri |
| I-008 | Piccola | Casetta a 250 soldi in E2 | S | Proposta | – | – | – |
| I-009 | Piccola | Massimo fisso alla mano di carte | S | Proposta | – | – | – |

**Gradi**
- **Piccola:** cambia un numero. Niente cartella: si prova come variante di `sim.py`.
- **Media:** cambia o aggiunge una regola. Ha una cartella quando entra in prova.
- **Grande:** cambia un sistema intero, come scontri o economia. Ha una cartella quando entra in prova.

**Stati:** proposta, in prova, adottata, scartata.

## Percorso di un'idea
1. Si registra qui con ID, grado e base.
2. Si crea la cartella `<base>_<idea>` dentro quella della base, se il grado lo richiede, con il suo GDD.
3. Si prova in `sim.py` e si salvano i risultati in `simulazione/`.
4. Si decide e si scrive qui il motivo.
5. Se è adottata, le modifiche entrano nel GDD della base. Se è scartata, la cartella resta come archivio.
