"""REST Ingestion Client & Mock Backend Server Module.

Provides integration to send AI inventory risk predictions to the Java backend via:
    POST /api/v1/ingestion/inventory-risk

Includes retry logic, batch dispatching, schema validation, and a standalone
mock backend HTTP server for decoupled testing and SIH demonstrations.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import requests


DEFAULT_BACKEND_URL = "http://127.0.0.1:8080"
INGESTION_ENDPOINT = "/api/v1/ingestion/inventory-risk"

REQUIRED_PAYLOAD_FIELDS = {
    "productId",
    "stockoutProbability",
    "riskLevel",
    "anomaly",
    "recommendedAction",
}

VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_RECOMMENDED_ACTIONS = {
    "REPLENISH",
    "EXPEDITE",
    "CYCLE_COUNT_AUDIT",
    "MONITOR",
    "NO_ACTION",
}

logger = logging.getLogger("RESTClient")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def validate_risk_payload(payload: Any) -> Tuple[bool, Optional[str]]:
    """Validate that a payload matches the agreed 5-field inventory risk schema and data types.

    Schema:
        - productId: int
        - stockoutProbability: float/int bounded [0.0, 1.0]
        - riskLevel: str in {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}
        - anomaly: bool
        - recommendedAction: str in {'REPLENISH', 'EXPEDITE', 'CYCLE_COUNT_AUDIT', 'MONITOR', 'NO_ACTION'}

    Returns:
        (True, None) if valid, (False, "error message") otherwise.
    """
    if not isinstance(payload, dict):
        return False, f"Payload must be a JSON object (dict), got {type(payload).__name__}"

    keys = set(payload.keys())
    if keys != REQUIRED_PAYLOAD_FIELDS:
        missing = REQUIRED_PAYLOAD_FIELDS - keys
        extra = keys - REQUIRED_PAYLOAD_FIELDS
        errs = []
        if missing:
            errs.append(f"Missing required fields: {sorted(missing)}")
        if extra:
            errs.append(f"Unexpected extra fields: {sorted(extra)}")
        return False, "; ".join(errs)

    # 1. productId: int (not bool, since bool is a subclass of int in Python)
    p_id = payload["productId"]
    if not isinstance(p_id, int) or isinstance(p_id, bool):
        return False, f"Field 'productId' must be an integer, got {type(p_id).__name__}"

    # 2. stockoutProbability: float (or int 0/1) bounded [0.0, 1.0]
    s_prob = payload["stockoutProbability"]
    if not isinstance(s_prob, (int, float)) or isinstance(s_prob, bool):
        return False, f"Field 'stockoutProbability' must be a numeric float, got {type(s_prob).__name__}"
    if not (0.0 <= s_prob <= 1.0):
        return False, f"Field 'stockoutProbability' must be between 0.0 and 1.0, got {s_prob}"

    # 3. riskLevel: str in VALID_RISK_LEVELS
    r_level = payload["riskLevel"]
    if not isinstance(r_level, str):
        return False, f"Field 'riskLevel' must be a string, got {type(r_level).__name__}"
    if r_level not in VALID_RISK_LEVELS:
        return False, f"Field 'riskLevel' must be one of {sorted(VALID_RISK_LEVELS)}, got '{r_level}'"

    # 4. anomaly: bool
    anom = payload["anomaly"]
    if not isinstance(anom, bool):
        return False, f"Field 'anomaly' must be a boolean, got {type(anom).__name__}"

    # 5. recommendedAction: str in VALID_RECOMMENDED_ACTIONS
    action = payload["recommendedAction"]
    if not isinstance(action, str):
        return False, f"Field 'recommendedAction' must be a string, got {type(action).__name__}"
    if action not in VALID_RECOMMENDED_ACTIONS:
        return False, f"Field 'recommendedAction' must be one of {sorted(VALID_RECOMMENDED_ACTIONS)}, got '{action}'"

    return True, None


class BackendIngestionClient:
    """HTTP client to transmit AI risk assessment results to the Java backend."""

    def __init__(
        self,
        base_url: str = DEFAULT_BACKEND_URL,
        endpoint: str = INGESTION_ENDPOINT,
        timeout: float = 5.0,
        max_retries: int = 2,
    ):
        self.base_url = base_url.rstrip("/")
        self.endpoint = endpoint
        self.full_url = f"{self.base_url}{self.endpoint}"
        self.timeout = timeout
        self.max_retries = max(1, max_retries)
        self.session = requests.Session()

    def send_single(
        self,
        payload: Dict[str, Any],
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Send a single product risk payload to the backend.

        Args:
            payload: Dict containing productId, stockoutProbability, riskLevel, anomaly, recommendedAction.
            dry_run: If True, simulates dispatch without network traffic.

        Returns:
            Dict containing status, status_code, and response body.
        """
        if dry_run:
            logger.info("[DRY-RUN] Dispatched payload for productId %s to %s", payload.get("productId"), self.full_url)
            return {"status": "success", "status_code": 200, "dry_run": True, "payload": payload}

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        last_error = None
        last_status = None
        last_response = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.post(
                    self.full_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                last_status = response.status_code
                last_response = response.text

                logger.info(
                    "POST %s -> Status: %d for productId %s (attempt %d/%d)",
                    self.full_url,
                    response.status_code,
                    payload.get("productId"),
                    attempt,
                    self.max_retries,
                )

                if response.ok:
                    return {
                        "status": "success",
                        "status_code": response.status_code,
                        "response": response.text,
                    }

                # Retry on transient server errors (HTTP 5xx)
                if response.status_code >= 500:
                    last_error = f"Server error {response.status_code}: {response.text}"
                    if attempt < self.max_retries:
                        time.sleep(0.3 * attempt)
                    continue

                # Client-side HTTP 4xx errors - do not retry
                return {
                    "status": "failed",
                    "status_code": response.status_code,
                    "response": response.text,
                }

            except requests.exceptions.RequestException as e:
                last_error = str(e)
                logger.warning(
                    "Attempt %d/%d failed to connect to %s: %s",
                    attempt,
                    self.max_retries,
                    self.full_url,
                    e,
                )
                if attempt < self.max_retries:
                    time.sleep(0.3 * attempt)

        logger.error("Failed to transmit to Java backend after %d attempts: %s", self.max_retries, last_error)
        return {
            "status": "error",
            "status_code": last_status,
            "error": last_error,
            "url": self.full_url,
            "response": last_response,
        }

    def send_batch(
        self,
        payloads: List[Dict[str, Any]],
        dry_run: bool = False,
        item_by_item: bool = False,
    ) -> Dict[str, Any]:
        """Send a batch of product risk assessments.

        Args:
            payloads: List of risk payloads.
            dry_run: Simulate dispatch without network traffic.
            item_by_item: If True, sends individual POST requests per item.
                          If False, sends the list directly as a JSON array.

        Returns:
            Summary dictionary of dispatch results.
        """
        if not payloads:
            return {"total": 0, "successful": 0, "failed": 0, "results": []}

        if item_by_item:
            results = []
            successful = 0
            for item in payloads:
                res = self.send_single(item, dry_run=dry_run)
                results.append(res)
                if res.get("status") == "success":
                    successful += 1
            return {
                "total": len(payloads),
                "successful": successful,
                "failed": len(payloads) - successful,
                "mode": "item_by_item",
                "results": results,
            }

        # Send full batch array in a single POST request
        if dry_run:
            logger.info("[DRY-RUN] Dispatched batch of %d items to %s", len(payloads), self.full_url)
            return {"status": "success", "status_code": 200, "dry_run": True, "total": len(payloads)}

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        last_error = None
        last_status = None
        last_response = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.post(
                    self.full_url,
                    json=payloads,
                    headers=headers,
                    timeout=self.timeout,
                )
                last_status = response.status_code
                last_response = response.text

                logger.info(
                    "POST %s (batch of %d) -> Status: %d (attempt %d/%d)",
                    self.full_url,
                    len(payloads),
                    response.status_code,
                    attempt,
                    self.max_retries,
                )

                if response.ok:
                    return {
                        "status": "success",
                        "status_code": response.status_code,
                        "total": len(payloads),
                        "response": response.text,
                    }

                if response.status_code >= 500:
                    last_error = f"Server error {response.status_code}: {response.text}"
                    if attempt < self.max_retries:
                        time.sleep(0.3 * attempt)
                    continue

                return {
                    "status": "failed",
                    "status_code": response.status_code,
                    "total": len(payloads),
                    "response": response.text,
                }

            except requests.exceptions.RequestException as e:
                last_error = str(e)
                logger.warning(
                    "Attempt %d/%d failed for batch: %s",
                    attempt,
                    self.max_retries,
                    e,
                )
                if attempt < self.max_retries:
                    time.sleep(0.3 * attempt)

        return {
            "status": "error",
            "status_code": last_status,
            "error": last_error,
            "total": len(payloads),
            "response": last_response,
        }


class MockJavaBackendHandler(BaseHTTPRequestHandler):
    """Lightweight mock HTTP handler emulating the Java Spring Boot ingestion endpoint."""

    received_payloads: List[Dict[str, Any]] = []

    def log_message(self, format, *args):
        # Suppress noisy HTTP request logging
        pass

    def do_POST(self):
        if self.path == INGESTION_ENDPOINT or self.path == f"{INGESTION_ENDPOINT}/":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            try:
                data = json.loads(body)
                items = data if isinstance(data, list) else [data]

                # Validate each payload against the strict 5-field schema and types
                for idx, item in enumerate(items):
                    valid, err = validate_risk_payload(item)
                    if not valid:
                        response_err = json.dumps({
                            "status": "REJECTED",
                            "code": 400,
                            "error": f"Invalid payload at index {idx}: {err}",
                        }).encode("utf-8")
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(response_err)))
                        self.end_headers()
                        self.wfile.write(response_err)
                        return

                MockJavaBackendHandler.received_payloads.extend(items)

                response_body = json.dumps({
                    "status": "RECEIVED",
                    "code": 200,
                    "message": "Inventory risk assessment ingested successfully.",
                    "ingestedCount": len(items),
                }).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response_body)))
                self.end_headers()
                self.wfile.write(response_body)
            except Exception as ex:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(ex)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Endpoint not found"}')


class MockBackendServer:
    """Mock server context manager for running an in-memory Java backend emulator."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        self.httpd: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    def start(self):
        MockJavaBackendHandler.received_payloads.clear()
        self.httpd = HTTPServer((self.host, self.port), MockJavaBackendHandler)
        if self.port == 0:
            self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        logger.info("Mock Java Backend Server listening on http://%s:%d%s", self.host, self.port, INGESTION_ENDPOINT)

    def stop(self):
        if self.httpd:
            try:
                self.httpd.shutdown()
            except Exception:
                pass
            try:
                self.httpd.server_close()
            except Exception:
                pass
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=1.0)
            logger.info("Mock Java Backend Server stopped.")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def get_received(self) -> List[Dict[str, Any]]:
        return list(MockJavaBackendHandler.received_payloads)


if __name__ == "__main__":
    sample_payload = {
        "productId": 101,
        "stockoutProbability": 0.87,
        "riskLevel": "HIGH",
        "anomaly": True,
        "recommendedAction": "REPLENISH",
    }
    is_valid, err = validate_risk_payload(sample_payload)
    print(f"Validation: valid={is_valid}, error={err}")

    client = BackendIngestionClient()
    res = client.send_single(sample_payload, dry_run=True)
    print("Dry run response:", res)
