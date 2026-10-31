package it.regoleguerra.engine.random;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class SeededDiceRollerTest {

    @Test
    void stessoSemeStessaSequenza() {
        var a = new SeededDiceRoller(42);
        var b = new SeededDiceRoller(42);
        for (int i = 0; i < 100; i++) {
            assertThat(a.boomDice(8)).isEqualTo(b.boomDice(8));
            assertThat(a.d6()).isEqualTo(b.d6());
        }
    }

    @Test
    void boomHaProbabilitaUnTerzo() {
        var dice = new SeededDiceRoller(7);
        int n = 300_000;
        double freq = (double) dice.boomDice(n) / n;
        assertThat(freq).isBetween(0.32, 0.345);
    }

    @Test
    void d6RestaTra1E6() {
        var dice = new SeededDiceRoller(1);
        for (int i = 0; i < 1000; i++) assertThat(dice.d6()).isBetween(1, 6);
    }
}
