# Regole di Guerra

Videogioco web multiplayer a fasi simultanee e segrete. Il design è in
[mainGamesRules/GDD_ufficiale.md](mainGamesRules/GDD_ufficiale.md).

## Struttura
| Cartella | Contenuto |
|---|---|
| `mainGamesRules/` | GDD ufficiale, varianti, idee e sommario globale |
| `progettazione/` | Immagini di riferimento |
| `simulazione/` | `sim.py` e risultati (oracolo di bilanciamento) |
| `scarto/` | idee scartate |
| `backend/` | `rg-engine` (dominio puro), `rg-server` (Spring Boot), `rg-sim-cli` |
| `frontend/` | React + TypeScript + three.js |
| `docs/adr/` | decisioni architetturali |

## Avvio in locale
```bash
docker compose up -d db                 # Postgres su :54322
cd backend && mvn verify                # build e test
cd backend/rg-server && mvn spring-boot:run
cd frontend && cp .env.example .env && npm install && npm run dev
```
Requisiti: Java 21, Maven, Node 22, Docker.
