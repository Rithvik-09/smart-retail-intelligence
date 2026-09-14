package com.smartretail.shopper.controller;

import com.smartretail.shopper.dto.ShopperEventRequest;
import com.smartretail.shopper.entity.ShopperEvent;
import com.smartretail.shopper.service.ShopperEventService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/ingestion")
public class ShopperEventController {

    private final ShopperEventService shopperEventService;

    public ShopperEventController(
            ShopperEventService shopperEventService) {

        this.shopperEventService = shopperEventService;
    }

    @PostMapping("/shopper")
    public ResponseEntity<ShopperEvent> createShopperEvent(
            @Valid @RequestBody ShopperEventRequest request) {

        ShopperEvent savedEvent =
                shopperEventService.saveShopperEvent(request);

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(savedEvent);
    }

    @GetMapping("/shopper")
    public ResponseEntity<java.util.List<com.smartretail.shopper.dto.ShopperEventResponse>> getAllShopperEvents() {

    java.util.List<ShopperEvent> events =
            shopperEventService.getAllShopperEvents();

    java.util.List<com.smartretail.shopper.dto.ShopperEventResponse> response =
            events.stream()
                    .map(event -> new com.smartretail.shopper.dto.ShopperEventResponse(
                            event.getId(),
                            event.getStore().getId(),
                            event.getCameraId(),
                            event.getTimestamp(),
                            event.getPeopleCount(),
                            event.getZoneId()
                    ))
                    .toList();

    return ResponseEntity.ok(response);
}

@GetMapping("/shopper/summary")
public ResponseEntity<com.smartretail.shopper.dto.ShopperSummaryResponse> getShopperSummary(
        @RequestParam Long storeId) {

    com.smartretail.shopper.dto.ShopperSummaryResponse summary =
            shopperEventService.getShopperSummary(storeId);

    return ResponseEntity.ok(summary);
}
}