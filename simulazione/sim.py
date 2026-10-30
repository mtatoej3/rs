"""Simulatore partite - GDD Regole di Guerra + 4 economie.
Uso: python sim.py [partite_per_combinazione]
"""
import random, sys, itertools
from collections import defaultdict

# ---------------------------------------------------------------- MAPPA
T = ["AfrOcc", "Sahara", "Egitto", "AfrMer", "Madagascar",
     "EurOcc", "GB", "EurCO", "Russia", "Scandinavia",
     "MedOr", "Caucaso", "India", "Cina", "Urali",
     "Indocina", "Borneo", "NGuinea", "AusOcc", "AusOr"]
GROUP = {}
for g, ts in {"Blu": T[0:5], "Rosso": T[5:10], "Viola": T[10:15], "Verde": T[15:20]}.items():
    for t in ts:
        GROUP[t] = g

# confini via terra + ponti (confermati dall'utente)
EDGES = [("AfrOcc", "Sahara"), ("Sahara", "Egitto"), ("Sahara", "AfrMer"),
         ("AfrOcc", "EurOcc"), ("EurOcc", "GB"), ("GB", "EurCO"), ("EurOcc", "EurCO"),
         ("EurCO", "Russia"), ("Russia", "Scandinavia"),
         ("Egitto", "MedOr"), ("MedOr", "Caucaso"), ("MedOr", "Cina"), ("MedOr", "India"),
         ("Russia", "Caucaso"), ("Russia", "Urali"), ("Caucaso", "Urali"), ("Caucaso", "Cina"),
         ("India", "Cina"), ("Cina", "Indocina"), ("India", "Indocina"),
         ("AusOcc", "AusOr"), ("Indocina", "Borneo"), ("Borneo", "NGuinea"), ("NGuinea", "AusOr")]
# IPOTESI: coste sui mari (per gli aerei un mare conta come 1 regione)
SEAS = {"AtlSud": ["AfrOcc", "AfrMer", "EurOcc"],
        "AtlNord": ["EurOcc", "GB", "Scandinavia"],
        "Medit": ["AfrOcc", "Sahara", "Egitto", "EurOcc", "EurCO", "MedOr"],
        "Indiano": ["AfrMer", "Madagascar", "Egitto", "MedOr", "India", "Indocina", "Borneo", "AusOcc"],
        "Pacifico": ["Indocina", "Cina", "Borneo", "NGuinea", "AusOr"]}

LAND = {t: set() for t in T}
for a, b in EDGES:
    LAND[a].add(b); LAND[b].add(a)
_air = {t: set(LAND[t]) for t in T}
for s, cs in SEAS.items():
    _air[s] = set(cs)
    for c in cs:
        _air[c].add(s)
AIR = {}  # territori raggiungibili dagli aerei (gittata 2, mare = 1 passo)
for t in T:
    r = set()
    for n in _air[t]:
        if n in LAND: r.add(n)
        for m in _air[n]:
            if m in LAND: r.add(m)
    r.discard(t)
    AIR[t] = r

# ---------------------------------------------------------------- ECONOMIE
START_MONEY = 1630
PP_PRICE = 100
ECON = {
    "E0_soloPP":  dict(money=False),
    "E1_soldiPP": dict(money=True, rent={g: 50 for g in "Blu Rosso Viola Verde".split()}, houses=False, fort=False, sets=False),
    "E2_edifici": dict(money=True, rent={g: 50 for g in "Blu Rosso Viola Verde".split()}, houses=True, fort=True, sets=False,
                       house_cost={g: 200 for g in "Blu Rosso Viola Verde".split()}, fort_cost=400),
    "E3_monopoly": dict(money=True, rent={"Blu": 30, "Viola": 40, "Rosso": 50, "Verde": 60}, houses=True, fort=False, sets=True,
                        house_cost={"Blu": 150, "Viola": 200, "Rosso": 250, "Verde": 300}),
}
MAX_HOUSES = 3

