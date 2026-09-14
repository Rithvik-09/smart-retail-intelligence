"""
Unit tests for PeopleCounter analytics module.
"""

import pytest
from app.analytics.people_counter import PeopleCounter


def test_people_counter_initial_state():
    counter = PeopleCounter(window_size=10)
    assert counter.current_count == 0
    assert counter.max_occupancy == 0
    assert counter.rolling_average == 0.0
    stats = counter.get_stats()
    assert stats["peopleCount"] == 0
    assert stats["maxOccupancy"] == 0
    assert stats["rollingAverage"] == 0.0


def test_people_counter_updates():
    counter = PeopleCounter(window_size=5)

    # Frame 1: 3 people
    assert counter.update(3) == 3
    assert counter.current_count == 3
    assert counter.max_occupancy == 3

    # Frame 2: 7 people
    assert counter.update(7) == 7
    assert counter.current_count == 7
    assert counter.max_occupancy == 7

    # Frame 3: 2 people
    assert counter.update(2) == 2
    assert counter.current_count == 2
    assert counter.max_occupancy == 7  # Peak retained

    # Rolling average of [3, 7, 2] = 4.0
    assert counter.rolling_average == pytest.approx(4.0)


def test_people_counter_with_list():
    counter = PeopleCounter()
    mock_detections = ["det1", "det2", "det3", "det4"]
    count = counter.update(mock_detections)
    assert count == 4
    assert counter.current_count == 4


def test_people_counter_reset():
    counter = PeopleCounter()
    counter.update(10)
    assert counter.max_occupancy == 10

    counter.reset()
    assert counter.current_count == 0
    assert counter.max_occupancy == 0
    assert counter.rolling_average == 0.0
