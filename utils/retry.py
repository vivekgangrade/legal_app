"""
utils/retry.py — Retry Decorator with Exponential Backoff
==========================================================
Wraps any function so that transient failures (network timeouts,
API rate limits, etc.) are automatically retried instead of crashing.

Source: NEW — neither original project had retry logic.

Usage:
    @retry_on_failure(max_retries=3, backoff_factor=2)
    def call_api():
        ...
"""

import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


def retry_on_failure(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator that retries a function on failure.

    Args:
        max_retries:    How many times to retry before giving up.
        backoff_factor: Multiplier for wait time between retries.
                        Wait = backoff_factor ** attempt (1s, 2s, 4s, …).
        exceptions:     Tuple of exception types to catch and retry on.

    Returns:
        The decorated function with retry behaviour.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as exc:
                    last_exception = exc
                    wait_time = backoff_factor ** attempt

                    if attempt < max_retries:
                        logger.warning(
                            "⚠️  %s failed (attempt %d/%d): %s — retrying in %.1fs",
                            func.__name__,
                            attempt,
                            max_retries,
                            str(exc),
                            wait_time,
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(
                            "❌ %s failed after %d attempts: %s",
                            func.__name__,
                            max_retries,
                            str(exc),
                        )

            # All retries exhausted — raise the last exception
            raise last_exception  # type: ignore[misc]

        return wrapper

    return decorator
