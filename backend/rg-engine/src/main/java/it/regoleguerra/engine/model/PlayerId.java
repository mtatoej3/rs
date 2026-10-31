package it.regoleguerra.engine.model;

public record PlayerId(String value) {
    public PlayerId {
        if (value == null || value.isBlank()) throw new IllegalArgumentException("PlayerId vuoto");
    }
}
