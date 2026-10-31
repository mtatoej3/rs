"""Simulatore partite - GDD Regole di Guerra + economie + varianti di regole.
Uso:
  python sim.py [partite_per_combinazione]              -> v1: 4 economie, regole del GDD
  python sim.py varianti [partite_per_combinazione]     -> v2: varianti aerei/anfibio su E2 e E3
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
# territori raggiungibili con lo sfondamento anfibio (stesso mare)
SEAREACH = {t: set() for t in T}
for cs in SEAS.values():
    for a in cs:
        SEAREACH[a] |= set(cs) - {a}

# ---------------------------------------------------------------- REGOLE (varianti v2)
RULES = dict(duel=False,       # n.3 duello aereo per l'iniziativa
             airport=False,    # n.4 aerei solo con aeroporto (solo economie con edifici)
             noairconq=False,  # n.5 l'aereo da solo non conquista
             amphib=False,     # sfondamento anfibio: il difensore lancia sempre per primo (1 a testa se non ci sono le carte)
             cards=False,      # mazzo delle carte (v3)
             flag1=False,      # (b) la bandierina lancia 1 dado (fortezza 2)
             deck2=False,      # (d) SuperProd 6, Tradimento 12, mano = territori // 2
             atk_first=False,  # (a) a parità di aerei lancia per primo l'attaccante
             cap=0,            # limite di unità per territorio (0 = nessun limite)
             barracks=False,   # caserma: +50% del limite nel territorio, per ogni caserma
             win="all")        # (c) "all" dominio completo | "groups3" 3 gruppi colore su 4 | "t14" 14 territori su 20
AIRPORT_COST, AIRPORT_CAP = 300, 3
BARRACKS_COST = 300

# ---------------------------------------------------------------- CARTE (v3)
DECK = {"Scudo": 6, "Missili": 6, "Tradimento": 6, "Tregua": 6,
        "Siluro": 12, "SuperProd": 12, "ArmaSegreta": 12, "Anfibio": 6}
DISCARD_ORDER = ["Siluro", "Tregua", "Scudo", "SuperProd", "Missili", "Anfibio", "ArmaSegreta", "Tradimento"]
DECK2 = dict(DECK, SuperProd=6, Tradimento=12)
COMBAT_CARDS = ("Tradimento", "ArmaSegreta")

# ---------------------------------------------------------------- ECONOMIE
START_MONEY = 1630
PP_PRICE = 100
ECON = {
    "E0_soloPP":  dict(money=False, houses=False),
    "E1_soldiPP": dict(money=True, rent={g: 50 for g in "Blu Rosso Viola Verde".split()}, houses=False, fort=False, sets=False),
    "E2_edifici": dict(money=True, rent={g: 50 for g in "Blu Rosso Viola Verde".split()}, houses=True, fort=True, sets=False,
                       house_cost={g: 200 for g in "Blu Rosso Viola Verde".split()}, fort_cost=400),
    "E3_monopoly": dict(money=True, rent={"Blu": 30, "Viola": 40, "Rosso": 50, "Verde": 60}, houses=True, fort=False, sets=True,
                        house_cost={"Blu": 150, "Viola": 200, "Rosso": 250, "Verde": 300}),
}
MAX_HOUSES = 3

# ---------------------------------------------------------------- STRATEGIE
# ratio = probabilità minima di vittoria per lanciare un attacco
STRAT = {
    "Rusher":     dict(air=0.0,  keep=0.2, ratio=0.55, chain=True,  build=None,     place_def=0.2, max_ap=1,  traps=False),
    "Aviazione":  dict(air=0.7,  keep=0.3, ratio=0.55, chain=True,  build=None,     place_def=0.3, max_ap=99, traps=False),
    "Economista": dict(air=0.25, keep=0.6, ratio=0.70, chain=False, build="houses", place_def=0.6, max_ap=2,  traps=True),
    "Tartaruga":  dict(air=0.25, keep=1.0, ratio=0.85, chain=False, build="turtle", place_def=1.0, max_ap=2,  traps=True),
}
MIN_PLANES = 2
ECON_BUILD_UNTIL = 6  # l'Economista costruisce fino al turno 6, poi converte tutto

# ---------------------------------------------------------------- DADI / SCONTRI
P_BOOM = 1 / 3
def roll(n):
    return random.binomialvariate(n, P_BOOM) if n else 0

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

def initiative(att, dfn, both_attack=False):
    """True = l'attaccante lancia per primo; None = simultaneo (solo attacchi incrociati)"""
    if not RULES["duel"] or att[1] == 0 or dfn[1] == 0:
        if att[1] == dfn[1]: return None if both_attack else RULES["atk_first"]
        return att[1] > dfn[1]
    a, d = [0, att[1]], [0, dfn[1]]  # duello aereo: solo aerei, il difensore lancia per primo
    while size(a) and size(d):
        exchange(a, d, None if both_attack else False)
    att[1], dfn[1] = a[1], d[1]
    if att[1] == dfn[1]: return None if both_attack else RULES["atk_first"]
    return att[1] > dfn[1]

