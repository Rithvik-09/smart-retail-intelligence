package com.smartretail.inventory.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.smartretail.inventory.entity.InventoryRisk;

public interface InventoryRiskRepository extends JpaRepository<InventoryRisk, Long> {

    List<InventoryRisk> findByRiskLevelIgnoreCase(String riskLevel);

    List<InventoryRisk> findByAnomalyTrue();

    boolean existsByProductIdAndRiskLevelIgnoreCaseAndAnomaly(
            Long productId,
            String riskLevel,
            Boolean anomaly
    );
}