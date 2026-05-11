"""Abstract base class for rate limiters."""

from abc import ABC, abstractmethod


class RateLimiter(ABC):
    """Base interface for all rate limiter implementations."""

    @abstractmethod
    def is_allowed(self, key: str) -> bool:
        """Return True if the request for the given key is allowed."""
        ...

    @abstractmethod
    def reset(self, key: str) -> None:
        """Reset the state for a given key."""
        ...