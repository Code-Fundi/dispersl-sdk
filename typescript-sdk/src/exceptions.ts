/**
 * Custom exceptions for the Dispersl SDK.
 * 
 * This module defines the exception hierarchy used throughout the SDK
 * for consistent error handling and user experience.
 */

export interface ErrorDetails {
  code?: number;
  message: string;
}

export interface DisperslErrorOptions {
  statusCode?: number;
  requestId?: string;
  responseBody?: unknown;
  timestamp?: Date;
  originalError?: Error;
}

/**
 * Base exception class for all Dispersl SDK errors.
 * 
 * All custom exceptions inherit from this class to provide
 * consistent error handling across the SDK.
 */
export class DisperslError extends Error {
  public override readonly message: string;
  public readonly statusCode?: number;
  public readonly requestId?: string;
  public readonly responseBody?: unknown;
  public readonly timestamp: Date;
  public readonly originalError?: Error;

  constructor(
    message: string,
    options: DisperslErrorOptions = {}
  ) {
    super(message);
    this.name = 'DisperslError';
    this.message = message;
    this.statusCode = options.statusCode;
    this.requestId = options.requestId;
    this.responseBody = options.responseBody;
    this.timestamp = options.timestamp || new Date();
    this.originalError = options.originalError;

    // Ensure the stack trace points to the correct location
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, DisperslError);
    }
  }

  override toString(): string {
    const parts = [this.message];
    if (this.statusCode) {
      parts.push(`Status: ${this.statusCode}`);
    }
    if (this.requestId) {
      parts.push(`Request ID: ${this.requestId}`);
    }
    return parts.join(' | ');
  }
}

/**
 * Raised when authentication fails (401, 403).
 * 
 * This includes invalid API keys, expired tokens,
 * and insufficient permissions.
 */
export class AuthenticationError extends DisperslError {
  constructor(
    message: string = 'Authentication failed',
    options: DisperslErrorOptions = {}
  ) {
    super(message, options);
    this.name = 'AuthenticationError';
  }
}

/**
 * Raised when a requested resource is not found (404).
 * 
 * This includes invalid task IDs, step IDs, or other
 * resource identifiers.
 */
export class NotFoundError extends DisperslError {
  constructor(
    message: string = 'Resource not found',
    options: DisperslErrorOptions = {}
  ) {
    super(message, options);
    this.name = 'NotFoundError';
  }
}

/**
 * Raised when request validation fails (400, 422).
 * 
 * This includes malformed requests, missing required fields,
 * and invalid parameter values.
 */
export class ValidationError extends DisperslError {
  public readonly validationErrors?: Record<string, unknown>;

  constructor(
    message: string = 'Request validation failed',
    options: DisperslErrorOptions & { validationErrors?: Record<string, unknown> } = {}
  ) {
    super(message, options);
    this.name = 'ValidationError';
    this.validationErrors = options.validationErrors;
  }
}

/**
 * Raised when rate limits are exceeded (429).
 * 
 * Includes retry-after information for proper backoff.
 */
export class RateLimitError extends DisperslError {
  public readonly retryAfter?: number;

  constructor(
    message: string = 'Rate limit exceeded',
    options: DisperslErrorOptions & { retryAfter?: number } = {}
  ) {
    super(message, options);
    this.name = 'RateLimitError';
    this.retryAfter = options.retryAfter;
  }
}

/**
 * Raised when server errors occur (500-599).
 * 
 * This includes internal server errors, service unavailable,
 * and gateway timeouts.
 */
export class ServerError extends DisperslError {
  constructor(
    message: string = 'Server error occurred',
    options: DisperslErrorOptions = {}
  ) {
    super(message, options);
    this.name = 'ServerError';
  }
}

/**
 * Raised when requests timeout.
 * 
 * This includes connection timeouts, read timeouts,
 * and total request timeouts.
 */
export class TimeoutError extends DisperslError {
  public readonly timeoutType?: string;

  constructor(
    message: string = 'Request timeout',
    options: DisperslErrorOptions & { timeoutType?: string } = {}
  ) {
    super(message, options);
    this.name = 'TimeoutError';
    this.timeoutType = options.timeoutType;
  }
}

/**
 * Raised when network-related errors occur.
 * 
 * This includes connection failures, DNS resolution errors,
 * and other network issues.
 */
export class NetworkError extends DisperslError {
  constructor(
    message: string = 'Network error occurred',
    options: DisperslErrorOptions = {}
  ) {
    super(message, options);
    this.name = 'NetworkError';
  }
}

/**
 * Raised when serialization/deserialization fails.
 * 
 * This includes JSON parsing errors, invalid data formats,
 * and encoding/decoding issues.
 */
export class SerializationError extends DisperslError {
  constructor(
    message: string = 'Serialization error',
    options: DisperslErrorOptions = {}
  ) {
    super(message, options);
    this.name = 'SerializationError';
  }
}

/**
 * Raised when circuit breaker is open and blocking requests.
 */
export class CircuitBreakerOpenError extends DisperslError {
  constructor(message: string = 'Circuit breaker is open') {
    super(message);
    this.name = 'CircuitBreakerOpenError';
  }
}
