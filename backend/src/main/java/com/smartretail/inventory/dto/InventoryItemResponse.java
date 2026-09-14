package com.smartretail.inventory.dto;

public class InventoryItemResponse {

    private Long id;
    private Long storeId;
    private String productName;
    private Integer currentStock;
    private Integer reorderLevel;
    private Double predictedStockoutRisk;

    public InventoryItemResponse() {
    }

    public InventoryItemResponse(
            Long id,
            Long storeId,
            String productName,
            Integer currentStock,
            Integer reorderLevel,
            Double predictedStockoutRisk) {

        this.id = id;
        this.storeId = storeId;
        this.productName = productName;
        this.currentStock = currentStock;
        this.reorderLevel = reorderLevel;
        this.predictedStockoutRisk = predictedStockoutRisk;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
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