# ratio = probabilità minima di vittoria per lanciare un attacco
# ---------------------------------------------------------------- STRATEGIE
STRAT = {
    "Rusher":     dict(air=0.0,  keep=0.2, ratio=0.55, chain=True,  build=None,     place_def=0.2),
    "Aviazione":  dict(air=0.7,  keep=0.3, ratio=0.55, chain=True,  build=None,     place_def=0.3),
    "Economista": dict(air=0.25, keep=0.6, ratio=0.70, chain=False, build="houses", place_def=0.6),
    "Tartaruga":  dict(air=0.25, keep=1.0, ratio=0.85, chain=False, build="turtle", place_def=1.0),
}
MIN_PLANES = 2
ECON_BUILD_UNTIL = 6 # l'Economista costruisce fino al turno 6, poi converte tutto

# ---------------------------------------------------------------- DADI / SCONTRI
P_BOOM = 1 / 3
def roll(n):
    r = random.random
    return sum(1 for _ in range(n) if r() < P_BOOM)

def size(a): return a[0] + a[1]          # army = [carri, aerei]
def hit(a, h):                          # chi colpisce elimina prima gli aerei
    k = min(h, a[1]); a[1] -= k; h -= k
    a[0] = max(0, a[0] - h)

def exchange(att, dfn, att_first):
    """un giro di lanci a turno (o simultaneo se att_first is None)"""
    if att_first is None:
        ha, hd = roll(size(att)), roll(size(dfn)); hit(dfn, ha); hit(att, hd)
    elif att_first:
        hit(dfn, roll(size(att)))
        if size(dfn): hit(att, roll(size(dfn)))
    else:
        hit(att, roll(size(dfn)))
        if size(att): hit(dfn, roll(size(att)))

def step1_1v1(att, dfn):
    first = att[1] > dfn[1]  # parità -> difensore; iniziativa fissa nello step
    while size(att) and size(dfn):
        exchange(att, dfn, first)

def flag_exchange(att, dice):
    """un giro contro la bandierina; True se conquistata"""
    if att[1] >= 1:
        if roll(size(att)): return True
        hit(att, roll(dice))
    else:
        hit(att, roll(dice))
        if size(att) and roll(size(att)): return True
    return False

def split_def(dfn, atts):
    tot = sum(size(a) for a in atts) or 1
    parts = []
    rem = [dfn[0], dfn[1]]
    for i, a in enumerate(atts):
        if i == len(atts) - 1:
            parts.append(rem[:]); break
        f = size(a) / tot
        p = [min(rem[0], round(dfn[0] * f)), min(rem[1], round(dfn[1] * f))]
        rem[0] -= p[0]; rem[1] -= p[1]
        parts.append(p)
    return parts

_WP = {}
def win_prob(at, ap, dt, dp, dice):
    """probabilità stimata (Monte Carlo, in cache) che l'attaccante conquisti la regione"""
    if dice == 0: return 1.0 if at + ap else 0.0
    key = (min(at, 40), min(ap, 20), min(dt, 40), min(dp, 20), dice)
    if key not in _WP:
        w = 0
        for _ in range(150):
            a, d = [key[0], key[1]], [key[2], key[3]]
            step1_1v1(a, d)
            if size(d) == 0:
                while size(a):
                    if flag_exchange(a, dice): w += 1; break
        _WP[key] = w / 150
    return _WP[key]

