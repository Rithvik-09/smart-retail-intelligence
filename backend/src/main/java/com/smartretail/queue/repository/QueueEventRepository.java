package com.smartretail.queue.repository;

import com.smartretail.queue.entity.QueueEvent;
import org.springframework.data.jpa.repository.JpaRepository;

public interface QueueEventRepository extends JpaRepository<QueueEvent, Long> {
}