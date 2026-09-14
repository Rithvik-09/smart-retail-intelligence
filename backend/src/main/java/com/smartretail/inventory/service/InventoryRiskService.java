package com.smartretail.inventory.service;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.stereotype.Service;

import com.smartretail.alert.dto.AlertRequest;
import com.smartretail.alert.service.AlertService;
import com.smartretail.inventory.dto.InventoryRiskRequest;
import com.smartretail.inventory.entity.InventoryRisk;
import com.smartretail.inventory.repository.InventoryRiskRepository;
import com.smartretail.recommendation.dto.RecommendationRequest;
import com.smartretail.recommendation.service.RecommendationService;

@Service
public class InventoryRiskService {

    private final InventoryRiskRepository inventoryRiskRepository;
    private final AlertService alertService;
    private final RecommendationService recommendationService;

    public InventoryRiskService(
            InventoryRiskRepository inventoryRiskRepository,
            AlertService alertService,
            RecommendationService recommendationService) {

        this.inventoryRiskRepository = inventoryRiskRepository;
        this.alertService = alertService;
        this.recommendationService = recommendationService;
    }

    public InventoryRisk saveRisk(InventoryRiskRequest request) {

        /*
         * Check whether this exact risk has already been processed
         * BEFORE saving the new record.
         */
        boolean alreadyProcessed =
                inventoryRiskRepository
                        .existsByProductIdAndRiskLevelIgnoreCaseAndAnomaly(
                                request.getProductId(),
                                request.getRiskLevel(),
                                request.getAnomaly()
                        );

        InventoryRisk risk = new InventoryRisk();

        risk.setProductId(request.getProductId());
        risk.setStockoutProbability(request.getStockoutProbability());
        risk.setRiskLevel(request.getRiskLevel());
        risk.setAnomaly(request.getAnomaly());
        risk.setRecommendedAction(request.getRecommendedAction());
        risk.setTimestamp(LocalDateTime.now());

        InventoryRisk savedRisk =
                inventoryRiskRepository.save(risk);

        /*
         * Automatically create an alert and recommendation
         * for HIGH or CRITICAL ML predictions.
         *
         * Only create them when this prediction combination
         * has not already been processed.
         */
        if (request.getStoreId() != null
                && isHighRisk(request.getRiskLevel())
                && !alreadyProcessed) {

            createAutomaticAlert(request);
            createAutomaticRecommendation(request);
        }

        return savedRisk;
    }

    private boolean isHighRisk(String riskLevel) {

        return "HIGH".equalsIgnoreCase(riskLevel)
                || "CRITICAL".equalsIgnoreCase(riskLevel);
    }

    private void createAutomaticAlert(
            InventoryRiskRequest request) {

        AlertRequest alertRequest = new AlertRequest();

        alertRequest.setStoreId(request.getStoreId());

        alertRequest.setTitle(
                "AI Stock-out Risk Detected"
        );

        alertRequest.setDescription(
                "Product " + request.getProductId()
                        + " has a predicted stock-out probability of "
                        + Math.round(request.getStockoutProbability() * 100)
                        + "%. Risk level: "
                        + request.getRiskLevel()
                        + ". Anomaly detected: "
                        + request.getAnomaly()
                        + "."
        );

        alertRequest.setSeverity(
                request.getRiskLevel().toUpperCase()
        );

        alertRequest.setPriority("HIGH");

        alertRequest.setCategory("INVENTORY");

        alertRequest.setTimestamp(
                LocalDateTime.now()
        );

        alertRequest.setResolved(false);

        alertRequest.setActionLabel(
                "Review Inventory"
        );

        alertRequest.setActionKey(
                "REVIEW_INVENTORY"
        );

        alertService.createAlert(alertRequest);
    }

    private void createAutomaticRecommendation(
            InventoryRiskRequest request) {

        RecommendationRequest recommendationRequest =
                new RecommendationRequest();

        recommendationRequest.setStoreId(
                request.getStoreId()
        );

        recommendationRequest.setTitle(
                "Replenish Product " + request.getProductId()
        );

        recommendationRequest.setDescription(
                "AI predicts a "
                        + Math.round(request.getStockoutProbability() * 100)
                        + "% stock-out probability. Recommended action: "
                        + request.getRecommendedAction()
                        + "."
        );

        recommendationRequest.setCategory(
                "INVENTORY"
        );

        recommendationRequest.setPriority("HIGH");

        recommendationRequest.setTimestamp(
                LocalDateTime.now()
        );

        recommendationRequest.setCompleted(false);

        recommendationRequest.setActionLabel(
                request.getRecommendedAction()
        );

        recommendationRequest.setActionKey(
                request.getRecommendedAction()
        );

        recommendationService.createRecommendation(
                recommendationRequest
        );
    }

    public List<InventoryRisk> getAllRisks() {
        return inventoryRiskRepository.findAll();
    }

    public List<InventoryRisk> getHighRiskItems() {
        return inventoryRiskRepository
                .findByRiskLevelIgnoreCase("HIGH");
    }

    public List<InventoryRisk> getCriticalRiskItems() {
        return inventoryRiskRepository
                .findByRiskLevelIgnoreCase("CRITICAL");
    }

    public List<InventoryRisk> getAnomalies() {
        return inventoryRiskRepository.findByAnomalyTrue();
    }
}