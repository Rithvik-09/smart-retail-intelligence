package com.smartretail.queue.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDateTime;

public class QueueEventRequest {

    @NotNull(message = "Store ID is required")
    private Long storeId;

    @NotBlank(message = "Camera ID is required")
    private String cameraId;

    @NotNull(message = "Timestamp is required")
    private LocalDateTime timestamp;

    @NotNull(message = "Queue length is required")
    @Min(value = 0, message = "Queue length cannot be negative")
    private Integer queueLength;

    @NotNull(message = "Estimated wait time is required")
    @Min(value = 0, message = "Estimated wait time cannot be negative")
    private Double estimatedWaitTime;

    private Integer checkoutCounterId;

    public QueueEventRequest() {
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