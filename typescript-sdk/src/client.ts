/**
 * Main client class for the Dispersl SDK.
 * 
 * This module provides the main Client and AsyncClient classes that serve
 * as the primary interface for interacting with the Dispersl API.
 */

import { AuthHandler, createAuthHandler } from './auth';
import { AuthenticationError } from './exceptions';
import { HTTPClient, HTTPClientOptions } from './http';
import { AgentsResource } from './resources/agents';
import { AuthenticationResource } from './resources/auth';
import { HistoryResource } from './resources/history';
import { ModelsResource } from './resources/models';
import { StepManagementResource } from './resources/steps';
import { TaskManagementResource } from './resources/tasks';

/**
 * Validate and normalize client options.
 * 
 * @param options - Client options to validate
 * @throws Error - If validation fails
 */
function validateAndNormalizeOptions(options: ClientOptions): {
  apiKey?: string;
  baseUrl: string;
  timeout: number;
  connectTimeout: number;
  maxRetries: number;
  retryBackoffFactor: number;
  debug: boolean;
  proxy?: string;
  userAgent?: string;
} {
  // Validate configuration
  if (options.timeout !== undefined && options.timeout < 0) {
    throw new Error('Timeout must be a positive number');
  }
  if (options.connectTimeout !== undefined && options.connectTimeout < 0) {
    throw new Error('Connect timeout must be a positive number');
  }
  if (options.maxRetries !== undefined && options.maxRetries < 0) {
    throw new Error('Max retries must be a non-negative number');
  }

  // Get API key
  const apiKey = options.apiKey || process.env.DISPERSL_API_KEY;
  
  // Support both baseURL and baseUrl, validate and normalize
  let baseUrl = options.baseUrl || options.baseURL || 'https://api.dispersl.com/v1';
  
  // Validate URL scheme
  if (baseUrl && !baseUrl.match(/^https?:\/\//)) {
    throw new Error('Base URL must include http:// or https:// scheme');
  }
  
  // Remove trailing slash
  baseUrl = baseUrl.replace(/\/$/, '');

  return {
    apiKey,
    baseUrl,
    timeout: options.timeout || 30000,
    connectTimeout: options.connectTimeout || 10000,
    maxRetries: options.maxRetries || 3,
    retryBackoffFactor: options.retryBackoffFactor || options.backoffFactor || 2.0,
    debug: options.debug || false,
    proxy: options.proxy,
    userAgent: options.userAgent,
  };
}

export interface ClientOptions {
  apiKey?: string;
  baseURL?: string;
  baseUrl?: string; // Alias for baseURL
  timeout?: number;
  connectTimeout?: number;
  maxRetries?: number;
  backoffFactor?: number;
  retryBackoffFactor?: number; // Alias for backoffFactor
  headers?: Record<string, string>;
  auth?: string | AuthHandler;
  debug?: boolean;
  proxy?: string;
  userAgent?: string;
}

/**
 * Main client for the Dispersl API.
 * 
 * This client provides a high-level interface for interacting with
 * the Dispersl API, including all available endpoints and resources.
 * 
 * @example
 * ```typescript
 * import { Client } from '@dispersl/sdk';
 * 
 * const client = new Client({ apiKey: 'your_api_key' });
 * const response = await client.agents.chat({ prompt: 'Hello, world!' });
 * ```
 */
export class Client {
  public readonly agents: AgentsResource;
  public readonly models: ModelsResource;
  public readonly auth: AuthenticationResource;
  public readonly tasks: TaskManagementResource;
  public readonly steps: StepManagementResource;
  public readonly history: HistoryResource;

  // Expose configuration properties for testing and debugging
  public readonly apiKey?: string;
  public readonly baseUrl: string;
  public readonly timeout: number;
  public readonly connectTimeout: number;
  public readonly maxRetries: number;
  public readonly retryBackoffFactor: number;
  public readonly debug: boolean;
  public readonly proxy?: string;
  public readonly userAgent?: string;

  private readonly http: HTTPClient;

  constructor(options: ClientOptions = {}) {
    // Set up authentication
    const auth = createAuthHandler(options.auth || options.apiKey);
    if (!auth) {
      throw new AuthenticationError(
        'Authentication required. Provide apiKey or auth parameter, ' +
        'or set DISPERSL_API_KEY environment variable.'
      );
    }

    // Validate and normalize configuration
    const config = validateAndNormalizeOptions(options);
    
    // Store configuration properties
    this.apiKey = config.apiKey;
    this.baseUrl = config.baseUrl;
    this.timeout = config.timeout;
    this.connectTimeout = config.connectTimeout;
    this.maxRetries = config.maxRetries;
    this.retryBackoffFactor = config.retryBackoffFactor;
    this.debug = config.debug;
    this.proxy = config.proxy;
    this.userAgent = config.userAgent;

    // Prepare headers
    const authHeaders = auth.getHeaders();
    const allHeaders = { ...(options.headers || {}), ...authHeaders };

    // Initialize HTTP client
    const httpOptions: HTTPClientOptions = {
      baseURL: this.baseUrl,
      timeout: this.timeout,
      connectTimeout: this.connectTimeout,
      maxRetries: this.maxRetries,
      backoffFactor: this.retryBackoffFactor,
      headers: allHeaders,
    };

    this.http = new HTTPClient(httpOptions);

    // Initialize resources
    this.agents = new AgentsResource(this.http);
    this.models = new ModelsResource(this.http);
    this.auth = new AuthenticationResource(this.http);
    this.tasks = new TaskManagementResource(this.http);
    this.steps = new StepManagementResource(this.http);
    this.history = new HistoryResource(this.http);
  }

  /**
   * Get the SDK version.
   * 
   * @returns SDK version string
   */
  getVersion(): string {
    return '0.1.0';
  }

  /**
   * Get the base URL for API requests.
   * 
   * @returns Base URL string
   */
  getBaseURL(): string {
    return this.http.getBaseURL();
  }

  /**
   * Build a URL with optional query parameters.
   * 
   * @param path - The path to append to base URL
   * @param params - Optional query parameters
   * @returns The built URL
   */
  buildUrl(path: string, params?: Record<string, any>): string {
    let url = `${this.baseUrl}${path}`;
    if (params && Object.keys(params).length > 0) {
      const queryString = Object.entries(params)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');
      url += `?${queryString}`;
    }
    return url;
  }

  /**
   * Verify connection to the API.
   * 
   * @returns True if connection is successful
   */
  async verifyConnection(): Promise<boolean> {
    try {
      await this.http.get('/health');
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Perform a health check on the API.
   * 
   * @returns Health check response
   */
  async healthCheck(): Promise<any> {
    return this.http.get('/health');
  }

  /**
   * Close the client and cleanup resources.
   */
  close(): void {
    this.http.close();
  }
}

/**
 * Async client for the Dispersl API.
 * 
 * This client provides an async interface for interacting with
 * the Dispersl API, supporting async/await patterns.
 * 
 * @example
 * ```typescript
 * import { AsyncClient } from '@dispersl/sdk';
 * 
 * async function main() {
 *   const client = new AsyncClient({ apiKey: 'your_api_key' });
 *   const response = await client.agents.chat({ prompt: 'Hello, world!' });
 * }
 * ```
 */
export class AsyncClient {
  public readonly agents: AgentsResource;
  public readonly models: ModelsResource;
  public readonly auth: AuthenticationResource;
  public readonly tasks: TaskManagementResource;
  public readonly steps: StepManagementResource;
  public readonly history: HistoryResource;

  // Expose configuration properties for testing and debugging
  public readonly apiKey?: string;
  public readonly baseUrl: string;
  public readonly timeout: number;
  public readonly connectTimeout: number;
  public readonly maxRetries: number;
  public readonly retryBackoffFactor: number;
  public readonly debug: boolean;
  public readonly proxy?: string;
  public readonly userAgent?: string;

  private readonly http: HTTPClient;

  constructor(options: ClientOptions = {}) {
    // Set up authentication
    const auth = createAuthHandler(options.auth || options.apiKey);
    if (!auth) {
      throw new AuthenticationError(
        'Authentication required. Provide apiKey or auth parameter, ' +
        'or set DISPERSL_API_KEY environment variable.'
      );
    }

    // Validate and normalize configuration
    const config = validateAndNormalizeOptions(options);
    
    // Store configuration properties
    this.apiKey = config.apiKey;
    this.baseUrl = config.baseUrl;
    this.timeout = config.timeout;
    this.connectTimeout = config.connectTimeout;
    this.maxRetries = config.maxRetries;
    this.retryBackoffFactor = config.retryBackoffFactor;
    this.debug = config.debug;
    this.proxy = config.proxy;
    this.userAgent = config.userAgent;

    // Prepare headers
    const authHeaders = auth.getHeaders();
    const allHeaders = { ...(options.headers || {}), ...authHeaders };

    // Initialize HTTP client
    const httpOptions: HTTPClientOptions = {
      baseURL: this.baseUrl,
      timeout: this.timeout,
      connectTimeout: this.connectTimeout,
      maxRetries: this.maxRetries,
      backoffFactor: this.retryBackoffFactor,
      headers: allHeaders,
    };

    this.http = new HTTPClient(httpOptions);

    // Initialize resources
    this.agents = new AgentsResource(this.http);
    this.models = new ModelsResource(this.http);
    this.auth = new AuthenticationResource(this.http);
    this.tasks = new TaskManagementResource(this.http);
    this.steps = new StepManagementResource(this.http);
    this.history = new HistoryResource(this.http);
  }

  /**
   * Get the SDK version.
   * 
   * @returns SDK version string
   */
  getVersion(): string {
    return '0.1.0';
  }

  /**
   * Get the base URL for API requests.
   * 
   * @returns Base URL string
   */
  getBaseURL(): string {
    return this.http.getBaseURL();
  }

  /**
   * Build a URL with optional query parameters.
   * 
   * @param path - The path to append to base URL
   * @param params - Optional query parameters
   * @returns The built URL
   */
  buildUrl(path: string, params?: Record<string, any>): string {
    let url = `${this.baseUrl}${path}`;
    if (params && Object.keys(params).length > 0) {
      const queryString = Object.entries(params)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');
      url += `?${queryString}`;
    }
    return url;
  }

  /**
   * Verify connection to the API.
   * 
   * @returns True if connection is successful
   */
  async verifyConnection(): Promise<boolean> {
    try {
      await this.http.get('/health');
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Perform a health check on the API.
   * 
   * @returns Health check response
   */
  async healthCheck(): Promise<any> {
    return this.http.get('/health');
  }

  /**
   * Close the client and cleanup resources.
   */
  close(): void {
    this.http.close();
  }
}

// Export Client as Dispersl for backwards compatibility and testing
export { Client as Dispersl };
