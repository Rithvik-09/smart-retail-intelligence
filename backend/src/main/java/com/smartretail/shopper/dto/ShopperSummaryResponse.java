package com.smartretail.shopper.dto;

public class ShopperSummaryResponse {

    private Long storeId;
    private Integer currentPeopleCount;
    private Double averagePeopleCount;
    private Integer maximumPeopleCount;

    public ShopperSummaryResponse() {
    }

    public ShopperSummaryResponse(
            Long storeId,
            Integer currentPeopleCount,
            Double averagePeopleCount,
            Integer maximumPeopleCount) {

        this.storeId = storeId;
        this.currentPeopleCount = currentPeopleCount;
        this.averagePeopleCount = averagePeopleCount;
        this.maximumPeopleCount = maximumPeopleCount;
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

    public Double getAveragePeopleCount() {
        return averagePeopleCount;
    }

    public void setAveragePeopleCount(Double averagePeopleCount) {
        this.averagePeopleCount = averagePeopleCount;
    }

    public Integer getMaximumPeopleCount() {
        return maximumPeopleCount;
    }

    public void setMaximumPeopleCount(Integer maximumPeopleCount) {
        this.maximumPeopleCount = maximumPeopleCount;
    }
}