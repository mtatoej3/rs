package it.regoleguerra.engine.model;

public record TerritoryId(String code) {
    public TerritoryId {
        if (code == null || code.isBlank()) throw new IllegalArgumentException("TerritoryId vuoto");
    }
}
