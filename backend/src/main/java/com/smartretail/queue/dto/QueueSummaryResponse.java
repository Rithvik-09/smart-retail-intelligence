package com.smartretail.queue.dto;

public class QueueSummaryResponse {

    private Long storeId;
    private Integer currentQueueLength;
    private Double averageQueueLength;
    private Integer maximumQueueLength;
    private Double currentEstimatedWaitTime;
    private Double averageEstimatedWaitTime;
    private Double maximumEstimatedWaitTime;

    public QueueSummaryResponse() {
    }

    public QueueSummaryResponse(
            Long storeId,
            Integer currentQueueLength,
            Double averageQueueLength,
            Integer maximumQueueLength,
            Double currentEstimatedWaitTime,
            Double averageEstimatedWaitTime,
            Double maximumEstimatedWaitTime) {

        this.storeId = storeId;
        this.currentQueueLength = currentQueueLength;
        this.averageQueueLength = averageQueueLength;
        this.maximumQueueLength = maximumQueueLength;
        this.currentEstimatedWaitTime = currentEstimatedWaitTime;
        this.averageEstimatedWaitTime = averageEstimatedWaitTime;
        this.maximumEstimatedWaitTime = maximumEstimatedWaitTime;
    }

    public Long getStoreId() {
        return storeId;
    }

    public void setStoreId(Long storeId) {
        this.storeId = storeId;
    }

    public Integer getCurrentQueueLength() {
        return currentQueueLength;
    }

    public void setCurrentQueueLength(Integer currentQueueLength) {
        this.currentQueueLength = currentQueueLength;
    }

    public Double getAverageQueueLength() {
        return averageQueueLength;
    }

    public void setAverageQueueLength(Double averageQueueLength) {
        this.averageQueueLength = averageQueueLength;
    }

    public Integer getMaximumQueueLength() {
        return maximumQueueLength;
    }

    public void setMaximumQueueLength(Integer maximumQueueLength) {
        this.maximumQueueLength = maximumQueueLength;
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

    public Double getMaximumEstimatedWaitTime() {
        return maximumEstimatedWaitTime;
    }

    public void setMaximumEstimatedWaitTime(Double maximumEstimatedWaitTime) {
        this.maximumEstimatedWaitTime = maximumEstimatedWaitTime;
    }
}
