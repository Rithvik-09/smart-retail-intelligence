package com.smartretail.inventory.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.smartretail.inventory.dto.InventoryRiskRequest;
import com.smartretail.inventory.entity.InventoryRisk;
import com.smartretail.inventory.service.InventoryRiskService;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/v1/ingestion/inventory-risk")
public class InventoryRiskController {

    private final InventoryRiskService inventoryRiskService;

    public InventoryRiskController(
            InventoryRiskService inventoryRiskService) {
        this.inventoryRiskService = inventoryRiskService;
    }

    @PostMapping
    public ResponseEntity<InventoryRisk> saveRisk(
            @Valid @RequestBody InventoryRiskRequest request) {

        InventoryRisk savedRisk =
                inventoryRiskService.saveRisk(request);

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(savedRisk);
    }

    @GetMapping
    public ResponseEntity<List<InventoryRisk>> getAllRisks() {
        return ResponseEntity.ok(
                inventoryRiskService.getAllRisks()
        );
    }

    @GetMapping("/high")
    public ResponseEntity<List<InventoryRisk>> getHighRiskItems() {
        return ResponseEntity.ok(
                inventoryRiskService.getHighRiskItems()
        );
    }

    @GetMapping("/critical")
    public ResponseEntity<List<InventoryRisk>> getCriticalRiskItems() {
        return ResponseEntity.ok(
                inventoryRiskService.getCriticalRiskItems()
        );
    }

    @GetMapping("/anomalies")
    public ResponseEntity<List<InventoryRisk>> getAnomalies() {
        return ResponseEntity.ok(
                inventoryRiskService.getAnomalies()
        );
    }
}