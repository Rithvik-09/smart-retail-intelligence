package com.smartretail.inventory.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.smartretail.inventory.dto.InventoryItemRequest;
import com.smartretail.inventory.dto.InventoryItemResponse;
import com.smartretail.inventory.service.InventoryItemService;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/v1/inventory")
public class InventoryItemController {

    private final InventoryItemService inventoryItemService;

    public InventoryItemController(
            InventoryItemService inventoryItemService) {

        this.inventoryItemService = inventoryItemService;
    }

    @PostMapping
    public ResponseEntity<InventoryItemResponse> createInventoryItem(
            @Valid @RequestBody InventoryItemRequest request) {

        InventoryItemResponse response =
                inventoryItemService.createInventoryItem(request);

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(response);
    }

    @GetMapping
    public ResponseEntity<List<InventoryItemResponse>> getAllInventoryItems() {

        List<InventoryItemResponse> response =
                inventoryItemService.getAllInventoryItems();

        return ResponseEntity.ok(response);
    }

    @GetMapping("/stockout-risk")
public ResponseEntity<List<InventoryItemResponse>> getStockoutRiskItems() {

    List<InventoryItemResponse> response =
            inventoryItemService.getStockoutRiskItems();

    return ResponseEntity.ok(response);
}

}