package com.smartretail.alert.dto;

import java.time.LocalDateTime;

public class AlertResponse {

    private Long id;
    private Long storeId;
    private String title;
    private String description;
    private String severity;
    private String priority;
    private String category;
    private LocalDateTime timestamp;
    private Boolean resolved;
    private String actionLabel;
    private String actionKey;

    public AlertResponse() {
    }

    public AlertResponse(
            Long id,
            Long storeId,
            String title,
            String description,
            String severity,
            String priority,
            String category,
            LocalDateTime timestamp,
            Boolean resolved,
            String actionLabel,
            String actionKey) {

        this.id = id;
        this.storeId = storeId;
        this.title = title;
        this.description = description;
        this.severity = severity;
        this.priority = priority;
        this.category = category;
        this.timestamp = timestamp;
        this.resolved = resolved;
        this.actionLabel = actionLabel;
        this.actionKey = actionKey;
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

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getSeverity() {
        return severity;
    }

    public void setSeverity(String severity) {
        this.severity = severity;
    }

    public String getPriority() {
        return priority;
    }

    public void setPriority(String priority) {
        this.priority = priority;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public Boolean getResolved() {
        return resolved;
    }

    public void setResolved(Boolean resolved) {
        this.resolved = resolved;
    }

    public String getActionLabel() {
        return actionLabel;
    }

    public void setActionLabel(String actionLabel) {
        this.actionLabel = actionLabel;
    }

    public String getActionKey() {
        return actionKey;
    }

    public void setActionKey(String actionKey) {
        this.actionKey = actionKey;
    }
}
