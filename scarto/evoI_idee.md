# evoI_idee — Meccaniche evolute

> File delle meccaniche progettate **oltre** `proto_idee.txt`, rifinite in sessione.
> Ogni meccanica qui dentro è considerata *chiusa per la v1 (loop brutto)*, salvo nota.

---

## Meccanica 1 — "Affitto & Presa"

**Stato:** ✅ chiusa per il loop v1
**Origine:** risolve il buco aperto in `proto_idee.txt` riga 74
> *"cosa impedisce all'occupante militare di espropriare invece di incassare?"*

**Idea in una riga:** la soluzione vive nel **layer militare** (che esiste già), non in una penalità economica appiccicata sopra. Espropriare diventa un atto militare *committed e leggibile*, non una multa invisibile.

### Le regole

1. **Affitto.** Possiedi un edificio in territorio nemico → paghi affitto al padrone del territorio. (È l'"anima di Monopoli in versione strategica": ostaggi reciproci, dipendenze geografiche.)

2. **Presidio.** Proteggi l'edificio con un presidio:
   - max **N unità** (numero **fisso per tipo di edificio** — *non* upgradabile in v1);
   - le unità stanno **dentro** la struttura;
   - sono **solo-difesa**: difendono l'edificio ma **non possono attaccare il territorio circostante**.

3. **Nebbia di guerra sul presidio.** Il nemico sa *che* c'è un presidio, **non** *quante* unità contiene → deve attaccare alla cieca → gambit "ho stimato male" (`proto_idee.txt` riga 67) in purezza.

4. **Costo di mantenimento logistico.** Tenere un presidio costa logistica **crescente con la profondità** (riga 83): più la fabbrica è in fondo al territorio nemico, più costa difenderla.

5. **Esito della presa.** Se il nemico attacca e il presidio **cede**:
   - la gestione dell'edificio passa all'attaccante;
   - l'edificio è **danneggiato**: produce **di meno**;
   - **ripararlo costa soldi** e **costa tempo** (N impulsi di riparazione);
   - le unità del presidio sono **distrutte** (ultima difesa — scelta per leggibilità).

### Perché funziona (i principi rispettati)

- **Regola-che-chiude col colpevole preciso** (riga 111): il vincolo "solo-difesa, non attacca il territorio" impedisce che ogni fabbrica in affitto diventi una **testa di ponte gratuita** per invadere. Senza il vincolo, degenererebbe.
- **Imposta-e-dimentica → peso zero** (riga 78): piazzi il presidio e resta. Non è una decisione per impulso. Anche i tre stati dell'edificio (intatto / danneggiato / in-riparazione) si attivano solo su evento raro → passano il test del peso.
- **Azzardo da info nascosta, non da penalità nascosta** (riga 67): la presa è una scelta visibile e committed.

### Intrecci gratuiti con altre meccaniche

- **Logistica (riga 83):** il presidio in profondità è "isolato e costoso" per definizione → difendere costa di più tanto più la fabbrica è lontana.
- **Combattimento asimmetrico (riga 65):** il presidio *difende* → usa il valore difesa → la **fanteria** è il guardiano naturale (ruolo emergente del vertice "terra" del triangolo a 3 unità).

### Emergenze (non progettate, escono dal sistema)

- **Il bluff.** Presidio 1 unità che ne simula 10: il nemico sovra-stima e non attacca. Tensione psicologica a costo-codice zero.
- **L'over-presidio si auto-punisce.** Troppe unità ferme in profondità bruciano logistica senza combattere → il sistema castiga l'eccesso da solo.
- **Anti-turtle.** La nebbia bilancia il vantaggio strutturale del difensore: ha il valore-difesa, ma l'attaccante non sa quanto portare → l'equilibrio non si rompe a senso unico.

### La decisione-cuore che genera

> *"Il bottino una-tantum vale più del flusso d'affitto che risparmierei, meno le unità che perdo contro un presidio di numero ignoto, meno il rendimento ridotto e il tempo/costo di riparazione dopo?"*

= il cannoni-vs-burro condensato su **un singolo edificio**.

### Nota architetturale (per le fasi successive)

La **nebbia vive sul muro sim↔rendering** (righe 23/52): la simulazione conosce *tutti* i presidi (le serve per risolvere il combattimento in modo deterministico — "due scatole, stesso mondo"); è la **UI** che nasconde i numeri al giocatore che non possiede l'edificio.
→ Nel **loop brutto** parti con **info piena** (più veloce). La nebbia sul presidio è la *prima* feature-informazione da aggiungere, perché è quella che rende il meccanismo un vero azzardo.

### Da NON fare in v1 (tendril potati)

- ❌ Capacità del presidio upgradabile (tech-tree che spunta).
- ❌ Variante "difesa da casella adiacente" (ambigua, spalma la difesa sulla mappa).
- ❌ Stato "prigioniero" per le unità catturate (nuovo sistema da gestire).
- ❌ Penalità reputazionale per l'esproprio (opaca, nemica del target "voglio capire" → eventuale v2.0).
