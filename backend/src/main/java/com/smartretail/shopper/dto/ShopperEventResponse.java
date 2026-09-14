package com.smartretail.shopper.dto;

import java.time.LocalDateTime;

public class ShopperEventResponse {

    private Long id;
    private Long storeId;
    private String cameraId;
    private LocalDateTime timestamp;
    private Integer peopleCount;
    private Integer zoneId;

    public ShopperEventResponse() {
    }

    public ShopperEventResponse(
            Long id,
            Long storeId,
            String cameraId,
            LocalDateTime timestamp,
            Integer peopleCount,
            Integer zoneId) {

        this.id = id;
        this.storeId = storeId;
        this.cameraId = cameraId;
        this.timestamp = timestamp;
        this.peopleCount = peopleCount;
        this.zoneId = zoneId;
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

    public Integer getPeopleCount() {
        return peopleCount;
    }

    public void setPeopleCount(Integer peopleCount) {
        this.peopleCount = peopleCount;
    }

    public Integer getZoneId() {
        return zoneId;
    }

    public void setZoneId(Integer zoneId) {
        this.zoneId = zoneId;
    }
}