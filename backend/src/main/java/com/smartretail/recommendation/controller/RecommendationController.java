package com.smartretail.recommendation.controller;

import com.smartretail.recommendation.dto.RecommendationRequest;
import com.smartretail.recommendation.dto.RecommendationResponse;
import com.smartretail.recommendation.service.RecommendationService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/v1/recommendations")
public class RecommendationController {
    private final RecommendationService recommendationService;

    public RecommendationController(RecommendationService recommendationService) {
        this.recommendationService = recommendationService;
    }

    @PostMapping
    public ResponseEntity<RecommendationResponse> createRecommendation(
            @Valid @RequestBody RecommendationRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(recommendationService.createRecommendation(request));
    }

    @GetMapping
    public ResponseEntity<List<RecommendationResponse>> getAllRecommendations() {
        return ResponseEntity.ok(recommendationService.getAllRecommendations());
    }

    @GetMapping("/high-priority")
    public ResponseEntity<List<RecommendationResponse>> getHighPriorityRecommendations() {
        return ResponseEntity.ok(
                recommendationService.getHighPriorityRecommendations());
    }

    @PutMapping("/{id}/complete")
    public ResponseEntity<RecommendationResponse> completeRecommendation(
            @PathVariable Long id) {
        return ResponseEntity.ok(
                recommendationService.completeRecommendation(id));
    }
}
