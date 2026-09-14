"""
Unit tests for anonymous object tracking structures.
"""

from app.tracking.tracker import TrackedPerson, get_color_for_id


def test_tracked_person_properties():
    person = TrackedPerson(
        track_id=17,
        bbox=(100, 200, 300, 600),
        confidence=0.88,
        history=[(200, 400), (205, 410)],
    )

    assert person.track_id == 17
    assert person.center == (200, 400)
    assert person.bottom_center == (200, 600)
    assert person.confidence == 0.88
    assert len(person.history) == 2


def test_color_determinism():
    # Colors for the same ID must be completely deterministic
    color1 = get_color_for_id(17)
    color2 = get_color_for_id(17)
    assert color1 == color2
    assert len(color1) == 3
    assert all(0 <= c <= 255 for c in color1)
