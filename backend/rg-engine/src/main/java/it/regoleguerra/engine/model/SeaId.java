package it.regoleguerra.engine.model;

public record SeaId(String code) {
    public SeaId {
        if (code == null || code.isBlank()) throw new IllegalArgumentException("SeaId vuoto");
    }
}
