package com.smartretail.store.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreateStoreRequest(
    @NotBlank(message = "Store name is required")
    @Size(max = 100, message = "Store name must not exceed 100 characters")
    String name,

    @NotBlank(message = "Store location is required")
    @Size(max = 255, message = "Store location must not exceed 255 characters")
    String location
) {
}
