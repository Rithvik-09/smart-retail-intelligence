package com.smartretail.recommendation.service;

import com.smartretail.recommendation.dto.RecommendationRequest;
import com.smartretail.recommendation.dto.RecommendationResponse;
import com.smartretail.recommendation.entity.Recommendation;
import com.smartretail.recommendation.repository.RecommendationRepository;
import com.smartretail.store.entity.Store;
import com.smartretail.store.repository.StoreRepository;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class RecommendationService {
    private final RecommendationRepository recommendationRepository;
    private final StoreRepository storeRepository;

    public RecommendationService(RecommendationRepository recommendationRepository,
                                 StoreRepository storeRepository) {
        this.recommendationRepository = recommendationRepository;
        this.storeRepository = storeRepository;
    }

    public RecommendationResponse createRecommendation(RecommendationRequest request) {
        Store store = storeRepository.findById(request.getStoreId())
                .orElseThrow(() -> new RuntimeException(
                        "Store not found with ID: " + request.getStoreId()));

        Recommendation recommendation = new Recommendation();
        recommendation.setStore(store);
        recommendation.setTitle(request.getTitle());
        recommendation.setDescription(request.getDescription());
        recommendation.setCategory(request.getCategory());
        recommendation.setPriority(request.getPriority());
        recommendation.setTimestamp(request.getTimestamp());
        recommendation.setCompleted(request.getCompleted() != null
                ? request.getCompleted() : false);
        recommendation.setActionLabel(request.getActionLabel());
        recommendation.setActionKey(request.getActionKey());

        return toResponse(recommendationRepository.save(recommendation));
    }

    public List<RecommendationResponse> getAllRecommendations() {
        return recommendationRepository.findAll().stream()
                .map(this::toResponse).toList();
    }

    public List<RecommendationResponse> getHighPriorityRecommendations() {
        return recommendationRepository
                .findByPriorityIgnoreCaseAndCompletedFalse("HIGH")
                .stream().map(this::toResponse).toList();
    }

    public RecommendationResponse completeRecommendation(Long id) {
        Recommendation recommendation = recommendationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException(
                        "Recommendation not found with ID: " + id));
        recommendation.setCompleted(true);
        return toResponse(recommendationRepository.save(recommendation));
    }

    private RecommendationResponse toResponse(Recommendation recommendation) {
        return new RecommendationResponse(
                recommendation.getId(),
                recommendation.getStore().getId(),
                recommendation.getTitle(),
                recommendation.getDescription(),
                recommendation.getCategory(),
                recommendation.getPriority(),
                recommendation.getTimestamp(),
                recommendation.getCompleted(),
                recommendation.getActionLabel(),
                recommendation.getActionKey()
        );
    }
}
