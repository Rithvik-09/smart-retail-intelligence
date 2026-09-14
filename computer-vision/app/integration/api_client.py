"""
REST API Client for Java Spring Boot Ingestion Service.
Asynchronous non-blocking event dispatcher with retry logic and offline buffering.
"""

from collections import deque
import logging
import queue
import threading
import time
from typing import Any, Dict, Optional
import requests

from app.config import BackendConfig

logger = logging.getLogger(__name__)


class BackendAPIClient:
    """Dispatches shopper and queue events to the Java Spring Boot backend via HTTP POST.

    Employs an internal worker thread and queue buffer so that network latency or backend
    downtime never blocks or degrades real-time computer vision frame rates.
    """

    def __init__(self, config: BackendConfig):
        self.base_url = config.base_url.rstrip("/")
        self.shopper_url = f"{self.base_url}{config.shopper_endpoint}"
        self.queue_url = f"{self.base_url}{config.queue_endpoint}"
        self.timeout = config.timeout_seconds
        self.retry_attempts = config.retry_attempts
        self.buffer_size = config.buffer_size

        self._queue: queue.Queue = queue.Queue(maxsize=self.buffer_size)
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

        self._running = True
        self._worker_thread = threading.Thread(
            target=self._worker_loop, daemon=True, name="BackendAPIWorker"
        )
        self._worker_thread.start()
        logger.info(
            f"BackendAPIClient initialized. Target: {self.base_url} "
            f"(timeout={self.timeout}s, buffer={self.buffer_size})"
        )

    def send_shopper_event(self, event: Dict[str, Any]) -> bool:
        """Enqueue shopper event for non-blocking asynchronous transmission."""
        return self._enqueue("shopper", self.shopper_url, event)

    def send_queue_event(self, event: Dict[str, Any]) -> bool:
        """Enqueue checkout queue event for non-blocking asynchronous transmission."""
        return self._enqueue("queue", self.queue_url, event)

    def _enqueue(self, event_type: str, url: str, payload: Dict[str, Any]) -> bool:
        """Add event to background transmission queue without blocking CV loop."""
        try:
            self._queue.put_nowait((event_type, url, payload))
            return True
        except queue.Full:
            # Drop oldest event to prevent memory leaks during prolonged backend downtime
            try:
                _ = self._queue.get_nowait()
                self._queue.put_nowait((event_type, url, payload))
                logger.warning(
                    f"Backend event buffer full ({self.buffer_size}). Dropped oldest event."
                )
                return True
            except Exception:
                return False

    def _post_with_retry(self, url: str, payload: Dict[str, Any]) -> bool:
        """Perform HTTP POST with configured retries and timeout."""
        for attempt in range(1, self.retry_attempts + 1):
            try:
                response = self._session.post(url, json=payload, timeout=self.timeout)
                if response.status_code in (200, 201, 202, 204):
                    logger.debug(f"Event successfully delivered to {url} (HTTP {response.status_code})")
                    return True
                else:
                    logger.warning(
                        f"Backend returned HTTP {response.status_code} from {url}: {response.text[:120]}"
                    )
            except requests.exceptions.RequestException as e:
                if attempt == self.retry_attempts:
                    logger.warning(
                        f"Failed to deliver event to {url} after {self.retry_attempts} attempts: {e}"
                    )
                else:
                    time.sleep(0.3 * attempt)

        return False

    def _worker_loop(self) -> None:
        """Background thread consumer processing queued events."""
        while self._running:
            try:
                item = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            event_type, url, payload = item
            try:
                self._post_with_retry(url, payload)
            except Exception as e:
                logger.error(f"Unexpected error in API worker: {e}")
            finally:
                self._queue.task_done()

    def close(self, timeout: float = 1.0) -> None:
        """Gracefully stop worker thread and close HTTP session."""
        self._running = False
        if self._worker_thread.is_alive():
            self._worker_thread.join(timeout=timeout)
        self._session.close()
        logger.info("BackendAPIClient closed.")
