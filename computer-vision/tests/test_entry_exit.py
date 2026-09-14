"""
Unit tests for virtual line crossing entry / exit counting.
"""

from app.analytics.entry_exit import EntryExitCounter, intersect
from app.tracking.tracker import TrackedPerson


def test_line_intersection_math():
    # Horizontal line from (0, 100) to (200, 100)
    p1 = (0, 100)
    p2 = (200, 100)

    # Vertical crossing from (100, 50) to (100, 150)
    assert intersect((100, 50), (100, 150), p1, p2) is True

    # Segment that does not reach the line
    assert intersect((100, 50), (100, 90), p1, p2) is False

    # Parallel segment
    assert intersect((50, 50), (150, 50), p1, p2) is False


def test_entry_crossing():
    counter = EntryExitCounter(
        line_start=(0, 200),
        line_end=(500, 200),
        entry_direction="down",
        cooldown_frames=5,
    )

    # Frame 1: Person 1 at (250, 150) [outside]
    p1_f1 = TrackedPerson(track_id=1, bbox=(230, 100, 270, 200), confidence=0.9)
    entries, exits = counter.update([p1_f1])
    assert entries == 0
    assert exits == 0

    # Frame 2: Person 1 moves to (250, 250) [crosses down into inside]
    p1_f2 = TrackedPerson(track_id=1, bbox=(230, 200, 270, 300), confidence=0.9)
    entries, exits = counter.update([p1_f2])
    assert entries == 1
    assert exits == 0
    assert counter.get_stats() == {"entries": 1, "exits": 0}


def test_exit_crossing():
    counter = EntryExitCounter(
        line_start=(0, 200),
        line_end=(500, 200),
        entry_direction="down",
        cooldown_frames=5,
    )

    # Frame 1: Person 2 at (250, 250) [inside]
    p2_f1 = TrackedPerson(track_id=2, bbox=(230, 200, 270, 300), confidence=0.9)
    counter.update([p2_f1])

    # Frame 2: Person 2 moves to (250, 150) [crosses up into outside]
    p2_f2 = TrackedPerson(track_id=2, bbox=(230, 100, 270, 200), confidence=0.9)
    entries, exits = counter.update([p2_f2])
    assert entries == 0
    assert exits == 1


def test_debounce_prevents_duplicate_count():
    counter = EntryExitCounter(
        line_start=(0, 200),
        line_end=(500, 200),
        entry_direction="down",
        cooldown_frames=10,
    )

    # Crossing entry
    p1 = TrackedPerson(track_id=3, bbox=(230, 100, 270, 200), confidence=0.9)
    p2 = TrackedPerson(track_id=3, bbox=(230, 200, 270, 300), confidence=0.9)
    counter.update([p1])
    counter.update([p2])
    assert counter.entries == 1

    # Immediate jitter back and forth during cooldown
    counter.update([p1])
    counter.update([p2])
    # Should not re-increment entries due to cooldown
    assert counter.entries == 1
