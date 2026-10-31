# ADR 0001 – Architettura esagonale in un monolite modulare

- **Stato:** accettata
- **Riferimento:** GDD 4.2, 6.1

## Contesto
Il gioco richiede un motore di regole deterministico, testabile e confrontabile con `simulazione/sim.py`.

## Decisione
Backend Java 21 / Spring Boot 3 come monolite modulare: `rg-engine` (dominio puro, nessuna dipendenza da Spring/DB),
`rg-server` (casi d'uso, REST/STOMP, persistenza), `rg-sim-cli` (simulazioni headless). Dipendenza ammessa solo
`rg-server → rg-engine`.

## Conseguenze
Il motore si testa a freddo e con replay a seme fisso; il costo è un po' di mapping tra dominio e DTO.
