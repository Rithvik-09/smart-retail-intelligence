package com.smartretail.inventory.dto;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class InventoryRiskRequest {

    @NotNull(message = "Product ID is required")
    private Long productId;
    private Long storeId;

    public Long getStoreId() {
        return storeId;
    }

    public void setStoreId(Long storeId) {
        this.storeId = storeId;
    }

    @NotNull(message = "Stockout probability is required")
    @DecimalMin(value = "0.0", message = "Stockout probability cannot be less than 0")
    @DecimalMax(value = "1.0", message = "Stockout probability cannot be greater than 1")
    private Double stockoutProbability;

    @NotBlank(message = "Risk level is required")
    private String riskLevel;

    @NotNull(message = "Anomaly status is required")
    private Boolean anomaly;

    @NotBlank(message = "Recommended action is required")
    private String recommendedAction;

    public InventoryRiskRequest() {
    }

    public Long getProductId() {
        return productId;
    }

    public void setProductId(Long productId) {
        this.productId = productId;
    }

    public Double getStockoutProbability() {
        return stockoutProbability;
    }

    public void setStockoutProbability(Double stockoutProbability) {
        this.stockoutProbability = stockoutProbability;
    }

    public String getRiskLevel() {
        return riskLevel;
    }

    public void setRiskLevel(String riskLevel) {
        this.riskLevel = riskLevel;
    }

    public Boolean getAnomaly() {
        return anomaly;
    }

    public void setAnomaly(Boolean anomaly) {
        this.anomaly = anomaly;
    }

    public String getRecommendedAction() {
        return recommendedAction;
    }

    public void setRecommendedAction(String recommendedAction) {
        this.recommendedAction = recommendedAction;
    }
}