"""
JSON Event Builder Module.
Constructs JSON event payloads compatible with the Spring Boot ingestion APIs.
"""

from datetime import datetime
import json
from typing import Any, Dict, Optional


def get_current_iso_timestamp() -> str:
    """Return current timestamp in ISO-8601 format without timezone suffix."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


class EventBuilder:
    """Constructs event payloads for the Spring Boot backend."""

    def __init__(self, store_id: int = 1, camera_id: str = "CAM-01"):
        self.store_id = int(store_id)
        self.camera_id = str(camera_id)

    def build_shopper_event(
        self,
        people_count: int,
        zone_id: Optional[int] = None,
        entries: Optional[int] = None,
        exits: Optional[int] = None,
        crowd_level: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:

        event: Dict[str, Any] = {
            "storeId": self.store_id,
            "cameraId": self.camera_id,
            "timestamp": timestamp or get_current_iso_timestamp(),
            "peopleCount": int(max(0, people_count)),
        }

        if zone_id is not None:
            event["zoneId"] = int(zone_id)

        return event

    def build_queue_event(
        self,
        counter_id: int,
        queue_length: int,
        estimated_wait_time_minutes: int,
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:

        return {
            "storeId": self.store_id,
            "cameraId": self.camera_id,
            "timestamp": timestamp or get_current_iso_timestamp(),
            "queueLength": int(max(0, queue_length)),
            "estimatedWaitTime": float(max(0, estimated_wait_time_minutes)),
            "checkoutCounterId": int(counter_id),
        }

    @staticmethod
    def to_json(
        event_dict: Dict[str, Any],
        indent: Optional[int] = None
    ) -> str:
        """Serialize event dictionary to JSON string."""
        return json.dumps(event_dict, indent=indent)