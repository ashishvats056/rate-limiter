"""Token bucket rate limiter implementation."""

import time
from dataclasses import dataclass, field

from .base import RateLimiter


@dataclass
class _BucketState:
    tokens: float
    last_refill: float = field(default_factory=time.time)


class TokenBucketRateLimiter(RateLimiter):
    """
    Classic token bucket algorithm.

    A bucket holds up to `capacity` tokens. Tokens are added at `refill_rate`
    per second (up to capacity). Each allowed request consumes one token.
    Bursts up to `capacity` are permitted; sustained rate is `refill_rate` rps.
    """

    def __init__(self, capacity: int, refill_rate: float) -> None:
        """
        Args:
            capacity:    Maximum tokens the bucket can hold (burst size).
            refill_rate: Tokens added per second.
        """
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")

        self._capacity = capacity
        self._refill_rate = refill_rate
        self._buckets: dict[str, _BucketState] = {}

    def _refill(self, state: _BucketState, now: float) -> _BucketState:
        elapsed = now - state.last_refill
        new_tokens = min(self._capacity, state.tokens + elapsed * self._refill_rate)
        return _BucketState(tokens=new_tokens, last_refill=now)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        state = self._buckets.get(key) or _BucketState(tokens=self._capacity)
        state = self._refill(state, now)

        if state.tokens >= 1:
            self._buckets[key] = _BucketState(
                tokens=state.tokens - 1,
                last_refill=state.last_refill,
            )
            return True

        self._buckets[key] = state
        return False

    def reset(self, key: str) -> None:
        self._buckets.pop(key, None)