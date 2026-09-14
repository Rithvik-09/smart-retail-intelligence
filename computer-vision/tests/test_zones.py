"""
Unit tests for polygonal zone occupancy analytics.
"""

from app.analytics.zones import ZoneManager
from app.config import ZoneConfig
from app.tracking.tracker import TrackedPerson


def test_zone_assignment():
    z1 = ZoneConfig(
        id=1,
        name="Entrance",
        polygon=[[0, 0], [200, 0], [200, 200], [0, 200]],
    )
    z2 = ZoneConfig(
        id=2,
        name="Electronics",
        polygon=[[300, 0], [500, 0], [500, 200], [300, 200]],
    )

    manager = ZoneManager([z1, z2])

    # Person 1 at center (100, 100) -> inside Zone 1
    p1 = TrackedPerson(track_id=1, bbox=(50, 50, 150, 150), confidence=0.9)

    # Person 2 at center (400, 100) -> inside Zone 2
    p2 = TrackedPerson(track_id=2, bbox=(350, 50, 450, 150), confidence=0.9)

    # Person 3 at center (250, 100) -> between zones (in hallway)
    p3 = TrackedPerson(track_id=3, bbox=(200, 50, 300, 150), confidence=0.9)

    occupancy = manager.update([p1, p2, p3])

    assert occupancy[1].people_count == 1
    assert occupancy[1].occupant_ids == [1]

    assert occupancy[2].people_count == 1
    assert occupancy[2].occupant_ids == [2]

    stats = manager.get_zone_stats()
    assert len(stats) == 2
    assert {"zoneId": 1, "peopleCount": 1} in stats
    assert {"zoneId": 2, "peopleCount": 1} in stats


def test_empty_zone_when_no_people():
    z1 = ZoneConfig(
        id=1,
        name="Entrance",
        polygon=[[0, 0], [100, 0], [100, 100], [0, 100]],
    )
    manager = ZoneManager([z1])
    occupancy = manager.update([])
    assert occupancy[1].people_count == 0
    assert occupancy[1].occupant_ids == []
