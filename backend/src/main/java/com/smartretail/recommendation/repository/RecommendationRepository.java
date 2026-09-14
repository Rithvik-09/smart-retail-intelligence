package com.smartretail.recommendation.repository;

import com.smartretail.recommendation.entity.Recommendation;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface RecommendationRepository extends JpaRepository<Recommendation, Long> {
    List<Recommendation> findByPriorityIgnoreCaseAndCompletedFalse(String priority);
}
