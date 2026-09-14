package com.smartretail.queue.controller;

import com.smartretail.queue.dto.QueueEventRequest;
import com.smartretail.queue.dto.QueueEventResponse;
import com.smartretail.queue.dto.QueueSummaryResponse;
import com.smartretail.queue.entity.QueueEvent;
import com.smartretail.queue.service.QueueEventService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/ingestion")
public class QueueEventController {

    private final QueueEventService queueEventService;

    public QueueEventController(QueueEventService queueEventService) {
        this.queueEventService = queueEventService;
    }

    @PostMapping("/queue")
    public ResponseEntity<QueueEventResponse> createQueueEvent(
            @Valid @RequestBody QueueEventRequest request) {

        QueueEvent savedEvent = queueEventService.saveQueueEvent(request);

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(toResponse(savedEvent));
    }

    @GetMapping("/queue")
    public ResponseEntity<List<QueueEventResponse>> getAllQueueEvents() {

        List<QueueEvent> events = queueEventService.getAllQueueEvents();

        List<QueueEventResponse> response =
                events.stream()
                        .map(this::toResponse)
                        .toList();

        return ResponseEntity.ok(response);
    }

    @GetMapping("/queue/summary")
    public ResponseEntity<QueueSummaryResponse> getQueueSummary(
            @RequestParam Long storeId) {

        QueueSummaryResponse summary = queueEventService.getQueueSummary(storeId);

        return ResponseEntity.ok(summary);
    }

    private QueueEventResponse toResponse(QueueEvent event) {
        return new QueueEventResponse(
                event.getId(),
                event.getStore().getId(),
                event.getCameraId(),
                event.getTimestamp(),
                event.getQueueLength(),
                event.getEstimatedWaitTime(),
                event.getCheckoutCounterId()
        );
    }
}
