"""
Unit tests for resilient Spring Boot REST API client.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import time
from app.config import BackendConfig
from app.integration.api_client import BackendAPIClient


class MockBackendHandler(BaseHTTPRequestHandler):
    received_events = []

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        payload = json.loads(post_data.decode("utf-8"))
        MockBackendHandler.received_events.append({"path": self.path, "data": payload})

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"SUCCESS"}')

    def log_message(self, format, *args):
        pass  # Suppress console logs during tests


def test_api_client_successful_delivery():
    MockBackendHandler.received_events.clear()

    # Start mock server on ephemeral port
    server = HTTPServer(("127.0.0.1", 0), MockBackendHandler)
    port = server.server_address[1]
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        cfg = BackendConfig(
            base_url=f"http://127.0.0.1:{port}",
            shopper_endpoint="/api/v1/ingestion/shopper",
            queue_endpoint="/api/v1/ingestion/queue",
            timeout_seconds=1.0,
            retry_attempts=1,
            buffer_size=10,
        )
        client = BackendAPIClient(cfg)

        shopper_payload = {"storeId": 1, "peopleCount": 5}
        queue_payload = {"storeId": 1, "counterId": 2, "queueLength": 3}

        client.send_shopper_event(shopper_payload)
        client.send_queue_event(queue_payload)

        # Wait briefly for worker thread to dispatch
        time.sleep(0.5)

        assert len(MockBackendHandler.received_events) == 2
        assert MockBackendHandler.received_events[0]["path"] == "/api/v1/ingestion/shopper"
        assert MockBackendHandler.received_events[0]["data"]["peopleCount"] == 5
        assert MockBackendHandler.received_events[1]["path"] == "/api/v1/ingestion/queue"
        assert MockBackendHandler.received_events[1]["data"]["counterId"] == 2

        client.close()
    finally:
        server.shutdown()
        server.server_close()


def test_api_client_resilience_when_backend_offline():
    # Target port that is not listening
    cfg = BackendConfig(
        base_url="http://127.0.0.1:59999",
        timeout_seconds=0.2,
        retry_attempts=1,
        buffer_size=5,
    )
    client = BackendAPIClient(cfg)

    # Calling send when offline MUST NOT raise exceptions or crash
    ok1 = client.send_shopper_event({"storeId": 1, "peopleCount": 10})
    ok2 = client.send_queue_event({"storeId": 1, "counterId": 1, "queueLength": 2})

    assert ok1 is True
    assert ok2 is True

    # Sleep briefly to let worker attempt delivery and log warning without crashing
    time.sleep(0.4)
    client.close()
