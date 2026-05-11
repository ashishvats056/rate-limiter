"""Sliding window log rate limiter implementation."""

import time
from collections import deque

from .base import RateLimiter


class SlidingWindowRateLimiter(RateLimiter):
    """
    Allows at most `limit` requests per `window_seconds` using a sliding log.

    Stores a timestamp for every request and evicts those outside the window
    on each call. More accurate than fixed window — no boundary burst problem —
    but uses more memory (O(limit) per key).
    """

    def __init__(self, limit: int, window_seconds: float) -> None:
        if limit <= 0:
            raise ValueError("limit must be a positive integer")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")

        self._limit = limit
        self._window_seconds = window_seconds
        self._logs: dict[str, deque[float]] = {}

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        cutoff = now - self._window_seconds

        log = self._logs.setdefault(key, deque())

        # evict timestamps outside the current window
        while log and log[0] <= cutoff:
            log.popleft()

        if len(log) < self._limit:
            log.append(now)
            return True

        return False

    def reset(self, key: str) -> None:
        self._logs.pop(key, None)