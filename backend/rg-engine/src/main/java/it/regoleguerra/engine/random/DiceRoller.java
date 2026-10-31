package it.regoleguerra.engine.random;

import java.util.List;

/** Unica fonte di casualità del motore (GDD 6.5, 6.6). */
public interface DiceRoller {

    /** Numero di Boom su {@code n} dadi (2 facce su 6, quindi 1/3 per dado). */
    int boomDice(int n);

    /** Dado a 6 facce (clausola 1.7). */
    int d6();

    /** Scelta casuale (es. territori non selezionabili, 1.1). */
    <T> T pick(List<T> items);
}
