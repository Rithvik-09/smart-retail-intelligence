package com.smartretail.store.dto;

import com.smartretail.store.entity.Store;

public record StoreResponse(
    Long id,
    String name,
    String location
) {
    public static StoreResponse fromEntity(Store store) {
        return new StoreResponse(store.getId(), store.getName(), store.getLocation());
    }
}
