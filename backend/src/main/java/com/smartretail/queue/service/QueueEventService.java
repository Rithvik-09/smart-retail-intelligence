package com.smartretail.queue.service;

import com.smartretail.queue.dto.QueueEventRequest;
import com.smartretail.queue.dto.QueueSummaryResponse;
import com.smartretail.queue.entity.QueueEvent;
import com.smartretail.queue.repository.QueueEventRepository;
import com.smartretail.store.entity.Store;
import com.smartretail.store.repository.StoreRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class QueueEventService {

    private final QueueEventRepository queueEventRepository;
    private final StoreRepository storeRepository;

    public QueueEventService(
            QueueEventRepository queueEventRepository,
            StoreRepository storeRepository) {

        this.queueEventRepository = queueEventRepository;
        this.storeRepository = storeRepository;
    }

    public QueueEvent saveQueueEvent(QueueEventRequest request) {

        Store store = storeRepository.findById(request.getStoreId())
                .orElseThrow(() ->
                        new RuntimeException(
                                "Store not found with ID: " + request.getStoreId()
                        )
                );

        QueueEvent event = new QueueEvent();

        event.setStore(store);
        event.setCameraId(request.getCameraId());
        event.setTimestamp(request.getTimestamp());
        event.setQueueLength(request.getQueueLength());
        event.setEstimatedWaitTime(request.getEstimatedWaitTime());
        event.setCheckoutCounterId(request.getCheckoutCounterId());

        return queueEventRepository.save(event);
    }

    public List<QueueEvent> getAllQueueEvents() {
        return queueEventRepository.findAll();
    }

    public QueueSummaryResponse getQueueSummary(Long storeId) {

        List<QueueEvent> events =
                queueEventRepository.findAll()
                        .stream()
                        .filter(event -> event.getStore().getId().equals(storeId))
                        .toList();

        if (events.isEmpty()) {
            return new QueueSummaryResponse(
                    storeId,
                    0,
                    0.0,
                    0,
                    0.0,
                    0.0,
                    0.0
            );
        }

        Integer currentQueueLength =
                events.get(events.size() - 1).getQueueLength();

        Double averageQueueLength =
                events.stream()
                        .mapToInt(QueueEvent::getQueueLength)
                        .average()
                        .orElse(0.0);

        Integer maximumQueueLength =
                events.stream()
                        .mapToInt(QueueEvent::getQueueLength)
                        .max()
                        .orElse(0);

        Double currentEstimatedWaitTime =
                events.get(events.size() - 1).getEstimatedWaitTime();

        Double averageEstimatedWaitTime =
                events.stream()
                        .mapToDouble(QueueEvent::getEstimatedWaitTime)
                        .average()
                        .orElse(0.0);

        Double maximumEstimatedWaitTime =
                events.stream()
                        .mapToDouble(QueueEvent::getEstimatedWaitTime)
                        .max()
                        .orElse(0.0);

        return new QueueSummaryResponse(
                storeId,
                currentQueueLength,
                averageQueueLength,
                maximumQueueLength,
                currentEstimatedWaitTime,
                averageEstimatedWaitTime,
                maximumEstimatedWaitTime
        );
    }
}
