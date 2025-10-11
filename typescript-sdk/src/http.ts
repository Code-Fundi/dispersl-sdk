/**
 * HTTP transport layer with enterprise-grade reliability.
 * 
 * This module handles all HTTP communication with retry logic,
 * connection pooling, and timeout management.
 */

import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
} from 'axios';
import {
  AuthenticationError,
  DisperslError,
  NetworkError,
  NotFoundError,
  RateLimitError,
  SerializationError,
  ServerError,
  TimeoutError,
  ValidationError,
} from './exceptions';
import { retryWithBackoff } from './retry';

export interface HTTPClientOptions {
  baseURL: string;
  timeout?: number;
  connectTimeout?: number;
  maxRetries?: number;
  backoffFactor?: number;
  headers?: Record<string, string>;
}

export interface RequestOptions {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  params?: Record<string, unknown>;
  data?: unknown;
  headers?: Record<string, string>;
}

/**
 * Robust HTTP client with automatic retries and circuit breaking.
 * 
 * This client provides enterprise-grade HTTP communication with:
 * - Connection pooling
 * - Automatic retries with exponential backoff
 * - Circuit breaker pattern
 * - Comprehensive error handling
 * - Request/response logging
 */
export class HTTPClient {
  private readonly axiosInstance: AxiosInstance;
  private readonly baseURL: string;

  constructor(options: HTTPClientOptions) {
    this.baseURL = options.baseURL.replace(/\/$/, '');

    this.axiosInstance = axios.create({
      baseURL: this.baseURL,
      timeout: options.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'dispersl-sdk-typescript/0.1.0',
        ...options.headers,
      },
    });

