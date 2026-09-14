"""
Zone Occupancy Analytics Module.
Calculates real-time shopper counts inside arbitrary polygonal store zones.
"""

from dataclasses import dataclass
import logging
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np

from app.config import ZoneConfig
from app.tracking.tracker import TrackedPerson

logger = logging.getLogger(__name__)


# Zone color palette (BGR) for distinct visualization
ZONE_COLORS = [
    (255, 128, 0),    # Blue / Cyan
    (0, 200, 100),    # Green
    (180, 50, 220),   # Magenta
    (0, 165, 255),    # Orange
    (220, 220, 0),    # Cyan-Yellow
]


@dataclass
class ZoneOccupancy:
    """Live occupancy details for a specific store zone."""
    zone_id: int
    name: str
    people_count: int
    occupant_ids: List[int]


class ZoneManager:
    """Manages polygonal zones and computes per-zone shopper occupancy."""

    def __init__(self, zone_configs: List[ZoneConfig]):
        self.zones: List[ZoneConfig] = zone_configs
        # Pre-convert polygon coordinates to numpy int32 contours for fast cv2 testing
        self._zone_contours: Dict[int, np.ndarray] = {}
        for z in self.zones:
            if len(z.polygon) >= 3:
                pts = np.array(z.polygon, dtype=np.int32).reshape((-1, 1, 2))
                self._zone_contours[z.id] = pts

        self._last_occupancy: Dict[int, ZoneOccupancy] = {}

    def update(self, tracked_people: List[TrackedPerson]) -> Dict[int, ZoneOccupancy]:
        """Assign tracked individuals to zones based on bounding-box center points.

        Args:
            tracked_people: List of active tracked people.

        Returns:
            Dictionary mapping zone_id -> ZoneOccupancy.
        """
        occupancy_map: Dict[int, ZoneOccupancy] = {
            z.id: ZoneOccupancy(
                zone_id=z.id,
                name=z.name,
                people_count=0,
                occupant_ids=[],
            )
            for z in self.zones
        }

        for person in tracked_people:
            pt = (float(person.center[0]), float(person.center[1]))

            for z in self.zones:
                contour = self._zone_contours.get(z.id)
                if contour is not None:
                    # pointPolygonTest returns >= 0 if inside or on boundary
                    if cv2.pointPolygonTest(contour, pt, False) >= 0:
                        occupancy_map[z.id].people_count += 1
                        occupancy_map[z.id].occupant_ids.append(person.track_id)
                        # A person typically belongs to one primary zone at a time
                        break

        self._last_occupancy = occupancy_map
        return occupancy_map

    def get_zone_stats(self) -> List[Dict[str, int]]:
        """Return standardized zone occupancy statistics for JSON reporting."""
        return [
            {
                "zoneId": occ.zone_id,
                "peopleCount": occ.people_count,
            }
            for occ in self._last_occupancy.values()
        ]

    def draw_zones(self, frame: np.ndarray) -> np.ndarray:
        """Render semi-transparent zone polygons and occupancy badges on frame."""
        if not self._zone_contours:
            return frame

        annotated = frame.copy()
        overlay = frame.copy()

        for idx, z in enumerate(self.zones):
            contour = self._zone_contours.get(z.id)
            if contour is None:
                continue

            color = ZONE_COLORS[idx % len(ZONE_COLORS)]
            count = (
                self._last_occupancy[z.id].people_count
                if z.id in self._last_occupancy
                else 0
            )

            # Fill polygon on overlay
            cv2.fillPoly(overlay, [contour], color)

        # Blend semi-transparent polygons
        alpha = 0.22
        cv2.addWeighted(overlay, alpha, annotated, 1 - alpha, 0, annotated)

        # Draw crisp borders and labels
        for idx, z in enumerate(self.zones):
            contour = self._zone_contours.get(z.id)
            if contour is None:
                continue

            color = ZONE_COLORS[idx % len(ZONE_COLORS)]
            count = (
                self._last_occupancy[z.id].people_count
                if z.id in self._last_occupancy
                else 0
            )

            cv2.polylines(annotated, [contour], isClosed=True, color=color, thickness=2)

            # Draw zone label badge near first vertex or center
            first_pt = tuple(contour[0][0])
            label = f"{z.name} (ID {z.id}): {count} people"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

            badge_pos = (first_pt[0] + 5, first_pt[1] + 20)
            cv2.rectangle(
                annotated,
                (badge_pos[0] - 2, badge_pos[1] - th - 4),
                (badge_pos[0] + tw + 4, badge_pos[1] + 4),
                (20, 24, 30),
                -1,
            )
            cv2.putText(
                annotated,
                label,
                badge_pos,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
                cv2.LINE_AA,
            )

        return annotated
