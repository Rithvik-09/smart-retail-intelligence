import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * usePolling Hook
 * Supports recurring polling of real REST endpoints or simulated live telemetry ticks.
 * Maintains realistic "Updated X seconds ago" indicator and controllable intervals.
 */
export function usePolling(callback, intervalMs = 6000, enabled = true) {
  const [lastUpdated, setLastUpdated] = useState(Date.now());
  const [secondsAgo, setSecondsAgo] = useState(0);
  const [isPolling, setIsPolling] = useState(enabled);
  const savedCallback = useRef(callback);

  // Keep ref up to date with latest callback
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Execute tick and update timestamps
  const triggerPoll = useCallback(() => {
    if (savedCallback.current) {
      savedCallback.current();
    }
    setLastUpdated(Date.now());
    setSecondsAgo(0);
  }, []);

  // Main polling interval
  useEffect(() => {
    if (!isPolling) return;

    const id = setInterval(() => {
      triggerPoll();
    }, intervalMs);

    return () => clearInterval(id);
  }, [isPolling, intervalMs, triggerPoll]);

  // Seconds ago live ticker (updates every second)
  useEffect(() => {
    const ticker = setInterval(() => {
      const elapsed = Math.floor((Date.now() - lastUpdated) / 1000);
      setSecondsAgo(elapsed);
    }, 1000);

    return () => clearInterval(ticker);
  }, [lastUpdated]);

  const togglePolling = useCallback(() => {
    setIsPolling(prev => !prev);
  }, []);

  const getRelativeTimeString = useCallback(() => {
    if (secondsAgo <= 1) return 'Updated just now';
    if (secondsAgo < 60) return `Updated ${secondsAgo} seconds ago`;
    const mins = Math.floor(secondsAgo / 60);
    return `Updated ${mins} minute${mins > 1 ? 's' : ''} ago`;
  }, [secondsAgo]);

  return {
    lastUpdated,
    secondsAgo,
    isPolling,
    togglePolling,
    triggerPoll,
    lastUpdatedText: getRelativeTimeString(),
  };
}
