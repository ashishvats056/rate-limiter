"""Fixed window rate limiter implementation."""

import time
from dataclasses import dataclass, field

from .base import RateLimiter


@dataclass
class _WindowState:
    count: int = 0
    window_start: float = field(default_factory=time.time)


class FixedWindowRateLimiter(RateLimiter):
    """
    Allows at most `limit` requests per `window_seconds` for each key.

    Simple and fast, but susceptible to burst traffic at window boundaries.
    """

    def __init__(self, limit: int, window_seconds: float) -> None:
        if limit <= 0:
            raise ValueError("limit must be a positive integer")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")

        self._limit = limit
        self._window_seconds = window_seconds
        self._states: dict[str, _WindowState] = {}

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        state = self._states.get(key)

        if state is None or (now - state.window_start) >= self._window_seconds:
            self._states[key] = _WindowState(count=1, window_start=now)
            return True

        if state.count < self._limit:
            self._states[key] = _WindowState(
                count=state.count + 1,
                window_start=state.window_start,
            )
            return True

        return False

    def reset(self, key: str) -> None:
        self._states.pop(key, None)