# ---------------------------------------------------------------- GIOCO
class Game:
    def __init__(self, strategies, econ_name, max_turns=40):
        self.n = len(strategies)
        self.strat = strategies
        self.E = ECON[econ_name]
        self.max_turns = max_turns
        self.owner = {t: None for t in T}
        self.units = {t: [0, 0] for t in T}
        self.houses = {t: 0 for t in T}
        self.fort = {t: False for t in T}
        self.pp = [0] * self.n
        self.money = [START_MONEY if self.E["money"] else 0] * self.n
        self.stats = dict(houses=0, forts=0, battles=0)

    # ---------- Fase 1
    def phase1(self):
        k = len(T) // self.n
        blocked = set(random.sample(T, len(T) % self.n))
        sel = [t for t in T if t not in blocked]
        picks = []
        for p in range(self.n):  # ogni bot sceglie un blocco compatto a partire da un seme casuale
            seed = random.choice(sel); chosen = [seed]
            while len(chosen) < k:
                fr = [n for c in chosen for n in LAND[c] if n in sel and n not in chosen]
                chosen.append(random.choice(fr) if fr and random.random() < 0.85
                              else random.choice([t for t in sel if t not in chosen]))
            picks.append(set(chosen))
        cnt = defaultdict(list)
        for p, s in enumerate(picks):
            for t in s: cnt[t].append(p)
        safe = [sum(1 for t in picks[p] if len(cnt[t]) == 1) for p in range(self.n)]
        losses = [0] * self.n
        for t in sel:
            ps = cnt[t]
            if len(ps) == 1: self.owner[t] = ps[0]
            elif len(ps) > 1:
                cont = ps[:]
                while True:
                    if all(safe[p] == 0 for p in cont): win = None; break
                    r = {p: roll(safe[p]) for p in cont}
                    m = max(r.values()); top = [p for p in cont if r[p] == m]
                    if len(top) == 1: win = top[0]; break
                    cont = top
                for p in ps:
                    if p != win: losses[p] += 1
                if win is not None: self.owner[t] = win
        free = [t for t in sel if self.owner[t] is None]
        random.shuffle(free)
        for p in range(self.n):
            for _ in range(losses[p]): self.owner[free.pop()] = p

    # ---------- utilità bot
    def owned(self, p): return [t for t in T if self.owner[t] == p]
    def threat(self, t, p):
        s = 0
        for n in LAND[t]:
            if self.owner[n] not in (p, None): s += self.units[n][0]
        for n in AIR[t]:
            if self.owner[n] not in (p, None): s += self.units[n][1]
        return s
    def def_eq(self, t):
        if self.owner[t] is None: return 0
        return size(self.units[t]) + (2.2 if self.fort[t] else 1.5)
    def frontier(self, p):
        return [t for t in self.owned(p) if any(self.owner[n] != p for n in LAND[t] | AIR[t])]

    # ---------- Fase 2: produzione
    def production(self, turn):
        E = self.E
        for p in range(self.n):
            mine = self.owned(p)
            if not mine: continue
            self.pp[p] += len(mine)
            if E["money"]:
                inc = 0
                for t in mine:
                    base = E["rent"][GROUP[t]]
                    if E["sets"] and all(self.owner[x] == p for x in T if GROUP[x] == GROUP[t]): base *= 2
                    inc += base + self.houses[t] * E["rent"][GROUP[t]]
                self.money[p] += inc
        for p in range(self.n):
            if self.owned(p): self.spend(p, turn)

    def spend(self, p, turn):
        S, E = STRAT[self.strat[p]], self.E
        mine = self.owned(p)
        if E["money"]:
            b = S["build"]
            if b == "houses" and E["houses"] and turn <= ECON_BUILD_UNTIL:
                cand = sorted(mine, key=lambda t: (self.threat(t, p), -E["rent"][GROUP[t]]))
                for t in cand:
                    c = E["house_cost"][GROUP[t]]
                    while self.houses[t] < MAX_HOUSES and self.money[p] >= c:
                        self.money[p] -= c; self.houses[t] += 1; self.stats["houses"] += 1
            elif b == "turtle":
                if E["fort"]:
                    for t in sorted(self.frontier(p), key=lambda t: -self.threat(t, p)):
                        if not self.fort[t] and self.money[p] >= E["fort_cost"]:
                            self.money[p] -= E["fort_cost"]; self.fort[t] = True; self.stats["forts"] += 1
                elif E["houses"] and turn <= ECON_BUILD_UNTIL:
                    for t in [t for t in mine if t not in self.frontier(p)]:
                        c = E["house_cost"][GROUP[t]]
                        if self.houses[t] < MAX_HOUSES and self.money[p] >= c:
                            self.money[p] -= c; self.houses[t] += 1; self.stats["houses"] += 1
            self.pp[p] += self.money[p] // PP_PRICE
            self.money[p] %= PP_PRICE
        # acquisto unità
        pp = self.pp[p]
        planes = int(pp * S["air"] / 2 + random.random())
        have = sum(self.units[t][1] for t in mine)
        if have + planes < MIN_PLANES:  # serve almeno qualche aereo (Madagascar si prende solo dal cielo)
            planes = min(pp // 2, MIN_PLANES - have)
        tanks = pp - 2 * planes
        self.pp[p] = 0
        new = [[1, 0]] * tanks + [[0, 1]] * planes
        random.shuffle(new)
        # piazzamento: prima la difesa del fronte, poi tutto sulla base d'attacco
        front = self.frontier(p) or mine
        need = {t: max(0, S["place_def"] * self.threat(t, p) - size(self.units[t])) for t in front}
        best = min(((self.def_eq(e), s) for s in front for e in LAND[s] | AIR[s] if self.owner[e] != p),
                   default=(0, random.choice(front)))[1]
        for u in new:
            tgt = max(need, key=need.get) if need and max(need.values()) >= 1 else best
            if tgt in need: need[tgt] -= 1
            self.units[tgt][0] += u[0]; self.units[tgt][1] += u[1]

    # ---------- Fase 3: ordini
    def orders(self, p):
        S = STRAT[self.strat[p]]
        mine = self.owned(p)
        avail = {}
        for t in mine:
            g = int(S["keep"] * self.threat(t, p) + 0.5)
            a = self.units[t][:]
            k = min(a[0], g); a[0] -= k; g -= k
            a[1] -= min(a[1], g)
            avail[t] = a
        orders, targeted = [], set()
        targets = sorted({e for t in mine for e in LAND[t] | AIR[t] if self.owner[e] != p}, key=self.def_eq)
        for tg in targets:
            d = self.units[tg]
            dice = 0 if self.owner[tg] is None else (3 if self.fort[tg] else 2)
            ok = lambda at, ap: win_prob(at, ap, d[0], d[1], dice) >= S["ratio"]
            srcs = [s for s in mine if tg in LAND[s] or tg in AIR[s]]
            parts, tot = [], [0, 0]
            for s in sorted(srcs, key=lambda s: -size(avail[s])):
                a = avail[s]
                take = [a[0] if tg in LAND[s] else 0, a[1]]
                if size(take) == 0: continue
                parts.append((s, take)); tot[0] += take[0]; tot[1] += take[1]
                if ok(*tot): break
            if size(tot) and ok(*tot):
                # restituisci i carri in eccesso finché la probabilità resta sopra soglia
                for s, take in parts:
                    while take[0] and ok(tot[0] - 1, tot[1]):
                        take[0] -= 1; tot[0] -= 1
                got = size(tot)
                for s, take in parts:
                    avail[s][0] -= take[0]; avail[s][1] -= take[1]
                chain = []
                if S["chain"]:
                    surplus = got - self.def_eq(tg) * 1.3
                    nxt = sorted([n for n in LAND[tg] if self.owner[n] != p and n not in targeted and n != tg], key=self.def_eq)
                    if nxt and surplus >= 1.3 * self.def_eq(nxt[0]) + 1:
                        chain = [nxt[0]]; targeted.add(nxt[0])
                orders.append(dict(p=p, parts=[(s, t) for s, t in parts if size(t)], steps=[tg] + chain))
                targeted.add(tg)
        # movimenti interni: dalle retrovie verso il fronte (1 spostamento)
        front = set(self.frontier(p))
        moves = []
        for t in mine:
            if t in front or size(avail[t]) == 0: continue
            dst = [n for n in LAND[t] if self.owner[n] == p]
            if dst:
                d = min(dst, key=lambda n: 0 if n in front else 1)
                moves.append((t, d, avail[t][:])); avail[t] = [0, 0]
        return orders, moves

    def movement(self):
        all_orders, all_moves = [], []
        for p in range(self.n):
            if self.owned(p):
                o, m = self.orders(p); all_orders += o; all_moves += m
        # le unità partono
        for o in all_orders:
            for s, a in o["parts"]:
                self.units[s][0] -= a[0]; self.units[s][1] -= a[1]
        for s, d, a in all_moves:
            self.units[s][0] -= a[0]; self.units[s][1] -= a[1]
        for s, d, a in all_moves:  # i rinforzi arrivano in tempo
            self.units[d][0] += a[0]; self.units[d][1] += a[1]
        # onde
        live = []
        for o in all_orders:
            army = [sum(a[0] for _, a in o["parts"]), sum(a[1] for _, a in o["parts"])]
            live.append(dict(p=o["p"], army=army, steps=o["steps"], srcs={s for s, _ in o["parts"]}, i=0))
        wave = 0
        while live:
            groups = defaultdict(lambda: dict(army=[0, 0], srcs=set(), conts=[]))
            for o in live:
                tg = o["steps"][o["i"]]
                g = groups[(o["p"], tg)]
                g["army"][0] += o["army"][0]; g["army"][1] += o["army"][1]
                if wave == 0: g["srcs"] |= o["srcs"]
                if o["i"] + 1 < len(o["steps"]): g["conts"].append(o["steps"][o["i"] + 1])
            # attacchi incrociati
            keys = list(groups)
            for (p, tg) in keys:
                for (q, tg2) in keys:
                    if p < q and tg2 in groups[(p, tg)]["srcs"] and tg in groups[(q, tg2)]["srcs"] \
                            and self.owner[tg] == q and self.owner[tg2] == p:
                        a, b = groups[(p, tg)]["army"], groups[(q, tg2)]["army"]
                        first = None if a[1] == b[1] else a[1] > b[1]
                        while size(a) and size(b): exchange(a, b, first)
            by_target = defaultdict(list)
            for (p, tg), g in groups.items():
                if size(g["army"]): by_target[tg].append((p, g))
            nxt = []
            for tg, lst in by_target.items():
                self.stats["battles"] += 1
                winner = self.resolve(tg, [(p, g["army"]) for p, g in lst])
                for p, g in lst:
                    if p == winner and g["conts"] and size(self.units[tg]) > 1:
                        a = self.units[tg]
                        go = [a[0] - 1 if a[0] else 0, a[1] if a[0] else a[1] - 1]
                        a[0] -= go[0]; a[1] -= go[1]
                        nxt.append(dict(p=p, army=go, steps=[g["conts"][0]], srcs=set(), i=0))
            live = nxt; wave += 1

    def resolve(self, tg, atts):
        """atts: lista (player, army). Ritorna il proprietario finale."""
        atts = [(p, a) for p, a in atts]
        while True:
            own = self.owner[tg]
            # rinforzi propri che arrivano dalle catene
            for p, a in atts:
                if p == own and size(a):
                    self.units[tg][0] += a[0]; self.units[tg][1] += a[1]; a[0] = a[1] = 0
            act = [(p, a) for p, a in atts if size(a) and p != own]
            if not act: return own
            act.sort(key=lambda x: -x[1][1] + random.random() * 0.1)
            if own is None:
                p, a = act[0]
                self.conquer(tg, p, a); continue
            dfn = self.units[tg]
            if len(act) == 1:
                step1_1v1(act[0][1], dfn)
            else:
                while size(dfn) and sum(size(a) for _, a in act) > 0:
                    alive = [(p, a) for p, a in act if size(a)]
                    if len(alive) == 1:
                        step1_1v1(alive[0][1], dfn); break
                    alive.sort(key=lambda x: -x[1][1])
                    parts = split_def(dfn, [a for _, a in alive])
                    for (p, a), d in zip(alive, parts):
                        if size(d) == 0: continue
                        first = None if a[1] == d[1] else a[1] > d[1]
                        exchange(a, d, first)
                    dfn[0] = sum(d[0] for d in parts); dfn[1] = sum(d[1] for d in parts)
            if size(dfn): continue  # attaccanti eliminati: loop esce al prossimo giro
            # step 2: assalto alla bandierina
            dice = 3 if self.fort[tg] else 2
            took = None
            while took is None:
                alive = sorted([(p, a) for p, a in act if size(a)], key=lambda x: -x[1][1])
                if not alive: break
                for p, a in alive:
                    if flag_exchange(a, dice): took = (p, a); break
            if took: self.conquer(tg, *took)

    def conquer(self, tg, p, a):
        self.owner[tg] = p
        self.units[tg] = [a[0], a[1]]
        a[0] = a[1] = 0
        if self.houses[tg]: self.houses[tg] -= 1  # saccheggio

    # ---------- partita
    def play(self):
        self.phase1()
        leader5 = None
        for turn in range(1, self.max_turns + 1):
            self.production(turn)
            self.movement()
            counts = [len(self.owned(p)) for p in range(self.n)]
            if turn == 5:
                m = max(counts)
                leader5 = counts.index(m) if counts.count(m) == 1 else None
            if max(counts) == len(T):
                return dict(winner=counts.index(len(T)), turns=turn, timeout=False, leader5=leader5, **self.stats)
        counts = [len(self.owned(p)) for p in range(self.n)]
        m = max(counts)
        w = counts.index(m) if counts.count(m) == 1 else None
        mad = w is not None and self.owner["Madagascar"] != w
        return dict(winner=w, turns=self.max_turns, timeout=True, leader5=leader5, lead=m, mad=mad, **self.stats)

# ---------------------------------------------------------------- ESPERIMENTI
def run(N):
    names = list(STRAT)
    print(f"Partite per combinazione: {N}  (3 giocatori, tetto {40} turni)\n")
    for en in ECON:
        print("=" * 70); print(f"ECONOMIA {en}"); print("=" * 70)
        # mescolate
        wins = defaultdict(int); played = defaultdict(int)
        turns, tos, snow, snow_n, hs, fs = [], 0, 0, 0, 0, 0
        for combo in itertools.combinations(names, 3):
            for _ in range(N):
                seats = list(combo); random.shuffle(seats)
                r = Game(seats, en).play()
                for s in seats: played[s] += 1
                if r["winner"] is not None: wins[seats[r["winner"]]] += 1
                turns.append(r["turns"]); tos += r["timeout"]
                hs += r["houses"]; fs += r["forts"]
                if r["leader5"] is not None and r["winner"] is not None:
                    snow_n += 1; snow += r["leader5"] == r["winner"]
        G = len(turns)
        print(f"Strategie mescolate ({G} partite):")
        for s in sorted(names, key=lambda s: -wins[s] / played[s]):
            print(f"  {s:11s} vince {100 * wins[s] / played[s]:5.1f}%   (atteso 33.3%)")
        print(f"  durata media {sum(turns) / G:.1f} turni | partite bloccate al tetto {100 * tos / G:.1f}%")
        print(f"  effetto valanga: chi guida al turno 5 vince il {100 * snow / max(1, snow_n):.0f}%")
        if hs or fs: print(f"  edifici medi a partita: casette {hs / G:.1f}, fortezze {fs / G:.1f}")
        # specchio
        print("Specchio (3 bot uguali): durata media / % bloccate al tetto")
        for s in names:
            rs = [Game([s] * 3, en).play() for _ in range(N)]
            to = [r for r in rs if r["timeout"]]
            extra = ""
            if to:
                extra = (f" | al tetto il leader ha in media {sum(r['lead'] for r in to) / len(to):.1f}/20,"
                         f" Madagascar non suo nel {100 * sum(r['mad'] for r in to) / len(to):.0f}%")
            print(f"  {s:11s} {sum(r['turns'] for r in rs) / N:5.1f} turni   bloccate {100 * len(to) / N:5.1f}%{extra}")
        print()

if __name__ == "__main__":
    random.seed(1)
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 200)
