package com.smartretail.shopper.service;

import com.smartretail.shopper.dto.ShopperEventRequest;
import com.smartretail.shopper.dto.ShopperSummaryResponse;
import com.smartretail.shopper.entity.ShopperEvent;
import com.smartretail.shopper.repository.ShopperEventRepository;
import com.smartretail.store.entity.Store;
import com.smartretail.store.repository.StoreRepository;
import org.springframework.stereotype.Service;

@Service
public class ShopperEventService {

    private final ShopperEventRepository shopperEventRepository;
    private final StoreRepository storeRepository;

    public ShopperEventService(
            ShopperEventRepository shopperEventRepository,
            StoreRepository storeRepository) {

        this.shopperEventRepository = shopperEventRepository;
        this.storeRepository = storeRepository;
    }

    public ShopperEvent saveShopperEvent(ShopperEventRequest request) {

        Store store = storeRepository.findById(request.getStoreId())
                .orElseThrow(() ->
                        new RuntimeException(
                                "Store not found with ID: " + request.getStoreId()
                        )
                );

        ShopperEvent event = new ShopperEvent();

        event.setStore(store);
        event.setCameraId(request.getCameraId());
        event.setTimestamp(request.getTimestamp());
        event.setPeopleCount(request.getPeopleCount());
        event.setZoneId(request.getZoneId());

        return shopperEventRepository.save(event);
    }
    public java.util.List<ShopperEvent> getAllShopperEvents() {
    return shopperEventRepository.findAll();
}

public ShopperSummaryResponse getShopperSummary(Long storeId) {

    java.util.List<ShopperEvent> events =
            shopperEventRepository.findAll()
                    .stream()
                    .filter(event -> event.getStore().getId().equals(storeId))
                    .toList();

    if (events.isEmpty()) {
        return new ShopperSummaryResponse(
                storeId,
                0,
                0.0,
                0
        );
    }

    Integer currentPeopleCount =
            events.get(events.size() - 1).getPeopleCount();

    Double averagePeopleCount =
            events.stream()
                    .mapToInt(ShopperEvent::getPeopleCount)
                    .average()
                    .orElse(0.0);

    Integer maximumPeopleCount =
            events.stream()
                    .mapToInt(ShopperEvent::getPeopleCount)
                    .max()
                    .orElse(0);

    return new ShopperSummaryResponse(
            storeId,
            currentPeopleCount,
            averagePeopleCount,
            maximumPeopleCount
    );
}

}