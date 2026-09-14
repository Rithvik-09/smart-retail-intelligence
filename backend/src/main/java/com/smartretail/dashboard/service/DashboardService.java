package com.smartretail.dashboard.service;

import org.springframework.stereotype.Service;

import com.smartretail.alert.service.AlertService;
import com.smartretail.dashboard.dto.DashboardSummaryResponse;
import com.smartretail.inventory.service.InventoryItemService;
import com.smartretail.inventory.service.InventoryRiskService;
import com.smartretail.queue.dto.QueueSummaryResponse;
import com.smartretail.queue.service.QueueEventService;
import com.smartretail.shopper.dto.ShopperSummaryResponse;
import com.smartretail.shopper.service.ShopperEventService;

@Service
public class DashboardService {

    private final ShopperEventService shopperEventService;
    private final QueueEventService queueEventService;
    private final InventoryItemService inventoryItemService;
    private final InventoryRiskService inventoryRiskService;
    private final AlertService alertService;

    public DashboardService(
            ShopperEventService shopperEventService,
            QueueEventService queueEventService,
            InventoryItemService inventoryItemService,
            InventoryRiskService inventoryRiskService,
            AlertService alertService) {

        this.shopperEventService = shopperEventService;
        this.queueEventService = queueEventService;
        this.inventoryItemService = inventoryItemService;
        this.inventoryRiskService = inventoryRiskService;
        this.alertService = alertService;
    }

    public DashboardSummaryResponse getDashboardSummary(Long storeId) {

        ShopperSummaryResponse shopperSummary =
                shopperEventService.getShopperSummary(storeId);

        QueueSummaryResponse queueSummary =
                queueEventService.getQueueSummary(storeId);

        int inventoryItems =
                (int) inventoryItemService.getAllInventoryItems()
                        .stream()
                        .filter(item -> item.getStoreId().equals(storeId))
                        .count();

        /*
         * Stock risks now come from the AI InventoryRisk module.
         *
         * Multiple risk records can exist for the same product because
         * the ML/AI service may receive repeated predictions.
         *
         * Therefore count distinct product IDs instead of counting
         * every prediction record.
         */
        int stockoutRiskItems =
                (int) inventoryRiskService.getHighRiskItems()
                        .stream()
                        .map(risk -> risk.getProductId())
                        .distinct()
                        .count();

        int activeAlerts =
                (int) alertService.getAllAlerts()
                        .stream()
                        .filter(alert ->
                                alert.getStoreId().equals(storeId)
                                        && !alert.getResolved())
                        .count();

        int criticalAlerts =
                (int) alertService.getCriticalAlerts()
                        .stream()
                        .filter(alert ->
                                alert.getStoreId().equals(storeId))
                        .count();

        return new DashboardSummaryResponse(
                storeId,
                shopperSummary.getCurrentPeopleCount(),
                queueSummary.getCurrentQueueLength(),
                shopperSummary.getAveragePeopleCount(),
                queueSummary.getAverageQueueLength(),
                queueSummary.getCurrentEstimatedWaitTime(),
                queueSummary.getAverageEstimatedWaitTime(),
                activeAlerts,
                criticalAlerts,
                inventoryItems,
                stockoutRiskItems
        );
    }
}