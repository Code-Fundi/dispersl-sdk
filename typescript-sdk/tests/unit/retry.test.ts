/**
 * Test suite for HTTP retry logic.
 * 
 * Tests verify exponential backoff, jitter, circuit breaking,
 * and proper error handling under various failure scenarios.
 */

import { retryWithBackoff, CircuitBreaker, CircuitBreakerOpenError } from '../../src/retry';
import { TimeoutError, NetworkError, ServerError } from '../../src/exceptions';

describe('Retry Logic', () => {
  describe('retryWithBackoff', () => {
    it('should retry with exponential backoff timing', async () => {
      let callCount = 0;
      
      const retryableFunction = retryWithBackoff({
        maxRetries: 3,
        backoffFactor: 2.0,
        jitter: false,
      })(async () => {
        callCount++;
        if (callCount <= 3) {
          throw new TimeoutError('Test timeout');
        }
        return 'success';
      });

      const startTime = Date.now();
      const result = await retryableFunction();
      const endTime = Date.now();

      expect(result).toBe('success');
      expect(callCount).toBe(4); // Initial call + 3 retries

      // Should take approximately 2 + 4 + 8 = 14 seconds
      const elapsed = endTime - startTime;
      expect(elapsed).toBeGreaterThanOrEqual(13000);
      expect(elapsed).toBeLessThanOrEqual(15000);
    });

    it('should add jitter to reduce thundering herd', async () => {
      const callTimes: number[] = [];
      
      const retryableFunction = retryWithBackoff({
        maxRetries: 1,
        backoffFactor: 2.0,
        jitter: true,
      })(async () => {
        callTimes.push(Date.now());
        throw new TimeoutError('Test timeout');
      });

      await expect(retryableFunction()).rejects.toThrow(TimeoutError);

      // Should have made 2 calls (initial + 1 retry)
      expect(callTimes).toHaveLength(2);

      // Delay should be randomized (not exactly 2 seconds)
      const delay = callTimes[1] - callTimes[0];
      expect(delay).toBeGreaterThanOrEqual(1000);
      expect(delay).toBeLessThanOrEqual(3000);
    });

    it('should only retry on specific exceptions', async () => {
      let callCount = 0;
      
      const retryableFunction = retryWithBackoff({
        maxRetries: 2,
        retryOnExceptions: new Set([TimeoutError, NetworkError]),
      })(async () => {
        callCount++;
        throw new Error('Not a retryable error');
      });

      await expect(retryableFunction()).rejects.toThrow('Not a retryable error');

      // Should only make 1 call (no retries for generic Error)
      expect(callCount).toBe(1);
    });

    it('should retry on specific status codes', async () => {
      let callCount = 0;
      
      const retryableFunction = retryWithBackoff({
        maxRetries: 2,
        retryOnStatus: new Set([500, 502]),
      })(async () => {
        callCount++;
        throw new ServerError('Server error', { statusCode: 500 });
      });

      await expect(retryableFunction()).rejects.toThrow(ServerError);

      // Should make 3 calls (initial + 2 retries)
      expect(callCount).toBe(3);
    });

    it('should respect maximum retry count', async () => {
      let callCount = 0;
      
      const retryableFunction = retryWithBackoff({
        maxRetries: 2,
      })(async () => {
        callCount++;
        throw new TimeoutError('Always fails');
      });

      await expect(retryableFunction()).rejects.toThrow(TimeoutError);

      // Should make 3 calls (initial + 2 retries)
      expect(callCount).toBe(3);
    });
  });

  describe('CircuitBreaker', () => {
    it('should open circuit after reaching failure threshold', async () => {
      const breaker = new CircuitBreaker({ failureThreshold: 2 });
      
      const failingFunction = async () => {
        throw new TimeoutError('Test error');
      };

      // First two failures should be allowed
      await expect(breaker.call(failingFunction)).rejects.toThrow(TimeoutError);
      await expect(breaker.call(failingFunction)).rejects.toThrow(TimeoutError);

      // Third failure should open the circuit
      await expect(breaker.call(failingFunction)).rejects.toThrow(CircuitBreakerOpenError);
    });

    it('should reset circuit after successful call', async () => {
      const breaker = new CircuitBreaker({ failureThreshold: 2 });
      
      let callCount = 0;
      
      const sometimesFailingFunction = async () => {
        callCount++;
        if (callCount <= 2) {
          throw new TimeoutError('Test error');
        }
        return 'success';
      };

      // First two calls should fail
      await expect(breaker.call(sometimesFailingFunction)).rejects.toThrow(TimeoutError);
      await expect(breaker.call(sometimesFailingFunction)).rejects.toThrow(TimeoutError);

      // Third call should succeed and reset the breaker
      const result = await breaker.call(sometimesFailingFunction);
      expect(result).toBe('success');

      // Circuit should be closed again
      expect(breaker.getState()).toBe('closed');
      expect(breaker.getFailureCount()).toBe(0);
    });

    it('should transition to half-open state after timeout', async () => {
      const breaker = new CircuitBreaker({ 
        failureThreshold: 1, 
        recoveryTimeout: 100 // 100ms
      });
      
      const failingFunction = async () => {
        throw new TimeoutError('Test error');
      };

      // Cause circuit to open
      await expect(breaker.call(failingFunction)).rejects.toThrow(TimeoutError);
      expect(breaker.getState()).toBe('open');

      // Wait for recovery timeout
      await new Promise(resolve => setTimeout(resolve, 150));

      // Next call should be in half-open state
      await expect(breaker.call(failingFunction)).rejects.toThrow(TimeoutError);

      // Circuit should be open again
      expect(breaker.getState()).toBe('open');
    });

    it('should close circuit after success in half-open state', async () => {
      const breaker = new CircuitBreaker({ 
        failureThreshold: 1, 
        recoveryTimeout: 100 // 100ms
      });
      
      let callCount = 0;
      
      const recoveringFunction = async () => {
        callCount++;
        if (callCount === 1) {
          throw new TimeoutError('Test error');
        }
        return 'success';
      };

      // Cause circuit to open
      await expect(breaker.call(recoveringFunction)).rejects.toThrow(TimeoutError);

      // Wait for recovery timeout
      await new Promise(resolve => setTimeout(resolve, 150));

      // Next call should succeed and close the circuit
      const result = await breaker.call(recoveringFunction);
      expect(result).toBe('success');
      expect(breaker.getState()).toBe('closed');
    });
  });
});
