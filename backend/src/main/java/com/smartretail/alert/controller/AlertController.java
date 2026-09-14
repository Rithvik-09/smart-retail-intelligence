package com.smartretail.alert.controller;

import com.smartretail.alert.dto.AlertRequest;
import com.smartretail.alert.dto.AlertResponse;
import com.smartretail.alert.service.AlertService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/alerts")
public class AlertController {

    private final AlertService alertService;

    public AlertController(AlertService alertService) {
        this.alertService = alertService;
    }

    @PostMapping
    public ResponseEntity<AlertResponse> createAlert(
            @Valid @RequestBody AlertRequest request) {

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(alertService.createAlert(request));
    }

    @GetMapping
    public ResponseEntity<List<AlertResponse>> getAllAlerts() {
        return ResponseEntity.ok(alertService.getAllAlerts());
    }

    @GetMapping("/critical")
    public ResponseEntity<List<AlertResponse>> getCriticalAlerts() {
        return ResponseEntity.ok(alertService.getCriticalAlerts());
    }

    @PutMapping("/{id}/resolve")
    public ResponseEntity<AlertResponse> resolveAlert(@PathVariable Long id) {
        return ResponseEntity.ok(alertService.resolveAlert(id));
    }
}
