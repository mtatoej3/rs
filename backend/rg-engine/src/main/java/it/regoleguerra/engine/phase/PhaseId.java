package it.regoleguerra.engine.phase;

/** Stati della partita (GDD 6.3). */
public enum PhaseId {
    LOBBY,
    SETUP_PICKING,
    SETUP_CONTESTS,
    SETUP_REPOSITION,
    SETUP_RESOLVE,
    PRODUCTION_ORDERS,
    PRODUCTION_SHOWDOWN,
    MOVEMENT_ORDERS,
    MOVEMENT_SHOWDOWN,
    RESOLUTION,
    FINISHED
}