def step1_1v1(att, dfn, amph=False):
    if not size(dfn): return
    first = False if amph else initiative(att, dfn)  # iniziativa fissa nello step
    while size(att) and size(dfn):
        exchange(att, dfn, first)

def can_take(att):
    return att[0] > 0 if RULES["noairconq"] else size(att) > 0

def hit_by_flag(a, h):
    """se l'aereo non conquista, la bandierina elimina prima i carri"""
    if RULES["noairconq"]:
        k = min(h, a[0]); a[0] -= k; h -= k
        a[1] = max(0, a[1] - h)
    else:
        hit(a, h)

def flag_exchange(att, dice, amph=False):
    """un giro contro la bandierina; True se conquistata"""
    if (att[1] >= 1 or RULES["atk_first"]) and not amph:
        if roll(size(att)) and can_take(att): return True
        hit_by_flag(att, roll(dice))
    else:
        hit_by_flag(att, roll(dice))
        if can_take(att) and roll(size(att)): return True
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

def card_effect(card, user, enemy):
    """Arma Segreta: ogni Boom elimina un'unità nemica. Tradimento: la trasforma in una propria."""
    h = min(roll(size(enemy)), size(enemy))
    k = min(h, enemy[1]); enemy[1] -= k          # prima gli aerei
    enemy[0] -= h - k
    if card == "Tradimento":
        user[1] += k; user[0] += h - k

_WP = {}
def win_prob(at, ap, dt, dp, dice, amph=False):
    """probabilità stimata (Monte Carlo, in cache) che l'attaccante conquisti la regione"""
    if RULES["noairconq"] and at == 0: return 0.0
    if dice == 0: return 1.0 if at + ap else 0.0
    key = (min(at, 40), min(ap, 20), min(dt, 40), min(dp, 20), dice, amph)
    if key not in _WP:
        w = 0
        for _ in range(150):
            a, d = [key[0], key[1]], [key[2], key[3]]
            step1_1v1(a, d, amph)
            if size(d) == 0:
                while can_take(a):
                    if flag_exchange(a, dice, amph): w += 1; break
        _WP[key] = w / 150
    return _WP[key]

