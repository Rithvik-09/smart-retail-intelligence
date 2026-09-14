"""
Crowd Level Classification Module.
Classifies store or zone occupancy into configurable categories: LOW, MEDIUM, HIGH, CRITICAL.
"""

from enum import Enum
import logging
from typing import Dict, Tuple
from app.config import CrowdConfig

logger = logging.getLogger(__name__)


class CrowdLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# High-visibility BGR colors for HUD rendering
CROWD_COLORS: Dict[CrowdLevel, Tuple[int, int, int]] = {
    CrowdLevel.LOW: (0, 200, 100),       # Green
    CrowdLevel.MEDIUM: (0, 215, 255),    # Yellow
    CrowdLevel.HIGH: (0, 140, 255),      # Orange
    CrowdLevel.CRITICAL: (0, 0, 255),    # Red
}


class CrowdClassifier:
    """Classifies occupancy based on configurable store thresholds."""

    def __init__(self, config: CrowdConfig):
        self.config = config
        self.low_threshold = config.low
        self.medium_threshold = config.medium
        self.high_threshold = config.high

    def classify(self, people_count: int) -> CrowdLevel:
        """Classify a given count into LOW, MEDIUM, HIGH, or CRITICAL.

        Args:
            people_count: Number of shoppers observed.

        Returns:
            CrowdLevel enum string value.
        """
        count = max(0, people_count)
        if count <= self.low_threshold:
            return CrowdLevel.LOW
        elif count <= self.medium_threshold:
            return CrowdLevel.MEDIUM
        elif count <= self.high_threshold:
            return CrowdLevel.HIGH
        else:
            return CrowdLevel.CRITICAL

    def get_color(self, level: CrowdLevel) -> Tuple[int, int, int]:
        """Return BGR color corresponding to crowd severity."""
        return CROWD_COLORS.get(level, (255, 255, 255))

    def get_stats(self, people_count: int) -> Dict[str, str]:
        """Return standardized crowd level dictionary."""
        level = self.classify(people_count)
        return {
            "crowdLevel": level.value,
        }
