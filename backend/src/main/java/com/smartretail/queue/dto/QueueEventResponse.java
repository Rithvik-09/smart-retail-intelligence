package com.smartretail.queue.dto;

import java.time.LocalDateTime;

public class QueueEventResponse {

    private Long id;
    private Long storeId;
    private String cameraId;
    private LocalDateTime timestamp;
    private Integer queueLength;
    private Double estimatedWaitTime;
    private Integer checkoutCounterId;

    public QueueEventResponse() {
    }

    public QueueEventResponse(
            Long id,
            Long storeId,
            String cameraId,
            LocalDateTime timestamp,
            Integer queueLength,
            Double estimatedWaitTime,
            Integer checkoutCounterId) {

        this.id = id;
        this.storeId = storeId;
        this.cameraId = cameraId;
        this.timestamp = timestamp;
        this.queueLength = queueLength;
        this.estimatedWaitTime = estimatedWaitTime;
        this.checkoutCounterId = checkoutCounterId;
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

    public String getCameraId() {
        return cameraId;
    }

    public void setCameraId(String cameraId) {
        this.cameraId = cameraId;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public Integer getQueueLength() {
        return queueLength;
    }

    public void setQueueLength(Integer queueLength) {
        this.queueLength = queueLength;
    }

    public Double getEstimatedWaitTime() {
        return estimatedWaitTime;
    }

    public void setEstimatedWaitTime(Double estimatedWaitTime) {
        this.estimatedWaitTime = estimatedWaitTime;
    }

    public Integer getCheckoutCounterId() {
        return checkoutCounterId;
    }

    public void setCheckoutCounterId(Integer checkoutCounterId) {
        this.checkoutCounterId = checkoutCounterId;
    }
}