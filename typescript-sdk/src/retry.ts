/**
 * Retry logic with exponential backoff and jitter.
 * 
 * This module provides utilities for automatic request retries
 * with enterprise-grade failure handling.
 */

import {
  CircuitBreakerOpenError,
  DisperslError,
  NetworkError,
  RateLimitError,
  ServerError,
  TimeoutError,
} from './exceptions';

export { CircuitBreakerOpenError };

export interface RetryOptions {
  maxRetries?: number;
  backoffFactor?: number;
  maxBackoff?: number;
  jitter?: boolean;
  retryOnStatus?: Set<number>;
  retryOnExceptions?: Set<new (...args: any[]) => Error>;
}

export interface CircuitBreakerOptions {
  failureThreshold?: number;
  recoveryTimeout?: number;
  expectedException?: new (...args: any[]) => Error;
}

/**
 * Default retry configuration
 */
const DEFAULT_RETRY_OPTIONS: Required<RetryOptions> = {
  maxRetries: 3,
  backoffFactor: 2.0,
  maxBackoff: 60.0,
  jitter: true,
  retryOnStatus: new Set([408, 429, 500, 502, 503, 504]),
  retryOnExceptions: new Set([TimeoutError, NetworkError, ServerError, RateLimitError]),
};

/**
 * Decorator for retrying failed requests with exponential backoff.
 * 
 * @param options - Retry configuration options
 * @returns Decorated function with retry logic
 */
export function retryWithBackoff<T extends (...args: any[]) => Promise<any>>(
  options: RetryOptions = {}
): (fn: T) => T {
  const config = { ...DEFAULT_RETRY_OPTIONS, ...options };

  return function (fn: T): T {
    return (async (...args: Parameters<T>): Promise<Awaited<ReturnType<T>>> => {
      let lastError: Error | undefined;

      for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
        try {
          return await fn(...args);
        } catch (error) {
          lastError = error as Error;

          // Check if we should retry this error
          if (!shouldRetry(error as Error, config)) {
            throw error;
          }

          // Don't retry on the last attempt
          if (attempt === config.maxRetries) {
            break;
          }

          // Calculate backoff delay
          const delay = calculateBackoff(
            attempt,
            config.backoffFactor,
            config.maxBackoff,
            config.jitter
          );

          // Handle rate limit retry-after
          if (error instanceof RateLimitError && error.retryAfter) {
            const actualDelay = Math.min(delay, error.retryAfter * 1000);
            await sleep(actualDelay);
          } else {
            await sleep(delay);
          }
        }
      }

      // If we get here, all retries failed
      throw lastError;
    }) as T;
  };
}

/**
 * Determine if an error should trigger a retry.
 * 
 * @param error - The error that occurred
 * @param config - Retry configuration
 * @returns True if the error should trigger a retry
 */
function shouldRetry(error: Error, config: Required<RetryOptions>): boolean {
  // Check exception type
  if (config.retryOnExceptions.has(error.constructor as any)) {
    return true;
  }

  // Check if it's a DisperslError with retryable status code
  if (error instanceof DisperslError && error.statusCode) {
    return config.retryOnStatus.has(error.statusCode);
  }

  return false;
}

/**
 * Calculate the backoff delay for a given attempt.
 * 
 * @param attempt - Current attempt number (0-based)
 * @param backoffFactor - Multiplier for exponential backoff
 * @param maxBackoff - Maximum backoff time in milliseconds
 * @param jitter - Whether to add randomization
 * @returns Delay in milliseconds
 */
function calculateBackoff(
  attempt: number,
  backoffFactor: number,
  maxBackoff: number,
  jitter: boolean
): number {
  // Calculate exponential backoff starting at backoffFactor^1
  let delay = Math.pow(backoffFactor, attempt + 1) * 1000; // Convert to milliseconds

  // Apply maximum backoff limit
  delay = Math.min(delay, maxBackoff * 1000);

  // Add jitter to prevent thundering herd
  if (jitter) {
    // Add random jitter between 0.5x and 1.5x the delay
    const jitterAmount = 0.5 + Math.random();
    delay *= jitterAmount;
  }

  return delay;
}

/**
 * Sleep for the specified number of milliseconds.
 * 
 * @param ms - Milliseconds to sleep
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Circuit breaker pattern implementation for preventing cascading failures.
 * 
 * The circuit breaker monitors the failure rate of operations and opens
 * the circuit when the failure threshold is exceeded, preventing further
 * calls to the failing service.
 */
export class CircuitBreaker {
  private failureCount = 0;
  private lastFailureTime?: number;
  private state: 'closed' | 'open' | 'half-open' = 'closed';
  private readonly failureThreshold: number;
  private readonly recoveryTimeout: number;
  private readonly expectedException: new (...args: any[]) => Error;

  constructor(options: CircuitBreakerOptions | number = {}) {
    if (typeof options === 'number') {
      this.failureThreshold = options;
      this.recoveryTimeout = 60000;
      this.expectedException = Error;
    } else {
      this.failureThreshold = options.failureThreshold ?? 5;
      this.recoveryTimeout = options.recoveryTimeout ?? 60000;
      this.expectedException = options.expectedException ?? Error;
    }
  }

  /**
   * Execute a function with circuit breaker protection.
   * 
   * @param fn - Function to execute
   * @param args - Function arguments
   * @returns Function result
   * @throws CircuitBreakerOpenError - When circuit is open
   */
  async call<T extends (...args: any[]) => Promise<any>>(
    fn: T,
    ...args: Parameters<T>
  ): Promise<Awaited<ReturnType<T>>> {
    if (this.state === 'open') {
      if (this.shouldAttemptReset()) {
        this.state = 'half-open';
      } else {
        throw new CircuitBreakerOpenError('Circuit breaker is open');
      }
    }

    try {
      const result = await fn(...args);
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  /**
   * Check if enough time has passed to attempt reset.
   */
  private shouldAttemptReset(): boolean {
    if (!this.lastFailureTime) {
      return true;
    }

    return Date.now() - this.lastFailureTime >= this.recoveryTimeout;
  }

  /**
   * Handle successful operation.
   */
  private onSuccess(): void {
    this.failureCount = 0;
    this.state = 'closed';
  }

  /**
   * Handle failed operation.
   */
  private onFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.failureCount >= this.failureThreshold) {
      this.state = 'open';
    }
  }

  /**
   * Get the current circuit breaker state.
   */
  getState(): 'closed' | 'open' | 'half-open' {
    return this.state;
  }

  /**
   * Get the current failure count.
   */
  getFailureCount(): number {
    return this.failureCount;
  }
}

/**
 * Retry configuration presets for common scenarios.
 */
export const RetryPresets = {
  /**
   * Conservative retry configuration for critical operations.
   */
  conservative: {
    maxRetries: 2,
    backoffFactor: 2.0,
    maxBackoff: 30.0,
    jitter: true,
  } as RetryOptions,

  /**
   * Aggressive retry configuration for non-critical operations.
   */
  aggressive: {
    maxRetries: 5,
    backoffFactor: 1.5,
    maxBackoff: 120.0,
    jitter: true,
  } as RetryOptions,

  /**
   * Fast retry configuration for quick operations.
   */
  fast: {
    maxRetries: 3,
    backoffFactor: 1.2,
    maxBackoff: 10.0,
    jitter: false,
  } as RetryOptions,
} as const;
