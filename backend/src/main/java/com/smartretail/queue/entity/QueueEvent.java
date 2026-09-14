package com.smartretail.queue.entity;

import com.smartretail.store.entity.Store;
import jakarta.persistence.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "queue_events")
public class QueueEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "store_id", nullable = false)
    private Store store;

    @Column(nullable = false)
    private String cameraId;

    @Column(nullable = false)
    private LocalDateTime timestamp;

    @Column(nullable = false)
    private Integer queueLength;

    @Column(nullable = false)
    private Double estimatedWaitTime;

    private Integer checkoutCounterId;

    public QueueEvent() {
    }

    public Long getId() {
        return id;
    }

    public Store getStore() {
        return store;
    }

    public void setStore(Store store) {
        this.store = store;
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