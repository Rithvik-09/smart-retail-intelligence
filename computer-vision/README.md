# Smart Retail Intelligence — Computer Vision Pipeline

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-5.0%2B-green.svg)](https://opencv.org/)
[![Ultralytics YOLO](https://img.shields.io/badge/Ultralytics-YOLOv8-yellow.svg)](https://github.com/ultralytics/ultralytics)
[![Tracking](https://img.shields.io/badge/Tracker-ByteTrack-orange.svg)](https://github.com/ifzhang/ByteTrack)
[![License](https://img.shields.io/badge/Privacy-Preserving-red.svg)](#privacy-guarantees)

**Smart Retail Intelligence** is a privacy-first, real-time computer vision analytics service. It processes live camera footage (laptop webcam, USB cameras, or video files) locally on-device, detecting and tracking shoppers anonymously to generate actionable retail intelligence:
- **Instantaneous & Peak People Count**
- **Virtual Line Crossing (Store Entries & Exits)**
- **Arbitrary Polygonal Zone Occupancy** (e.g., Entrance, Electronics, Grocery)
- **Crowd Level Severity** (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
- **Checkout Queue Detection & Queue Length**
- **Explainable Approximate Waiting Time** ($\text{queueLength} \times \text{averageServiceTime}$)
- **Non-blocking JSON REST Event Dispatch** to Java Spring Boot backend

---

##  Privacy Guarantees

The system is strictly designed with privacy-by-design principles:
- **NO Face Recognition**: Faces are never detected, analyzed, or stored.
- **NO Biometric Tracking**: No facial embeddings, gait analysis, or demographic profiling.
- **Anonymous Ephemeral IDs Only**: People receive temporary numerical IDs (e.g., `ID 17`, `ID 23`) assigned in volatile memory solely for path and line-crossing calculations.
- **Local Raw Video**: Video feeds remain on the local machine and are **never** uploaded to servers or the cloud.
- **Aggregated Telemetry**: Only anonymized metadata and aggregate counts are transmitted to backend REST endpoints.

---

##  System Architecture

```
Webcam / Video File
        │
        ▼
OpenCV Capture Stream (DirectShow / MP4 VideoStream)
        │
        ▼
YOLOv8n Person Detector (Strictly COCO Class 0 — GPU / CUDA Auto-detected)
        │
        ▼
ByteTrack Multi-Object Tracker (Ephemeral Anonymous IDs)
        │
        ▼
Analytics Engine
 ├── People Counter (Instantaneous, Peak, Rolling Avg)
 ├── Line Crossing (Vector Intersection & Debounced Entry/Exit)
 ├── Zone Manager (Point-in-Polygon Occupancy)
 ├── Crowd Classifier (Configurable Severity Thresholds)
 └── Queue Manager (Wait-time Approximation)
        │
        ▼
JSON Event Builder (ISO-8601 UTC Formatted Payloads)
        │
        ▼
Non-blocking Background REST Client (Worker Thread + Bounded Queue Buffer)
        │
        ▼
Java Spring Boot Backend (/api/v1/ingestion/shopper & /api/v1/ingestion/queue)
```

---

## 📂 Project Directory Structure

```
smart-retail-cv/
├── app/
│   ├── __init__.py
│   ├── main.py                     # Main execution loop & HUD overlay
│   ├── config.py                   # Typed configuration loader with env overrides
│   │
│   ├── input/
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract base class FrameStream
│   │   ├── camera.py               # Laptop & USB webcam capture (cv2.CAP_DSHOW)
│   │   ├── video.py                # Local video file reader with looping support
│   │   └── stream_factory.py       # Source resolver (webcam, index, or file)
│   │
│   ├── detection/
│   │   ├── __init__.py
│   │   └── person_detector.py      # YOLOv8n detector filtered strictly to class 0
│   │
│   ├── tracking/
│   │   ├── __init__.py
│   │   └── tracker.py              # ByteTrack integration with anonymous IDs & trails
│   │
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── people_counter.py       # Instantaneous, rolling avg, peak occupancy
│   │   ├── entry_exit.py           # Line crossing vector math & hysteresis debounce
│   │   ├── zones.py                # Arbitrary polygon ray casting for zone occupancy
│   │   ├── crowd.py                # Configurable crowd level classifier (LOW/MED/HIGH/CRIT)
│   │   └── queue.py                # Checkout queue counter & wait-time estimator
│   │
│   ├── events/
│   │   ├── __init__.py
│   │   └── event_builder.py        # Schema-compliant Shopper & Queue JSON builders
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   └── api_client.py           # Resilient non-blocking Spring Boot REST client
│   │
│   └── utils/
│       ├── __init__.py
│       └── fps.py                  # Exponentially smoothed FPS counter
│
├── config/
│   └── config.yaml                 # Store metadata, camera source, zones, queues, backend
│
├── tests/
│   ├── __init__.py
│   ├── test_counter.py             # Unit tests for people counter
│   ├── test_tracker.py             # Unit tests for tracker and anonymous IDs
│   ├── test_entry_exit.py          # Unit tests for virtual line crossing
│   ├── test_zones.py               # Unit tests for polygonal zone occupancy
│   ├── test_crowd.py               # Unit tests for crowd classification
│   ├── test_queue.py               # Unit tests for queue detection & wait times
│   ├── test_events.py              # Unit tests for JSON event schemas
│   └── test_api_client.py          # Unit tests for REST client & offline tolerance
│
├── videos/
│   ├── generate_sample_video.py    # Offline retail floor video generator
│   └── sample_store.mp4            # Generated test video
│
├── requirements.txt                # Pinned dependencies
├── README.md                       # Complete documentation
└── .gitignore
```

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
- Python 3.11 or higher (Python 3.13 tested and verified)
- Built-in laptop camera or external USB webcam
- NVIDIA GPU with CUDA (recommended for 50+ FPS, but automatically falls back to CPU)

### 2. Setup Environment & Dependencies
```powershell
# Clone or navigate to the workspace
cd c:\Users\rehan\Desktop\Aditya

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Running the Pipeline

### Mode 1: Live Laptop Webcam (with visual GUI overlay)
```powershell
python -m app.main --source webcam
```
*Press `q` or `ESC` in the display window to exit.*

### Mode 2: Offline Video File (with visual GUI overlay)
```powershell
python -m app.main --source videos/sample_store.mp4
```

### Mode 3: Headless Mode (Server / Automated Test / CI)
```powershell
python -m app.main --source videos/sample_store.mp4 --no-display --max-frames 60
```

---

## ⚙️ Configuration (`config/config.yaml`)

All parameters are configured via `config/config.yaml` or overridden through environment variables:

```yaml
store:
  id: 1

camera:
  id: "CAM-01"
  source: 0                 # 0 for webcam, or path to MP4
  width: 1280
  height: 720
  fps: 30

model:
  path: "yolov8n.pt"        # Lightweight YOLOv8 nano model
  confidence: 0.45          # Minimum detection confidence
  device: "auto"            # "auto", "cuda", or "cpu"
  imgsz: 640

tracker:
  tracker_type: "bytetrack.yaml"

backend:
  baseUrl: "http://localhost:8080"
  shopper_endpoint: "/api/v1/ingestion/shopper"
  queue_endpoint: "/api/v1/ingestion/queue"
  timeout_seconds: 3.0
  retry_attempts: 2
  buffer_size: 100
  emit_interval_seconds: 2.0  # Dispatch event every 2 seconds

line_crossing:
  enabled: true
  line: [[100, 360], [1180, 360]]
  entry_direction: "down"    # "down" (y increases) or "up"

zones:
  - id: 1
    name: "Entrance"
    polygon: [[50, 50], [500, 50], [500, 350], [50, 350]]
  - id: 2
    name: "Electronics"
    polygon: [[550, 50], [1220, 50], [1220, 350], [550, 350]]

checkout:
  counters:
    - id: 1
      name: "Counter 1"
      averageServiceTimeMinutes: 1.0
      polygon: [[100, 420], [450, 420], [450, 680], [100, 680]]
    - id: 2
      name: "Counter 2"
      averageServiceTimeMinutes: 1.2
      polygon: [[500, 420], [850, 420], [850, 680], [500, 680]]
    - id: 3
      name: "Counter 3"
      averageServiceTimeMinutes: 1.2
      polygon: [[900, 420], [1250, 420], [1250, 680], [900, 680]]

crowd:
  low: 5
  medium: 10
  high: 20
```

---

## 📡 REST API & JSON Event Specifications

The pipeline communicates directly with the Java Spring Boot backend via HTTP POST with `Content-Type: application/json`. **No direct database or PostgreSQL connections are used.**

### 1. Shopper Event (`POST /api/v1/ingestion/shopper`)
Dispatched periodically (every 2.0s):
```json
{
  "storeId": 1,
  "cameraId": "CAM-01",
  "timestamp": "2026-09-06T14:30:00Z",
  "peopleCount": 18,
  "zoneId": 2,
  "entries": 5,
  "exits": 2,
  "crowdLevel": "HIGH"
}
```

### 2. Checkout Queue Event (`POST /api/v1/ingestion/queue`)
Dispatched for each active checkout counter:
```json
{
  "storeId": 1,
  "counterId": 3,
  "queueLength": 12,
  "estimatedWaitTimeMinutes": 14
}
```

#### Wait Time Calculation Formula:
$$\text{estimatedWaitTimeMinutes} = \text{round}(\text{queueLength} \times \text{averageServiceTimeMinutes})$$
*Example: 12 people $\times$ 1.2 min/customer = 14.4 min $\rightarrow$ rounded to 14 minutes.*

---

## 🧪 Automated Testing

The project includes an end-to-end automated test suite built with `pytest`. Tests use mocked coordinates and synthetic frame dimensions—**no physical webcam, video file, or GPU is required to run the tests**.

```powershell
# Run the complete test suite (23 tests)
python -m pytest tests/ -v
```

All 23 unit tests cover:
- Instantaneous count, rolling average, and peak occupancy (`test_counter.py`)
- Anonymous tracking IDs and deterministic color palette (`test_tracker.py`)
- Vector geometry segment intersection, entries, exits, and jitter debounce (`test_entry_exit.py`)
- Arbitrary polygonal zone assignment (`test_zones.py`)
- Configurable crowd severity classification (`test_crowd.py`)
- Multi-counter queue length & explainable wait-time rounding (`test_queue.py`)
- JSON schema contract compliance & ISO-8601 formatting (`test_events.py`)
- REST client HTTP delivery and offline resilience tolerance (`test_api_client.py`)

---

## 🛠️ Reliability & Fault Tolerance

- **Offline Backend Immunity**: If the Java Spring Boot backend is down, slow, or returning errors, the CV pipeline **does not freeze or crash**. Events are queued in a bounded buffer, retried with exponential backoff, and gracefully dropped if full to prevent memory leaks.
- **Camera Fallback**: If the webcam is locked by another application, clear diagnostic error messages are logged.
- **Graceful Shutdown**: Pressing `q` or `ESC` safely stops frame streaming, flushes pending tasks, and releases all video and GPU memory.
