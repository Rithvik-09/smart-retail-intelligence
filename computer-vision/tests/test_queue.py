"""
Unit tests for checkout queue detection and wait time estimation.
"""

from app.analytics.queue import QueueManager
from app.config import CheckoutConfig, CounterConfig
from app.tracking.tracker import TrackedPerson


def test_queue_counting_and_wait_time():
    c1 = CounterConfig(
        id=1,
        name="Counter 1",
        average_service_time_minutes=1.0,
        polygon=[[0, 0], [100, 0], [100, 100], [0, 100]],
    )
    c2 = CounterConfig(
        id=2,
        name="Counter 2",
        average_service_time_minutes=1.2,
        polygon=[[200, 0], [300, 0], [300, 100], [200, 100]],
    )

    manager = QueueManager(CheckoutConfig(counters=[c1, c2]))

    # Place 3 people in Counter 1: wait = 3 * 1.0 = 3 min
    p1 = TrackedPerson(track_id=1, bbox=(20, 20, 80, 80), confidence=0.9)
    p2 = TrackedPerson(track_id=2, bbox=(25, 25, 85, 85), confidence=0.9)
    p3 = TrackedPerson(track_id=3, bbox=(30, 30, 90, 90), confidence=0.9)

    # Place 12 people in Counter 2: wait = round(12 * 1.2) = round(14.4) = 14 min
    counter2_people = [
        TrackedPerson(track_id=10 + i, bbox=(220, 20, 280, 80), confidence=0.9)
        for i in range(12)
    ]

    all_people = [p1, p2, p3] + counter2_people
    metrics = manager.update(all_people)

    # Counter 1 verification
    assert metrics[1].queue_length == 3
    assert metrics[1].estimated_wait_time_minutes == 3
    assert len(metrics[1].occupant_ids) == 3

    # Counter 2 verification
    assert metrics[2].queue_length == 12
    assert metrics[2].estimated_wait_time_minutes == 14  # round(14.4) = 14
    assert len(metrics[2].occupant_ids) == 12


def test_queue_events_schema():
    c1 = CounterConfig(
        id=3,
        name="Counter 3",
        average_service_time_minutes=1.2,
        polygon=[[10, 10], [100, 10], [100, 100], [10, 100]],
    )
    manager = QueueManager(CheckoutConfig(counters=[c1]))

    # Add 12 people
    people = [
        TrackedPerson(track_id=100 + i, bbox=(30, 30, 70, 70), confidence=0.9)
        for i in range(12)
    ]
    manager.update(people)

    events = manager.get_queue_events(store_id=1)
    assert len(events) == 1
    event = events[0]

    assert event == {
        "storeId": 1,
        "counterId": 3,
        "queueLength": 12,
        "estimatedWaitTimeMinutes": 14,
    }
