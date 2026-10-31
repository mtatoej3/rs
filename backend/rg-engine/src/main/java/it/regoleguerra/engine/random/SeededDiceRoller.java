package it.regoleguerra.engine.random;

import java.util.List;
import java.util.SplittableRandom;

/** Implementazione deterministica: stesso seme, stessa sequenza (GDD 6.6). */
public final class SeededDiceRoller implements DiceRoller {

    private final SplittableRandom rng;

    public SeededDiceRoller(long seed) {
        this.rng = new SplittableRandom(seed);
    }

    @Override
    public int boomDice(int n) {
        if (n < 0) throw new IllegalArgumentException("n < 0");
        int booms = 0;
        for (int i = 0; i < n; i++) {
            if (rng.nextInt(6) < 2) booms++;
        }
        return booms;
    }

    @Override
    public int d6() {
        return rng.nextInt(6) + 1;
    }

    @Override
    public <T> T pick(List<T> items) {
        if (items.isEmpty()) throw new IllegalArgumentException("lista vuota");
        return items.get(rng.nextInt(items.size()));
    }
}
