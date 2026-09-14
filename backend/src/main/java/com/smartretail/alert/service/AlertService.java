package com.smartretail.alert.service;

import com.smartretail.alert.dto.AlertRequest;
import com.smartretail.alert.dto.AlertResponse;
import com.smartretail.alert.entity.Alert;
import com.smartretail.alert.repository.AlertRepository;
import com.smartretail.store.entity.Store;
import com.smartretail.store.repository.StoreRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class AlertService {

    private final AlertRepository alertRepository;
    private final StoreRepository storeRepository;

    public AlertService(
            AlertRepository alertRepository,
            StoreRepository storeRepository) {

        this.alertRepository = alertRepository;
        this.storeRepository = storeRepository;
    }

    public AlertResponse createAlert(AlertRequest request) {

        Store store = storeRepository.findById(request.getStoreId())
                .orElseThrow(() ->
                        new RuntimeException(
                                "Store not found with ID: " + request.getStoreId()
                        )
                );

        Alert alert = new Alert();

        alert.setStore(store);
        alert.setTitle(request.getTitle());
        alert.setDescription(request.getDescription());
        alert.setSeverity(request.getSeverity());
        alert.setPriority(request.getPriority());
        alert.setCategory(request.getCategory());
        alert.setTimestamp(request.getTimestamp());
        alert.setResolved(
                request.getResolved() != null ? request.getResolved() : false
        );
        alert.setActionLabel(request.getActionLabel());
        alert.setActionKey(request.getActionKey());

        return toResponse(alertRepository.save(alert));
    }

    public List<AlertResponse> getAllAlerts() {
        return alertRepository.findAll()
                .stream()
                .map(this::toResponse)
                .toList();
    }

    public List<AlertResponse> getCriticalAlerts() {
        return alertRepository
                .findBySeverityIgnoreCaseAndResolvedFalse("CRITICAL")
                .stream()
                .map(this::toResponse)
                .toList();
    }

    public AlertResponse resolveAlert(Long id) {

        Alert alert = alertRepository.findById(id)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Alert not found with ID: " + id
                        )
                );

        alert.setResolved(true);

        return toResponse(alertRepository.save(alert));
    }

    private AlertResponse toResponse(Alert alert) {

        return new AlertResponse(
                alert.getId(),
                alert.getStore().getId(),
                alert.getTitle(),
                alert.getDescription(),
                alert.getSeverity(),
                alert.getPriority(),
                alert.getCategory(),
                alert.getTimestamp(),
                alert.getResolved(),
                alert.getActionLabel(),
                alert.getActionKey()
        );
    }
}