# ---------------------------------------------------------------- GIOCO
class Game:
    def __init__(self, strategies, econ_name, max_turns=40):
        self.n = len(strategies)
        self.strat = strategies
        self.E = ECON[econ_name]
        self.max_turns = max_turns
        self.turn = 0
        self.owner = {t: None for t in T}
        self.units = {t: [0, 0] for t in T}
        self.houses = {t: 0 for t in T}
        self.fort = {t: False for t in T}
        self.airport = {t: False for t in T}
        self.barracks = {t: 0 for t in T}
        self.card = [RULES["amphib"] and not RULES["cards"]] * self.n
        self.pp = [0] * self.n
        self.money = [START_MONEY if self.E["money"] else 0] * self.n
        self.stats = dict(houses=0, forts=0, battles=0, airports=0, amphib=0, planes_bought=0, units_bought=0,
                          missili_pp=0, superprod_pp=0, barracks=0, cap_lost=0, cap_refund=0, scudi=0, tregue=0, trap_fired=0, magic=0, card_kills=0)
        # carte
        deck = DECK2 if RULES["deck2"] else DECK
        self.deck = [c for c, k in deck.items() for _ in range(k)] if RULES["cards"] else []
        random.shuffle(self.deck)
        self.discard = []
        self.hand = [[] for _ in range(self.n)]
        self.traps = {}          # territorio -> carta (del proprietario del territorio)
        self.truce = set()       # coppie (p, q) in tregua per la Fase 3 in corso

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
    def cap(self, t):
        if not RULES["cap"]: return 10 ** 9
        return int(RULES["cap"] * (1 + 0.5 * self.barracks[t]))
    def room(self, t): return self.cap(t) - size(self.units[t])

    def flag_dice(self, t):
        if self.owner[t] is None: return 0
        return (1 if RULES["flag1"] else 2) + (1 if self.fort[t] else 0)

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
        if RULES["cards"]: self.cards_production()
        for p in range(self.n):
            if self.owned(p): self.spend(p, turn)
        if RULES["cards"]: self.place_traps()

    # ---------- carte
    def limit(self, p): return len(self.owned(p)) // (2 if RULES["deck2"] else 3)
    def held(self, p): return len(self.hand[p]) + sum(1 for t, c in self.traps.items() if self.owner[t] == p)
    def use(self, p, c):
        self.hand[p].remove(c); self.discard.append(c)

    def cards_production(self):
        alive = [p for p in range(self.n) if self.owned(p)]
        for p in alive:  # si completa la mano fino al limite; se si è oltre, si scarta
            while self.held(p) < self.limit(p):
                if not self.deck:
                    self.deck, self.discard = self.discard, []
                    random.shuffle(self.deck)
                    if not self.deck: break
                self.hand[p].append(self.deck.pop())
            while self.held(p) > self.limit(p):
                if self.hand[p]:
                    c = min(self.hand[p], key=DISCARD_ORDER.index); self.use(p, c)
                else:
                    t = next(t for t in self.traps if self.owner[t] == p)
                    self.discard.append(self.traps.pop(t))
        # Missili Balistici sul giocatore più grande; lo Scudo Spaziale li annulla
        for p in alive:
            while "Missili" in self.hand[p]:
                others = [q for q in alive if q != p]
                if not others: break
                q = max(others, key=lambda q: len(self.owned(q)))
                self.use(p, "Missili")
                if "Scudo" in self.hand[q]:
                    self.use(q, "Scudo"); self.stats["scudi"] += 1; continue
                h = min(roll(len(self.owned(q))), self.pp[q])
                self.pp[q] -= h; self.stats["missili_pp"] += h
        # Super Produzione
        for p in alive:
            while "SuperProd" in self.hand[p]:
                self.use(p, "SuperProd")
                h = roll(len(self.owned(p))); self.pp[p] += h; self.stats["superprod_pp"] += h

    def place_traps(self):
        """dopo lo showdown: chi gioca in difesa piazza Arma Segreta/Tradimento come trappole"""
        for p in range(self.n):
            if not STRAT[self.strat[p]]["traps"]: continue
            for c in [c for c in self.hand[p] if c in COMBAT_CARDS]:
                free = [t for t in self.frontier(p) if t not in self.traps]
                if not free: break
                t = max(free, key=lambda t: self.threat(t, p))
                if self.threat(t, p) == 0: break
                self.hand[p].remove(c); self.traps[t] = c

    def magic_card(self, p, enemy_size):
        """carta da giocare come magia, se conviene"""
        if not RULES["cards"] or enemy_size < 3: return None
        for c in COMBAT_CARDS:
            if c in self.hand[p]: return c
        return None

    def tregua(self):
        self.truce = set(); self.hostage = []
        for p in range(self.n):
            mine = self.owned(p)
            if "Tregua" not in self.hand[p] or not mine: continue
            press = defaultdict(int)  # quanto ogni avversario preme sul mio fronte
            for t in self.frontier(p):
                for n in LAND[t]:
                    if self.owner[n] not in (p, None): press[self.owner[n]] += self.units[n][0]
                for n in AIR[t]:
                    if self.owner[n] not in (p, None): press[self.owner[n]] += self.units[n][1]
            if not press: continue
            q = max(press, key=press.get)
            mydef = sum(size(self.units[t]) for t in self.frontier(p))
            if press[q] > mydef and (q, p) not in self.truce:
                src = max(mine, key=lambda t: size(self.units[t]))
                if not size(self.units[src]): continue
                u = [1, 0] if self.units[src][0] else [0, 1]  # l'unità in pegno sta sulla carta
                self.units[src][0] -= u[0]; self.units[src][1] -= u[1]
                self.hostage.append((p, src, u))
                self.use(p, "Tregua"); self.truce |= {(p, q), (q, p)}; self.stats["tregue"] += 1

    def end_tregua(self):
        for p, src, u in getattr(self, "hostage", []):
            dst = src if self.owner[src] == p else next(iter(self.owned(p)), None)
            if dst: self.units[dst][0] += u[0]; self.units[dst][1] += u[1]
        self.truce = set(); self.hostage = []

    def spend(self, p, turn):
        S, E = STRAT[self.strat[p]], self.E
        mine = self.owned(p)
        have = sum(self.units[t][1] for t in mine)
        air_rule = RULES["airport"] and E["houses"]
        if air_rule:  # aeroporti: costruiti finché servono per gli aerei che il bot vuole
            want = max(MIN_PLANES, have + int((self.pp[p] + self.money[p] // PP_PRICE) * S["air"] / 2) + 1)
            while sum(self.airport[t] for t in mine) < S["max_ap"] \
                    and AIRPORT_CAP * sum(self.airport[t] for t in mine) < want and self.money[p] >= AIRPORT_COST:
                free = [t for t in mine if not self.airport[t]]
                if not free: break
                t = min(free, key=lambda t: self.threat(t, p))
                self.airport[t] = True; self.money[p] -= AIRPORT_COST; self.stats["airports"] += 1
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
            if RULES["cap"] and RULES["barracks"] and E["houses"]:
                while self.money[p] >= BARRACKS_COST:
                    units = self.pp[p] + (self.money[p] - BARRACKS_COST) // PP_PRICE
                    front = self.frontier(p) or mine
                    if sum(max(0, self.room(t)) for t in front) >= units: break
                    t = min(front, key=lambda t: (self.room(t), -self.threat(t, p)))
                    self.barracks[t] += 1; self.money[p] -= BARRACKS_COST; self.stats["barracks"] += 1
            self.pp[p] += self.money[p] // PP_PRICE
            self.money[p] %= PP_PRICE
        # acquisto unità
        pp = self.pp[p]
        planes = int(pp * S["air"] / 2 + random.random())
        if have + planes < MIN_PLANES:  # serve almeno qualche aereo
            planes = min(pp // 2, MIN_PLANES - have)
        bases = None
        if air_rule:
            cap = AIRPORT_CAP * sum(self.airport[t] for t in mine) - have
            planes = max(0, min(planes, cap))
            bases = [t for t in mine if self.airport[t]]
        tanks = pp - 2 * planes
        self.pp[p] = 0
        self.stats["planes_bought"] += planes; self.stats["units_bought"] += planes + tanks
        new = [[1, 0]] * tanks + [[0, 1]] * planes
        random.shuffle(new)
        # piazzamento: prima la difesa del fronte, poi tutto sulla base d'attacco
        front = self.frontier(p) or mine
        need = {t: max(0, S["place_def"] * self.threat(t, p) - size(self.units[t])) for t in front}
        best = min(((self.def_eq(e), s) for s in front for e in LAND[s] | AIR[s] if self.owner[e] != p),
                   default=(0, random.choice(front)))[1]
        for u in new:
            if u[1] and bases:  # gli aerei nascono solo negli aeroporti
                ok_b = [t for t in bases if self.room(t) > 0]
                if ok_b:
                    tgt = max(ok_b, key=lambda t: self.threat(t, p))
                    self.units[tgt][1] += 1; continue
                u = [1, 0]; self.pp[p] += 1  # niente spazio per l'aereo: carro al suo posto, 1 PP resta
            tgt = max(need, key=need.get) if need and max(need.values()) >= 1 else best
            if self.room(tgt) <= 0:
                free = [t for t in mine if self.room(t) > 0]
                if not free:  # nessuno spazio: le unità non si comprano, i PP restano
                    self.pp[p] += 2 if u[1] else 1; self.stats["cap_refund"] += 1; continue
                tgt = max(free, key=lambda t: (t in front, self.threat(t, p)))
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
        peace = lambda e: (p, self.owner[e]) in self.truce
        targets = sorted({e for t in mine for e in LAND[t] | AIR[t] if self.owner[e] != p and not peace(e)},
                         key=self.def_eq)
        magic = [c for c in self.hand[p] if c in COMBAT_CARDS]
        for tg in targets:
            d = self.units[tg]
            dice = self.flag_dice(tg)
            card = magic[0] if magic and size(d) >= 3 else None
            if card:  # con la carta in mano il bot stima i difensori ridotti di un terzo
                d = [d[0] - round(d[0] / 3), d[1] - round(d[1] / 3)]
            if tg in self.traps: d = self.units[tg][:]  # una trappola nemica è possibile: prudenza
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
                if card: magic.remove(card)
                orders.append(dict(p=p, parts=[(s, t) for s, t in parts if size(t)], steps=[tg] + chain, magic=card))
                targeted.add(tg)
        # carta sfondamento anfibio: carri da una costa verso un territorio sullo stesso mare
        if self.card[p] or "Anfibio" in self.hand[p]:
            best_o = None
            for tg in T:
                if self.owner[tg] == p or tg in targeted or peace(tg): continue
                if tg != "Madagascar" and self.turn < 8: continue  # i primi turni la tiene per il Madagascar
                srcs = [s for s in mine if tg in SEAREACH[s] and tg not in LAND[s] and avail[s][0]]
                if not srcs: continue
                s = max(srcs, key=lambda s: avail[s][0])
                at = avail[s][0]
                d = self.units[tg]
                pr = win_prob(at, 0, d[0], d[1], self.flag_dice(tg), amph=True)
                if pr >= S["ratio"]:
                    sc = pr + (1 if tg == "Madagascar" else 0)
                    if best_o is None or sc > best_o[0]: best_o = (sc, s, tg, at)
            if best_o:
                _, s, tg, at = best_o
                avail[s][0] -= at
                orders.append(dict(p=p, parts=[(s, [at, 0])], steps=[tg], amph=True))
                if self.card[p]: self.card[p] = False
                else: self.use(p, "Anfibio")
                self.stats["amphib"] += 1
        # movimenti interni: dalle retrovie verso il fronte (1 spostamento)
        front = set(self.frontier(p))
        moves = []
        incoming = defaultdict(int)
        for t in mine:
            if t in front or size(avail[t]) == 0: continue
            dst = [n for n in LAND[t] if self.owner[n] == p]
            if dst:
                d = min(dst, key=lambda n: 0 if n in front else 1)
                r = self.room(d) - incoming[d]
                if r <= 0: continue
                a = avail[t][:]
                k = max(0, size(a) - r); kt = min(k, a[0]); a[0] -= kt; a[1] -= k - kt
                incoming[d] += size(a)
                moves.append((t, d, a)); avail[t][0] -= a[0]; avail[t][1] -= a[1]
        return orders, moves

    def movement(self):
        if RULES["cards"]: self.tregua()
        self._movement()
        if RULES["cards"]: self.end_tregua()
        if RULES["cap"]: self.enforce_cap()

    def enforce_cap(self):
        """a fine fase l'eccesso va nei territori vicini con spazio, altrimenti è perso"""
        for t in T:
            p = self.owner[t]
            while p is not None and self.room(t) < 0:
                u = [1, 0] if self.units[t][0] else [0, 1]
                self.units[t][0] -= u[0]; self.units[t][1] -= u[1]
                near = [n for n in (LAND[t] if u[0] else AIR[t]) if self.owner[n] == p and self.room(n) > 0]
                if near:
                    n = max(near, key=lambda n: self.room(n))
                    self.units[n][0] += u[0]; self.units[n][1] += u[1]
                else:
                    self.stats["cap_lost"] += 1

    def _movement(self):
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
            live.append(dict(p=o["p"], army=army, steps=o["steps"], srcs={s for s, _ in o["parts"]}, i=0,
                             amph=o.get("amph", False), magic=o.get("magic")))
        wave = 0
        while live:
            groups = defaultdict(lambda: dict(army=[0, 0], srcs=set(), conts=[], amph=False, magic=None))
            for o in live:
                tg = o["steps"][o["i"]]
                g = groups[(o["p"], tg)]
                g["army"][0] += o["army"][0]; g["army"][1] += o["army"][1]
                g["srcs"] |= o["srcs"]
                if o["amph"]: g["amph"] = True
                if o.get("magic"): g["magic"] = o["magic"]
                if o["i"] + 1 < len(o["steps"]): g["conts"].append(o["steps"][o["i"] + 1])
            # attacchi incrociati
            keys = list(groups)
            for (p, tg) in keys:
                for (q, tg2) in keys:
                    if p < q and tg2 in groups[(p, tg)]["srcs"] and tg in groups[(q, tg2)]["srcs"] \
                            and self.owner[tg] == q and self.owner[tg2] == p:
                        a, b = groups[(p, tg)]["army"], groups[(q, tg2)]["army"]
                        first = initiative(a, b, both_attack=True)
                        while size(a) and size(b): exchange(a, b, first)
            by_target = defaultdict(list)
            for (p, tg), g in groups.items():
                if size(g["army"]): by_target[tg].append((p, g))
            nxt = []
            for tg, lst in by_target.items():
                self.stats["battles"] += 1
                winner = self.resolve(tg, [(p, g["army"]) for p, g in lst],
                                      amph=len(lst) == 1 and lst[0][1]["amph"],
                                      info={p: g for p, g in lst})
                for p, g in lst:
                    a = g["army"]
                    if size(a) and p != self.owner[tg]:
                        # sopravvissuti che non hanno potuto conquistare (aerei senza carri): rientrano
                        home = [s for s in g["srcs"] if self.owner[s] == p]
                        if home: self.units[home[0]][0] += a[0]; self.units[home[0]][1] += a[1]
                        a[0] = a[1] = 0
                    if p == winner and g["conts"] and size(self.units[tg]) > 1:
                        a = self.units[tg]
                        go = [a[0] - 1 if a[0] else 0, a[1] if a[0] else a[1] - 1]
                        a[0] -= go[0]; a[1] -= go[1]
                        nxt.append(dict(p=p, army=go, steps=[g["conts"][0]], srcs={tg}, i=0, amph=False))
            live = nxt; wave += 1

    def fire_traps(self, tg, own, act, info, used):
        """le trappole scattano prima di tutto, anche prima della superiorità aerea"""
        dfn = self.units[tg]
        if tg in self.traps and self.owner[tg] == own and act:
            c = self.traps.pop(tg); self.discard.append(c)
            p, a = max(act, key=lambda x: size(x[1]))
            before = size(a); card_effect(c, dfn, a)
            self.stats["trap_fired"] += 1; self.stats["card_kills"] += before - size(a); used.add(own)
        for p, a in act:
            for s in info.get(p, {}).get("srcs", ()):
                if s in self.traps and self.owner[s] == p and p not in used:
                    c = self.traps.pop(s); self.discard.append(c)
                    before = size(dfn); card_effect(c, a, dfn)
                    self.stats["trap_fired"] += 1; self.stats["card_kills"] += before - size(dfn); used.add(p)

    def play_magic(self, p, user, enemy, used, reserved=None):
        if p in used or not size(enemy): return
        c = reserved if reserved in self.hand[p] else self.magic_card(p, size(enemy))
        if not c: return
        self.use(p, c); used.add(p)
        before = size(enemy); card_effect(c, user, enemy)
        self.stats["magic"] += 1; self.stats["card_kills"] += before - size(enemy)

    def battle_1v1_cards(self, p, att, own, dfn, amph, used, reserved):
        """step 1 con le carte magia: chi ha l'iniziativa lancia per primo, la carta precede il lancio"""
        first = False if amph else initiative(att, dfn)
        sides = [(p, att, dfn, reserved), (own, dfn, att, None)]
        if not first: sides.reverse()
        for q, me, en, res in sides:
            if not (size(att) and size(dfn)): break
            self.play_magic(q, me, en, used, res)
            if size(me) and size(en): hit(en, roll(size(me)))
        while size(att) and size(dfn):
            exchange(att, dfn, first)

    def resolve(self, tg, atts, amph=False, info=None):
        """atts: lista (player, army). Ritorna il proprietario finale."""
        info = info or {}
        used = set()  # al massimo una carta per giocatore per scontro
        while True:
            own = self.owner[tg]
            for p, a in atts:  # rinforzi propri che arrivano dalle catene
                if p == own and size(a):
                    self.units[tg][0] += a[0]; self.units[tg][1] += a[1]; a[0] = a[1] = 0
            act = [(p, a) for p, a in atts if size(a) and p != own]
            if not act: return own
            act.sort(key=lambda x: -x[1][1] + random.random() * 0.1)
            if own is None:
                takers = [(p, a) for p, a in act if can_take(a)]
                if not takers: return own
                p, a = takers[0]
                self.conquer(tg, p, a); amph = False; continue
            dfn = self.units[tg]
            if RULES["cards"]:
                self.fire_traps(tg, own, act, info, used)
                act = [(p, a) for p, a in act if size(a)]
                if not act: return own
            if len(act) == 1 and RULES["cards"] and size(dfn):
                p, a = act[0]
                self.battle_1v1_cards(p, a, own, dfn, amph, used, info.get(p, {}).get("magic"))
            elif len(act) == 1:
                if RULES["cards"]:  # solo bandierina: il difensore può usare la carta prima del suo lancio
                    self.play_magic(own, dfn, act[0][1], used)
                step1_1v1(act[0][1], dfn, amph)
            else:
                while size(dfn) and sum(size(a) for _, a in act) > 0:
                    alive = [(p, a) for p, a in act if size(a)]
                    if len(alive) == 1:
                        step1_1v1(alive[0][1], dfn); break
                    alive.sort(key=lambda x: -x[1][1])
                    parts = split_def(dfn, [a for _, a in alive])
                    for (p, a), d in zip(alive, parts):
                        if size(d) == 0: continue
                        exchange(a, d, initiative(a, d))
                    dfn[0] = sum(d[0] for d in parts); dfn[1] = sum(d[1] for d in parts)
            if size(dfn): continue  # attaccanti eliminati
            # step 2: assalto alla bandierina
            dice = self.flag_dice(tg)
            took = None
            while took is None:
                alive = sorted([(p, a) for p, a in act if can_take(a)], key=lambda x: -x[1][1])
                if not alive: break
                for p, a in alive:
                    if flag_exchange(a, dice, amph): took = (p, a); break
            if not took: return own
            self.conquer(tg, *took); amph = False

    def conquer(self, tg, p, a):
        self.owner[tg] = p
        self.units[tg] = [a[0], a[1]]
        a[0] = a[1] = 0
        if self.houses[tg]: self.houses[tg] -= 1  # saccheggio; fortezza e aeroporto passano al conquistatore

    # ---------- partita
    def victory(self, counts):
        for p in range(self.n):
            if RULES["win"] == "all" and counts[p] == len(T): return p
            if RULES["win"] == "t14" and counts[p] >= 14: return p
            if RULES["win"] == "groups3":
                full = sum(all(self.owner[t] == p for t in T if GROUP[t] == g) for g in ("Blu", "Rosso", "Viola", "Verde"))
                if full >= 3: return p
        return None

    def play(self):
        self.phase1()
        leader5 = None
        for turn in range(1, self.max_turns + 1):
            self.turn = turn
            self.production(turn)
            self.movement()
            counts = [len(self.owned(p)) for p in range(self.n)]
            if turn == 5:
                m = max(counts)
                leader5 = counts.index(m) if counts.count(m) == 1 else None
            w = self.victory(counts)
            if w is not None:
                return dict(winner=w, turns=turn, timeout=False, leader5=leader5, **self.stats)
        counts = [len(self.owned(p)) for p in range(self.n)]
        m = max(counts)
        w = counts.index(m) if counts.count(m) == 1 else None
        mad = w is not None and self.owner["Madagascar"] != w
        return dict(winner=w, turns=self.max_turns, timeout=True, leader5=leader5, lead=m, mad=mad, **self.stats)

# ---------------------------------------------------------------- ESPERIMENTI
def batch(en, N):
    """partite mescolate (4 combinazioni di 3 strategie) + specchio"""
    names = list(STRAT)
    wins = defaultdict(int); played = defaultdict(int); real = defaultdict(int)
    rs_all = []
    for combo in itertools.combinations(names, 3):
        for _ in range(N):
            seats = list(combo); random.shuffle(seats)
            r = Game(seats, en).play()
            for s in seats: played[s] += 1
            if r["winner"] is not None:
                wins[seats[r["winner"]]] += 1
                if not r["timeout"]: real[seats[r["winner"]]] += 1
            rs_all.append(r)
    mirror = {s: [Game([s] * 3, en).play() for _ in range(N)] for s in names}
    return dict(wins=wins, played=played, real=real, rs=rs_all, mirror=mirror)

def report(B, label):
    names = list(STRAT)
    rs = B["rs"]; G = len(rs)
    to = [r for r in rs if r["timeout"]]
    snow = [r for r in rs if r["leader5"] is not None and r["winner"] is not None]
    print(f"--- {label}  ({G} partite mescolate)")
    for s in sorted(names, key=lambda s: -B["wins"][s] / B["played"][s]):
        print(f"  {s:11s} vince {100 * B['wins'][s] / B['played'][s]:5.1f}%"
              f"  (di cui vittoria vera prima del tetto {100 * B['real'][s] / B['played'][s]:5.1f}%)")
    print(f"  durata media {sum(r['turns'] for r in rs) / G:.1f} turni | bloccate al tetto {100 * len(to) / G:.1f}%"
          f" | valanga (leader al turno 5 vince) {100 * sum(r['leader5'] == r['winner'] for r in snow) / max(1, len(snow)):.0f}%")
    if to:
        print(f"  partite bloccate: leader medio {sum(r['lead'] for r in to) / len(to):.1f}/20,"
              f" Madagascar non suo nel {100 * sum(r['mad'] for r in to) / len(to):.0f}%")
    ub = sum(r["units_bought"] for r in rs) or 1
    print(f"  aerei sul totale unità comprate {100 * sum(r['planes_bought'] for r in rs) / ub:.0f}%"
          f" | aeroporti/partita {sum(r['airports'] for r in rs) / G:.1f}"
          f" | carte anfibie usate/partita {sum(r['amphib'] for r in rs) / G:.1f}"
          f" | casette {sum(r['houses'] for r in rs) / G:.1f} fortezze {sum(r['forts'] for r in rs) / G:.1f}")
    if RULES["cards"]:
        k = lambda x: sum(r[x] for r in rs) / G
        print(f"  carte/partita: missili -{k('missili_pp'):.1f} PP, scudi {k('scudi'):.1f}, superprod +{k('superprod_pp'):.1f} PP,"
              f" tregue {k('tregue'):.1f}, trappole scattate {k('trap_fired'):.1f}, magie {k('magic'):.1f},"
              f" unità eliminate/rubate dalle carte {k('card_kills'):.1f}")
    if RULES["cap"]:
        k = lambda x: sum(r[x] for r in rs) / G
        print(f"  limite unità: caserme/partita {k('barracks'):.1f}, unità perse per eccesso {k('cap_lost'):.1f},"
              f" acquisti bloccati per mancanza di spazio {k('cap_refund'):.1f}")
    line = []
    for s in names:
        m = B["mirror"][s]
        line.append(f"{s} {100 * sum(r['timeout'] for r in m) / len(m):.0f}%")
    print("  specchio, bloccate al tetto: " + " | ".join(line))

def run_v1(N):
    print(f"Partite per combinazione: {N}  (3 giocatori, tetto 40 turni)\n")
    for en in ECON:
        report(batch(en, N), en)
        print()

VARIANTS = [
    ("A base (regole GDD)",                       dict()),
    ("B duello aereo",                            dict(duel=True)),
    ("C aeroporti",                               dict(airport=True)),
    ("D aereo non conquista + carta anfibia",     dict(noairconq=True, amphib=True)),
    ("E tutto: duello + aeroporti + D",           dict(duel=True, airport=True, noairconq=True, amphib=True)),
    ("F base + carte",                            dict(cards=True)),
    ("G tutto (E) + carte",                       dict(duel=True, airport=True, noairconq=True, amphib=True, cards=True)),
    ("H G + b bandierina 1 dado",                 dict(duel=True, airport=True, noairconq=True, amphib=True, cards=True, flag1=True)),
    ("I G + c vittoria 3 gruppi su 4",            dict(duel=True, airport=True, noairconq=True, amphib=True, cards=True, win="groups3")),
    ("J G + d mazzo e mano",                      dict(duel=True, airport=True, noairconq=True, amphib=True, cards=True, deck2=True)),
    ("K G + b + c(3 gruppi) + d",                 dict(duel=True, airport=True, noairconq=True, amphib=True, cards=True, flag1=True, win="groups3", deck2=True)),
    ("L G + b + c(14 territori) + d",             dict(duel=True, airport=True, noairconq=True, amphib=True, cards=True, flag1=True, win="t14", deck2=True)),
    ("M L + a attaccante primo a parità",         dict(duel=True, airport=True, noairconq=True, amphib=True, cards=True, flag1=True, win="t14", deck2=True, atk_first=True)),
    ("N L + a + limite 10 + caserma",             dict(duel=True, airport=True, noairconq=True, amphib=True, cards=True, flag1=True, win="t14", deck2=True, atk_first=True, cap=10, barracks=True)),
    ("O L + a + limite 6 + caserma",              dict(duel=True, airport=True, noairconq=True, amphib=True, cards=True, flag1=True, win="t14", deck2=True, atk_first=True, cap=6, barracks=True)),
    ("P L + a + limite 15 + caserma",              dict(duel=True, airport=True, noairconq=True, amphib=True, cards=True, flag1=True, win="t14", deck2=True, atk_first=True, cap=15, barracks=True)),
    ("Q L + a + limite 20 + caserma",              dict(duel=True, airport=True, noairconq=True, amphib=True, cards=True, flag1=True, win="t14", deck2=True, atk_first=True, cap=20, barracks=True)),
]

def run_v2(N, only=None):
    for name, rules in VARIANTS:
        if only and not name.startswith(only): continue
        for k in RULES: RULES[k] = rules.get(k, False)
        _WP.clear()
        print("=" * 78); print(f"VARIANTE {name}"); print("=" * 78)
        for en in ["E2_edifici", "E3_monopoly"]:
            report(batch(en, N), en)
        print(flush=True)

if __name__ == "__main__":
    random.seed(1)
    if len(sys.argv) > 1 and sys.argv[1] == "varianti":
        N = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        run_v2(N, sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        run_v1(int(sys.argv[1]) if len(sys.argv) > 1 else 200)
