"""
Unit tests for JSON event generation schemas.
"""

import json
from app.events.event_builder import EventBuilder, get_current_utc_iso_timestamp


def test_shopper_event_basic():
    builder = EventBuilder(store_id=1, camera_id="CAM-01")
    event = builder.build_shopper_event(
        people_count=18,
        zone_id=2,
        timestamp="2026-09-06T14:30:00Z",
    )

    assert event == {
        "storeId": 1,
        "cameraId": "CAM-01",
        "timestamp": "2026-09-06T14:30:00Z",
        "peopleCount": 18,
        "zoneId": 2,
    }


def test_shopper_event_full():
    builder = EventBuilder(store_id=1, camera_id="CAM-01")
    event = builder.build_shopper_event(
        people_count=18,
        zone_id=2,
        entries=5,
        exits=2,
        crowd_level="HIGH",
        timestamp="2026-09-06T14:30:00Z",
    )

    assert event == {
        "storeId": 1,
        "cameraId": "CAM-01",
        "timestamp": "2026-09-06T14:30:00Z",
        "peopleCount": 18,
        "zoneId": 2,
        "entries": 5,
        "exits": 2,
        "crowdLevel": "HIGH",
    }

    # Verify JSON serialization
    json_str = builder.to_json(event)
    parsed = json.loads(json_str)
    assert parsed["crowdLevel"] == "HIGH"
    assert parsed["entries"] == 5


def test_queue_event():
    builder = EventBuilder(store_id=1, camera_id="CAM-01")
    event = builder.build_queue_event(
        counter_id=3,
        queue_length=12,
        estimated_wait_time_minutes=14,
    )

    assert event == {
        "storeId": 1,
        "counterId": 3,
        "queueLength": 12,
        "estimatedWaitTimeMinutes": 14,
    }

    json_str = builder.to_json(event)
    parsed = json.loads(json_str)
    assert parsed["queueLength"] == 12
    assert parsed["estimatedWaitTimeMinutes"] == 14


def test_iso_timestamp_format():
    ts = get_current_utc_iso_timestamp()
    # Check format: YYYY-MM-DDTHH:MM:SSZ
    assert len(ts) == 20
    assert ts[10] == "T"
    assert ts[-1] == "Z"
