package com.smartretail.shopper.repository;

import com.smartretail.shopper.entity.ShopperEvent;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ShopperEventRepository extends JpaRepository<ShopperEvent, Long> {
}