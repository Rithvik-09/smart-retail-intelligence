package com.smartretail.dashboard.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.smartretail.dashboard.dto.DashboardSummaryResponse;
import com.smartretail.dashboard.service.DashboardService;

@RestController
@RequestMapping("/api/v1/stores")
public class DashboardController {

    private final DashboardService dashboardService;

    public DashboardController(DashboardService dashboardService) {
        this.dashboardService = dashboardService;
    }

    @GetMapping("/{storeId}/dashboard/summary")
    public ResponseEntity<DashboardSummaryResponse> getDashboardSummary(
            @PathVariable Long storeId) {

        return ResponseEntity.ok(
                dashboardService.getDashboardSummary(storeId)
        );
    }
}