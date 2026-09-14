package com.smartretail.inventory.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.smartretail.inventory.entity.InventoryItem;

public interface InventoryItemRepository extends JpaRepository<InventoryItem, Long> {
}