package com.smartretail.inventory.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.smartretail.inventory.dto.InventoryItemRequest;
import com.smartretail.inventory.dto.InventoryItemResponse;
import com.smartretail.inventory.entity.InventoryItem;
import com.smartretail.inventory.repository.InventoryItemRepository;
import com.smartretail.store.entity.Store;
import com.smartretail.store.repository.StoreRepository;

@Service
public class InventoryItemService {

    private final InventoryItemRepository inventoryItemRepository;
    private final StoreRepository storeRepository;

    public InventoryItemService(
            InventoryItemRepository inventoryItemRepository,
            StoreRepository storeRepository) {

        this.inventoryItemRepository = inventoryItemRepository;
        this.storeRepository = storeRepository;
    }

    public InventoryItemResponse createInventoryItem(
            InventoryItemRequest request) {

        Store store = storeRepository.findById(request.getStoreId())
                .orElseThrow(() ->
                        new RuntimeException(
                                "Store not found with ID: "
                                        + request.getStoreId()
                        ));

        InventoryItem item = new InventoryItem();

        item.setStore(store);
        item.setProductName(request.getProductName());
        item.setCurrentStock(request.getCurrentStock());
        item.setReorderLevel(request.getReorderLevel());
        item.setPredictedStockoutRisk(
                request.getPredictedStockoutRisk()
        );

        InventoryItem savedItem =
                inventoryItemRepository.save(item);

        return toResponse(savedItem);
    }

    public List<InventoryItemResponse> getAllInventoryItems() {

        return inventoryItemRepository.findAll()
                .stream()
                .map(this::toResponse)
                .toList();
    }

    private InventoryItemResponse toResponse(
            InventoryItem item) {

        return new InventoryItemResponse(
                item.getId(),
                item.getStore().getId(),
                item.getProductName(),
                item.getCurrentStock(),
                item.getReorderLevel(),
                item.getPredictedStockoutRisk()
        );
    }
    public List<InventoryItemResponse> getStockoutRiskItems() {

    List<InventoryItem> items = inventoryItemRepository.findAll();

    return items.stream()
            .filter(item ->
                    item.getCurrentStock() <= item.getReorderLevel()
                    || (item.getPredictedStockoutRisk() != null
                    && item.getPredictedStockoutRisk() >= 0.70)
            )
            .map(item -> new InventoryItemResponse(
                    item.getId(),
                    item.getStore().getId(),
                    item.getProductName(),
                    item.getCurrentStock(),
                    item.getReorderLevel(),
                    item.getPredictedStockoutRisk()
            ))
            .toList();
}
}