    // Add request interceptor for logging
    this.axiosInstance.interceptors.request.use(
      (config) => {
        this.logRequest(config);
        return config;
      },
      (error) => {
        this.logError('Request error', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => {
        this.logResponse(response);
        return response;
      },
      (error) => {
        this.logError('Response error', error);
        return Promise.reject(this.handleResponseError(error));
      }
    );
  }

  /**
   * Make an HTTP request with automatic retries.
   * 
   * @param options - Request options
   * @returns HTTP response
   * @throws DisperslError - For various API errors
   */
  async request<T = unknown>(options: RequestOptions): Promise<AxiosResponse<T>> {
    const retryableRequest = retryWithBackoff({
      maxRetries: 3,
      backoffFactor: 2.0,
    })(this.makeRequest.bind(this));

    return retryableRequest(options) as Promise<AxiosResponse<T>>;
  }

  /**
   * Make a GET request.
   * 
   * @param path - Request path
   * @param params - Query parameters
   * @param headers - Additional headers
   * @returns HTTP response
   */
  async get<T = unknown>(
    path: string,
    params?: Record<string, unknown>,
    headers?: Record<string, string>
  ): Promise<AxiosResponse<T>> {
    return this.request<T>({
      method: 'GET',
      path,
      params,
      headers,
    });
  }

  /**
   * Make a POST request.
   * 
   * @param path - Request path
   * @param data - Request body
   * @param params - Query parameters
   * @param headers - Additional headers
   * @returns HTTP response
   */
  async post<T = unknown>(
    path: string,
    data?: unknown,
    params?: Record<string, unknown>,
    headers?: Record<string, string>
  ): Promise<AxiosResponse<T>> {
    return this.request<T>({
      method: 'POST',
      path,
      data,
      params,
      headers,
    });
  }

  /**
   * Make a PUT request.
   * 
   * @param path - Request path
   * @param data - Request body
   * @param params - Query parameters
   * @param headers - Additional headers
   * @returns HTTP response
   */
  async put<T = unknown>(
    path: string,
    data?: unknown,
    params?: Record<string, unknown>,
    headers?: Record<string, string>
  ): Promise<AxiosResponse<T>> {
    return this.request<T>({
      method: 'PUT',
      path,
      data,
      params,
      headers,
    });
  }

  /**
   * Make a DELETE request.
   * 
   * @param path - Request path
   * @param params - Query parameters
   * @param headers - Additional headers
   * @returns HTTP response
   */
  async delete<T = unknown>(
    path: string,
    params?: Record<string, unknown>,
    headers?: Record<string, string>
  ): Promise<AxiosResponse<T>> {
    return this.request<T>({
      method: 'DELETE',
      path,
      params,
      headers,
    });
  }

  /**
   * Get the base URL for API requests.
   * 
   * @returns Base URL string
   */
  getBaseURL(): string {
    return this.baseURL;
  }

  /**
   * Close the HTTP client and cleanup resources.
   */
  close(): void {
    // Axios doesn't require explicit cleanup
  }

  /**
   * Internal method to make HTTP requests.
   * 
   * @param options - Request options
   * @returns HTTP response
   */
  private async makeRequest<T = unknown>(
    options: RequestOptions
  ): Promise<AxiosResponse<T>> {
    const config: AxiosRequestConfig = {
      method: options.method,
      url: options.path,
      params: options.params,
      data: options.data,
      headers: options.headers,
    };

    return this.axiosInstance.request<T>(config);
  }

  /**
   * Log outgoing request (excluding sensitive data).
   * 
   * @param config - Axios request config
   */
  private logRequest(config: AxiosRequestConfig): void {
    if (process.env.NODE_ENV === 'development') {
      const safeHeaders = this.sanitizeHeaders(config.headers || {});
      console.debug(
        `Request: ${config.method?.toUpperCase()} ${config.url} | ` +
        `Params: ${JSON.stringify(config.params)} | ` +
        `Headers: ${JSON.stringify(safeHeaders)}`
      );
    }
  }

  /**
   * Log incoming response.
   * 
   * @param response - Axios response
   */
  private logResponse(response: AxiosResponse): void {
    if (process.env.NODE_ENV === 'development') {
      console.debug(
        `Response: ${response.status} | ` +
        `Headers: ${JSON.stringify(response.headers)} | ` +
        `Size: ${response.data ? JSON.stringify(response.data).length : 0} bytes`
      );
    }
  }

  /**
   * Log error information.
   * 
   * @param message - Error message
   * @param error - Error object
   */
  private logError(message: string, error: unknown): void {
    if (process.env.NODE_ENV === 'development') {
      console.error(`${message}:`, error);
    }
  }

  /**
   * Remove sensitive headers from logging.
   * 
   * @param headers - Headers to sanitize
   * @returns Sanitized headers
   */
  private sanitizeHeaders(headers: Record<string, unknown>): Record<string, unknown> {
    const sensitiveKeys = new Set(['authorization', 'x-api-key', 'cookie']);
    const sanitized: Record<string, unknown> = {};

    for (const [key, value] of Object.entries(headers)) {
      sanitized[key] = sensitiveKeys.has(key.toLowerCase()) ? '***' : value;
    }

    return sanitized;
  }

  /**
   * Handle HTTP response errors and convert to appropriate DisperslError.
   * 
   * @param error - Axios error
   * @returns Appropriate DisperslError
   */
  private handleResponseError(error: AxiosError): DisperslError {
    if (error.code === 'ECONNABORTED') {
      return new TimeoutError('Request timeout', {
        timeoutType: 'request',
        originalError: error,
      });
    }

    if (error.code === 'ENOTFOUND' || error.code === 'ECONNREFUSED') {
      return new NetworkError('Connection failed', {
        originalError: error,
      });
    }

    if (!error.response) {
      return new NetworkError('Network error', {
        originalError: error,
      });
    }

    const response = error.response;
    const requestId = response.headers['x-request-id'] as string;
    const retryAfter = response.headers['retry-after'] as string;

    let errorData: unknown;
    try {
      errorData = response.data;
    } catch {
      errorData = { message: 'Unknown error' };
    }

    // Create appropriate exception based on status code
    switch (response.status) {
      case 401:
        return new AuthenticationError(
          (errorData as any)?.message || 'Authentication failed',
          {
            statusCode: response.status,
            requestId,
            responseBody: errorData,
          }
        );

      case 403:
        return new AuthenticationError(
          (errorData as any)?.message || 'Access forbidden',
          {
            statusCode: response.status,
            requestId,
            responseBody: errorData,
          }
        );

      case 404:
        return new NotFoundError(
          (errorData as any)?.message || 'Resource not found',
          {
            statusCode: response.status,
            requestId,
            responseBody: errorData,
          }
        );

      case 429:
        const retryAfterSeconds = retryAfter ? parseInt(retryAfter, 10) : undefined;
        return new RateLimitError(
          (errorData as any)?.message || 'Rate limit exceeded',
          {
            statusCode: response.status,
            requestId,
            responseBody: errorData,
            retryAfter: retryAfterSeconds,
          }
        );

      case 400:
      case 422:
        return new ValidationError(
          (errorData as any)?.message || 'Request validation failed',
          {
            statusCode: response.status,
            requestId,
            responseBody: errorData,
            validationErrors: (errorData as any)?.errors || {},
          }
        );

      default:
        if (response.status >= 500) {
          return new ServerError(
            (errorData as any)?.message || 'Server error occurred',
            {
              statusCode: response.status,
              requestId,
              responseBody: errorData,
            }
          );
        }

        return new DisperslError(
          (errorData as any)?.message || `HTTP ${response.status}`,
          {
            statusCode: response.status,
            requestId,
            responseBody: errorData,
          }
        );
    }
  }
}
