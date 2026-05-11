"""Leaky bucket rate limiter implementation."""

import time
from dataclasses import dataclass, field

from .base import RateLimiter


@dataclass
class _LeakyState:
    water: float = 0.0
    last_leak: float = field(default_factory=time.time)


class LeakyBucketRateLimiter(RateLimiter):
    """
    Leaky bucket algorithm — a counter-based variant of token bucket.

    Requests add water to the bucket. The bucket leaks at a constant `leak_rate`
    per second. If the bucket overflows (water > capacity) the request is denied.

    Unlike token bucket, this enforces a smooth output rate and does NOT allow
    bursts beyond `capacity`. All excess requests are dropped (no queuing).

    Relationship to token bucket:
        Token bucket  → accumulates allowance over time  (burst-friendly)
        Leaky bucket  → accumulates debt over time       (smooth, strict)
    """

    def __init__(self, capacity: float, leak_rate: float) -> None:
        """
        Args:
            capacity:  Max water level (burst tolerance).
            leak_rate: Water drained per second (= sustained requests/sec allowed).
        """
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if leak_rate <= 0:
            raise ValueError("leak_rate must be positive")

        self._capacity = capacity
        self._leak_rate = leak_rate
        self._buckets: dict[str, _LeakyState] = {}

    def _leak(self, state: _LeakyState, now: float) -> _LeakyState:
        elapsed = now - state.last_leak
        remaining = max(0.0, state.water - elapsed * self._leak_rate)
        return _LeakyState(water=remaining, last_leak=now)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        state = self._buckets.get(key) or _LeakyState()
        state = self._leak(state, now)

        if state.water + 1 <= self._capacity:
            self._buckets[key] = _LeakyState(
                water=state.water + 1,
                last_leak=state.last_leak,
            )
            return True

        self._buckets[key] = state
        return False

    def reset(self, key: str) -> None:
        self._buckets.pop(key, None)
