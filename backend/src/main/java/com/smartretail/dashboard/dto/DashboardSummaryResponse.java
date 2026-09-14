package com.smartretail.dashboard.dto;

public class DashboardSummaryResponse {

    private Long storeId;

    private Integer currentPeopleCount;
    private Integer currentQueueLength;

    private Double averagePeopleCount;
    private Double averageQueueLength;

    private Double currentEstimatedWaitTime;
    private Double averageEstimatedWaitTime;

    private Integer activeAlerts;
    private Integer criticalAlerts;

    private Integer inventoryItems;
    private Integer stockoutRiskItems;

    public DashboardSummaryResponse() {
    }

    public DashboardSummaryResponse(
            Long storeId,
            Integer currentPeopleCount,
            Integer currentQueueLength,
            Double averagePeopleCount,
            Double averageQueueLength,
            Double currentEstimatedWaitTime,
            Double averageEstimatedWaitTime,
            Integer activeAlerts,
            Integer criticalAlerts,
            Integer inventoryItems,
            Integer stockoutRiskItems) {

        this.storeId = storeId;
        this.currentPeopleCount = currentPeopleCount;
        this.currentQueueLength = currentQueueLength;
        this.averagePeopleCount = averagePeopleCount;
        this.averageQueueLength = averageQueueLength;
        this.currentEstimatedWaitTime = currentEstimatedWaitTime;
        this.averageEstimatedWaitTime = averageEstimatedWaitTime;
        this.activeAlerts = activeAlerts;
        this.criticalAlerts = criticalAlerts;
        this.inventoryItems = inventoryItems;
        this.stockoutRiskItems = stockoutRiskItems;
    }

    public Long getStoreId() {
        return storeId;
    }

    public void setStoreId(Long storeId) {
        this.storeId = storeId;
    }

    public Integer getCurrentPeopleCount() {
        return currentPeopleCount;
    }

    public void setCurrentPeopleCount(Integer currentPeopleCount) {
        this.currentPeopleCount = currentPeopleCount;
    }

    public Integer getCurrentQueueLength() {
        return currentQueueLength;
    }

    public void setCurrentQueueLength(Integer currentQueueLength) {
        this.currentQueueLength = currentQueueLength;
    }

    public Double getAveragePeopleCount() {
        return averagePeopleCount;
    }

    public void setAveragePeopleCount(Double averagePeopleCount) {
        this.averagePeopleCount = averagePeopleCount;
    }

    public Double getAverageQueueLength() {
        return averageQueueLength;
    }

    public void setAverageQueueLength(Double averageQueueLength) {
        this.averageQueueLength = averageQueueLength;
    }

    public Double getCurrentEstimatedWaitTime() {
        return currentEstimatedWaitTime;
    }

    public void setCurrentEstimatedWaitTime(Double currentEstimatedWaitTime) {
        this.currentEstimatedWaitTime = currentEstimatedWaitTime;
    }

    public Double getAverageEstimatedWaitTime() {
        return averageEstimatedWaitTime;
    }

    public void setAverageEstimatedWaitTime(Double averageEstimatedWaitTime) {
        this.averageEstimatedWaitTime = averageEstimatedWaitTime;
    }

    public Integer getActiveAlerts() {
        return activeAlerts;
    }

    public void setActiveAlerts(Integer activeAlerts) {
        this.activeAlerts = activeAlerts;
    }

    public Integer getCriticalAlerts() {
        return criticalAlerts;
    }

    public void setCriticalAlerts(Integer criticalAlerts) {
        this.criticalAlerts = criticalAlerts;
    }

    public Integer getInventoryItems() {
        return inventoryItems;
    }

    public void setInventoryItems(Integer inventoryItems) {
        this.inventoryItems = inventoryItems;
    }

    public Integer getStockoutRiskItems() {
        return stockoutRiskItems;
    }

    public void setStockoutRiskItems(Integer stockoutRiskItems) {
        this.stockoutRiskItems = stockoutRiskItems;
    }
}