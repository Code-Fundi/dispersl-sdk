"""
Test suite for HTTP retry logic.

Tests verify exponential backoff, jitter, circuit breaking,
and proper error handling under various failure scenarios.
"""

import time

import pytest

from dispersl.exceptions import NetworkError, ServerError, TimeoutError
from dispersl.retry import CircuitBreaker, CircuitBreakerOpenError, retry_with_backoff


class TestRetryLogic:
    """
    Tests for retry_with_backoff decorator and related utilities.
    """

    def test_exponential_backoff_timing(self):
        """
        Verify retry delays follow exponential backoff formula.

        Given a backoff_factor of 2.0, delays should be:
        1st retry: ~2s, 2nd retry: ~4s, 3rd retry: ~8s
        """
        call_count = 0

        @retry_with_backoff(max_retries=3, backoff_factor=2.0, jitter=False)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise TimeoutError("Test timeout")
            return "success"

        start_time = time.time()
        result = failing_function()
        end_time = time.time()

        assert result == "success"
        assert call_count == 4  # Initial call + 3 retries

        # Should take approximately 2 + 4 + 8 = 14 seconds
        elapsed = end_time - start_time
        assert 13 <= elapsed <= 15  # Allow some tolerance

    def test_jitter_reduces_thundering_herd(self):
        """
        Verify jitter adds randomization to prevent thundering herd.
        """
        call_times = []

        @retry_with_backoff(max_retries=1, backoff_factor=2.0, jitter=True)
        def failing_function():
            call_times.append(time.time())
            raise TimeoutError("Test timeout")

        with pytest.raises(TimeoutError):
            failing_function()

        # Should have made 2 calls (initial + 1 retry)
        assert len(call_times) == 2

        # Delay should be randomized (not exactly 2 seconds)
        delay = call_times[1] - call_times[0]
        assert 1.0 <= delay <= 3.0  # Jittered range

    def test_retry_on_specific_exceptions(self):
        """
        Verify retries only occur for specified exception types.
        """
        call_count = 0

        @retry_with_backoff(max_retries=2, retry_on_exceptions={TimeoutError, NetworkError})
        def function_with_different_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("Not a retryable error")

        with pytest.raises(ValueError):
            function_with_different_error()

        # Should only make 1 call (no retries for ValueError)
        assert call_count == 1

    def test_retry_on_status_codes(self):
        """
        Verify retries occur for specific HTTP status codes.
        """
        call_count = 0

        @retry_with_backoff(max_retries=2, retry_on_status={500, 502})
        def function_with_server_error():
            nonlocal call_count
            call_count += 1
            from dispersl.exceptions import ServerError

            raise ServerError("Server error", status_code=500)

        with pytest.raises(ServerError):
            function_with_server_error()

        # Should make 3 calls (initial + 2 retries)
        assert call_count == 3

    def test_max_retries_respected(self):
        """
        Verify maximum retry count is respected.
        """
        call_count = 0

        @retry_with_backoff(max_retries=2)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise TimeoutError("Always fails")

        with pytest.raises(TimeoutError):
            always_failing_function()

        # Should make 3 calls (initial + 2 retries)
        assert call_count == 3


class TestCircuitBreaker:
    """
    Tests for CircuitBreaker class.
    """

    def test_circuit_breaker_opens_after_failures(self):
        """
        Verify circuit breaker opens after reaching failure threshold.
        """
        breaker = CircuitBreaker(failure_threshold=2)

        def failing_function():
            raise TimeoutError("Test error")

        # First two failures should be allowed
        with pytest.raises(TimeoutError):
            breaker.call(failing_function)

        with pytest.raises(TimeoutError):
            breaker.call(failing_function)

        # Third failure should open the circuit
        with pytest.raises(CircuitBreakerOpenError):
            breaker.call(failing_function)

    def test_circuit_breaker_resets_after_success(self):
        """
        Verify circuit breaker resets after successful call.
        """
        breaker = CircuitBreaker(failure_threshold=3)

        call_count = 0

        def sometimes_failing_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise TimeoutError("Test error")
            return "success"

        # First two calls should fail but circuit stays closed
        with pytest.raises(TimeoutError):
            breaker.call(sometimes_failing_function)

        with pytest.raises(TimeoutError):
            breaker.call(sometimes_failing_function)

        # Third call should succeed and reset the breaker
        result = breaker.call(sometimes_failing_function)
        assert result == "success"

        # Circuit should be closed again
        assert breaker.get_state() == "closed"
        assert breaker.get_failure_count() == 0

    def test_circuit_breaker_half_open_state(self):
        """
        Verify circuit breaker transitions to half-open state after timeout.
        """
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)

        def failing_function():
            raise TimeoutError("Test error")

        # Cause circuit to open
        with pytest.raises(TimeoutError):
            breaker.call(failing_function)

        assert breaker.get_state() == "open"

        # Wait for recovery timeout
        time.sleep(0.2)

        # Next call should be in half-open state
        with pytest.raises(TimeoutError):
            breaker.call(failing_function)

        # Circuit should be open again
        assert breaker.get_state() == "open"

    def test_circuit_breaker_success_in_half_open(self):
        """
        Verify circuit breaker closes after success in half-open state.
        """
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)

        call_count = 0

        def recovering_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise TimeoutError("Test error")
            return "success"

        # Cause circuit to open
        with pytest.raises(TimeoutError):
            breaker.call(recovering_function)

        # Wait for recovery timeout
        time.sleep(0.2)

        # Next call should succeed and close the circuit
        result = breaker.call(recovering_function)
        assert result == "success"
        assert breaker.get_state() == "closed"
