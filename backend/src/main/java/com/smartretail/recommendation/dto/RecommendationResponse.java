package com.smartretail.recommendation.dto;

import java.time.LocalDateTime;

public class RecommendationResponse {
    private Long id;
    private Long storeId;
    private String title;
    private String description;
    private String category;
    private String priority;
    private LocalDateTime timestamp;
    private Boolean completed;
    private String actionLabel;
    private String actionKey;

    public RecommendationResponse() {}

    public RecommendationResponse(Long id, Long storeId, String title,
                                  String description, String category,
                                  String priority, LocalDateTime timestamp,
                                  Boolean completed, String actionLabel,
                                  String actionKey) {
        this.id = id;
        this.storeId = storeId;
        this.title = title;
        this.description = description;
        this.category = category;
        this.priority = priority;
        this.timestamp = timestamp;
        this.completed = completed;
        this.actionLabel = actionLabel;
        this.actionKey = actionKey;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getStoreId() { return storeId; }
    public void setStoreId(Long storeId) { this.storeId = storeId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    public String getPriority() { return priority; }
    public void setPriority(String priority) { this.priority = priority; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
    public Boolean getCompleted() { return completed; }
    public void setCompleted(Boolean completed) { this.completed = completed; }
    public String getActionLabel() { return actionLabel; }
    public void setActionLabel(String actionLabel) { this.actionLabel = actionLabel; }
    public String getActionKey() { return actionKey; }
    public void setActionKey(String actionKey) { this.actionKey = actionKey; }
}
