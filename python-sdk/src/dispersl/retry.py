"""
Retry logic with exponential backoff and jitter.

This module provides decorators and utilities for automatic request retries
with enterprise-grade failure handling.
"""

import asyncio
import random
import time
from functools import wraps
from typing import Any, Callable, Optional

from .exceptions import (
    DisperslError,
    NetworkError,
    RateLimitError,
    ServerError,
    TimeoutError,
)


def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    max_backoff: float = 60.0,
    jitter: bool = True,
    retry_on_status: Optional[set[int]] = None,
    retry_on_exceptions: Optional[set[type[Exception]]] = None,
) -> Callable:
    """
    Decorator for retrying failed requests with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff (2.0 = double each time)
        max_backoff: Maximum backoff time in seconds
        jitter: Add randomization to prevent thundering herd
        retry_on_status: HTTP status codes that trigger retry
        retry_on_exceptions: Exception types that trigger retry

    Returns:
        Decorated function with retry logic
    """
    if retry_on_status is None:
        retry_on_status = {408, 429, 500, 502, 503, 504}

    if retry_on_exceptions is None:
        retry_on_exceptions = {
            TimeoutError,
            NetworkError,
            ServerError,
            RateLimitError,
        }

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if we should retry this exception
                    if not _should_retry(e, retry_on_status, retry_on_exceptions):
                        raise

                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        break

                    # Calculate backoff delay
                    delay = _calculate_backoff(attempt, backoff_factor, max_backoff, jitter)

                    # Handle rate limit retry-after
                    if isinstance(e, RateLimitError) and e.retry_after:
                        delay = min(delay, e.retry_after)

                    time.sleep(delay)

            # If we get here, all retries failed
            raise last_exception

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if we should retry this exception
                    if not _should_retry(e, retry_on_status, retry_on_exceptions):
                        raise

                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        break

                    # Calculate backoff delay
                    delay = _calculate_backoff(attempt, backoff_factor, max_backoff, jitter)

                    # Handle rate limit retry-after
                    if isinstance(e, RateLimitError) and e.retry_after:
                        delay = min(delay, e.retry_after)

                    await asyncio.sleep(delay)

            # If we get here, all retries failed
            raise last_exception

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def _should_retry(
    exception: Exception,
    retry_on_status: set[int],
    retry_on_exceptions: set[type[Exception]],
) -> bool:
    """
    Determine if an exception should trigger a retry.

    Args:
        exception: The exception that occurred
        retry_on_status: HTTP status codes that trigger retry
        retry_on_exceptions: Exception types that trigger retry

    Returns:
        True if the exception should trigger a retry
    """
    # Check exception type
    if type(exception) in retry_on_exceptions:
        return True

    # Check if it's a DisperslError with retryable status code
    if isinstance(exception, DisperslError) and exception.status_code:
        return exception.status_code in retry_on_status

    return False


def _calculate_backoff(
    attempt: int,
    backoff_factor: float,
    max_backoff: float,
    jitter: bool,
) -> float:
    """
    Calculate the backoff delay for a given attempt.

    Args:
        attempt: Current attempt number (0-based)
        backoff_factor: Multiplier for exponential backoff
        max_backoff: Maximum backoff time in seconds
        jitter: Whether to add randomization

    Returns:
        Delay in seconds
    """
    # Calculate exponential backoff starting at backoff_factor^1
    delay = backoff_factor ** (attempt + 1)

    # Apply maximum backoff limit
    delay = min(delay, max_backoff)

    # Add jitter to prevent thundering herd
    if jitter:
        # Add random jitter between 0.5x and 1.5x the delay
        jitter_amount = random.uniform(0.5, 1.5)
        delay *= jitter_amount

    return delay


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for preventing cascading failures.

    The circuit breaker monitors the failure rate of operations and opens
    the circuit when the failure threshold is exceeded, preventing further
    calls to the failing service.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type[Exception] = Exception,
    ) -> None:
        """
        Initialize the circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time in seconds before attempting recovery
            expected_exception: Exception type to count as failures
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Execute a function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: When circuit is open
        """
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True

        return time.time() - self.last_failure_time >= self.recovery_timeout

    def _on_success(self) -> None:
        """Handle successful operation."""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self) -> None:
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"

    def get_state(self) -> str:
        """Get the current circuit breaker state."""
        return self.state

    def get_failure_count(self) -> int:
        """Get the current failure count."""
        return self.failure_count


class CircuitBreakerOpenError(DisperslError):
    """Raised when circuit breaker is open and blocking requests."""

    def __init__(self, message: str = "Circuit breaker is open") -> None:
        super().__init__(message)
