"""
Configuration Loader Module
Loads and validates application settings from YAML and environment variables.
"""

from dataclasses import dataclass, field
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

logger = logging.getLogger(__name__)


@dataclass
class StoreConfig:
    id: int = 1


@dataclass
class CameraConfig:
    id: str = "CAM-01"
    source: Any = 0
    width: int = 1280
    height: int = 720
    fps: int = 30


@dataclass
class ModelConfig:
    path: str = "yolov8n.pt"
    confidence: float = 0.45
    device: str = "auto"
    imgsz: int = 640


@dataclass
class TrackerConfig:
    tracker_type: str = "bytetrack.yaml"


@dataclass
class BackendConfig:
    base_url: str = "http://localhost:8080"
    shopper_endpoint: str = "/api/v1/ingestion/shopper"
    queue_endpoint: str = "/api/v1/ingestion/queue"
    timeout_seconds: float = 3.0
    retry_attempts: int = 2
    buffer_size: int = 100
    emit_interval_seconds: float = 2.0


@dataclass
class LineCrossingConfig:
    enabled: bool = True
    line: List[List[int]] = field(default_factory=lambda: [[100, 360], [1180, 360]])
    entry_direction: str = "down"


@dataclass
class ZoneConfig:
    id: int
    name: str
    polygon: List[List[int]]


@dataclass
class CounterConfig:
    id: int
    name: str
    average_service_time_minutes: float
    polygon: List[List[int]]


@dataclass
class CheckoutConfig:
    counters: List[CounterConfig] = field(default_factory=list)


@dataclass
class CrowdConfig:
    low: int = 5
    medium: int = 10
    high: int = 20


@dataclass
class AppConfig:
    store: StoreConfig = field(default_factory=StoreConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    tracker: TrackerConfig = field(default_factory=TrackerConfig)
    backend: BackendConfig = field(default_factory=BackendConfig)
    line_crossing: LineCrossingConfig = field(default_factory=LineCrossingConfig)
    zones: List[ZoneConfig] = field(default_factory=list)
    checkout: CheckoutConfig = field(default_factory=CheckoutConfig)
    crowd: CrowdConfig = field(default_factory=CrowdConfig)


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """Load and validate configuration from YAML file and environment variables."""
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "config/config.yaml")

    path = Path(config_path)
    if not path.is_file():
        logger.warning(f"Config file not found at {path}. Using default configuration.")
        raw_cfg: Dict[str, Any] = {}
    else:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_cfg = yaml.safe_load(f) or {}
            logger.info(f"Loaded configuration from {path}")
        except Exception as e:
            logger.error(f"Failed to parse config file at {path}: {e}")
            raise

    # Store
    store_data = raw_cfg.get("store", {})
    store_cfg = StoreConfig(id=int(os.getenv("STORE_ID", store_data.get("id", 1))))

    # Camera
    cam_data = raw_cfg.get("camera", {})
    source_val = os.getenv("CAMERA_SOURCE", cam_data.get("source", 0))
    # If source is a digit string, cast to int for webcam index
    if isinstance(source_val, str) and source_val.isdigit():
        source_val = int(source_val)
    cam_cfg = CameraConfig(
        id=str(os.getenv("CAMERA_ID", cam_data.get("id", "CAM-01"))),
        source=source_val,
        width=int(cam_data.get("width", 1280)),
        height=int(cam_data.get("height", 720)),
        fps=int(cam_data.get("fps", 30)),
    )

    # Model
    model_data = raw_cfg.get("model", {})
    model_cfg = ModelConfig(
        path=str(os.getenv("MODEL_PATH", model_data.get("path", "yolov8n.pt"))),
        confidence=float(model_data.get("confidence", 0.45)),
        device=str(os.getenv("MODEL_DEVICE", model_data.get("device", "auto"))),
        imgsz=int(model_data.get("imgsz", 640)),
    )

    # Tracker
    tracker_data = raw_cfg.get("tracker", {})
    tracker_cfg = TrackerConfig(
        tracker_type=str(tracker_data.get("tracker_type", "bytetrack.yaml"))
    )

    # Backend
    backend_data = raw_cfg.get("backend", {})
    backend_cfg = BackendConfig(
        base_url=str(os.getenv("BACKEND_URL", backend_data.get("baseUrl", "http://localhost:8080"))).rstrip("/"),
        shopper_endpoint=str(backend_data.get("shopper_endpoint", "/api/v1/ingestion/shopper")),
        queue_endpoint=str(backend_data.get("queue_endpoint", "/api/v1/ingestion/queue")),
        timeout_seconds=float(backend_data.get("timeout_seconds", 3.0)),
        retry_attempts=int(backend_data.get("retry_attempts", 2)),
        buffer_size=int(backend_data.get("buffer_size", 100)),
        emit_interval_seconds=float(backend_data.get("emit_interval_seconds", 2.0)),
    )

    # Line crossing
    line_data = raw_cfg.get("line_crossing", {})
    line_cfg = LineCrossingConfig(
        enabled=bool(line_data.get("enabled", True)),
        line=line_data.get("line", [[100, 360], [1180, 360]]),
        entry_direction=str(line_data.get("entry_direction", "down")),
    )

    # Zones
    zones_list: List[ZoneConfig] = []
    for z in raw_cfg.get("zones", []):
        zones_list.append(
            ZoneConfig(
                id=int(z.get("id", 0)),
                name=str(z.get("name", f"Zone {z.get('id')}")),
                polygon=z.get("polygon", []),
            )
        )

    # Checkout
    checkout_data = raw_cfg.get("checkout", {})
    counters_list: List[CounterConfig] = []
    for c in checkout_data.get("counters", []):
        counters_list.append(
            CounterConfig(
                id=int(c.get("id", 0)),
                name=str(c.get("name", f"Counter {c.get('id')}")),
                average_service_time_minutes=float(c.get("averageServiceTimeMinutes", 1.2)),
                polygon=c.get("polygon", []),
            )
        )
    checkout_cfg = CheckoutConfig(counters=counters_list)

    # Crowd
    crowd_data = raw_cfg.get("crowd", {})
    crowd_cfg = CrowdConfig(
        low=int(crowd_data.get("low", 5)),
        medium=int(crowd_data.get("medium", 10)),
        high=int(crowd_data.get("high", 20)),
    )

    return AppConfig(
        store=store_cfg,
        camera=cam_cfg,
        model=model_cfg,
        tracker=tracker_cfg,
        backend=backend_cfg,
        line_crossing=line_cfg,
        zones=zones_list,
        checkout=checkout_cfg,
        crowd=crowd_cfg,
    )
