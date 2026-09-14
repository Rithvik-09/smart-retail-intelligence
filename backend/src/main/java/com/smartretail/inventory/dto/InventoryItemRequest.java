package com.smartretail.inventory.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;

public class InventoryItemRequest {

    @NotNull(message = "Store ID is required")
    private Long storeId;

    @NotBlank(message = "Product name is required")
    private String productName;

    @NotNull(message = "Current stock is required")
    @Min(value = 0, message = "Current stock cannot be negative")
    private Integer currentStock;

    @NotNull(message = "Reorder level is required")
    @Min(value = 0, message = "Reorder level cannot be negative")
    private Integer reorderLevel;

    @PositiveOrZero(message = "Predicted stockout risk cannot be negative")
    private Double predictedStockoutRisk;

    public InventoryItemRequest() {
    }

    public Long getStoreId() {
        return storeId;
    }

    public void setStoreId(Long storeId) {
        this.storeId = storeId;
    }

    public String getProductName() {
        return productName;
    }

    public void setProductName(String productName) {
        this.productName = productName;
    }

    public Integer getCurrentStock() {
        return currentStock;
    }

    public void setCurrentStock(Integer currentStock) {
        this.currentStock = currentStock;
    }

    public Integer getReorderLevel() {
        return reorderLevel;
    }

    public void setReorderLevel(Integer reorderLevel) {
        this.reorderLevel = reorderLevel;
    }

    public Double getPredictedStockoutRisk() {
        return predictedStockoutRisk;
    }

    public void setPredictedStockoutRisk(Double predictedStockoutRisk) {
        this.predictedStockoutRisk = predictedStockoutRisk;
    }
}