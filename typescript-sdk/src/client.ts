/**
 * Main client class for the Dispersl SDK.
 * 
 * This module provides the main Client and AsyncClient classes that serve
 * as the primary interface for interacting with the Dispersl API.
 */

import { AuthHandler, createAuthHandler } from './auth';
import { DisperslError } from './exceptions';
import { HTTPClient, HTTPClientOptions } from './http';
import { AgentsResource } from './resources/agents';
import { AuthenticationResource } from './resources/auth';
import { HistoryResource } from './resources/history';
import { ModelsResource } from './resources/models';
import { StepManagementResource } from './resources/steps';
import { TaskManagementResource } from './resources/tasks';

export interface ClientOptions {
  apiKey?: string;
  baseURL?: string;
  timeout?: number;
  connectTimeout?: number;
  maxRetries?: number;
  backoffFactor?: number;
  headers?: Record<string, string>;
  auth?: string | AuthHandler;
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

  private readonly http: HTTPClient;

  constructor(options: ClientOptions = {}) {
    // Set up authentication
    const auth = createAuthHandler(options.auth || options.apiKey);
    if (!auth) {
      throw new DisperslError(
        'Authentication required. Provide apiKey or auth parameter, ' +
        'or set DISPERSL_API_KEY environment variable.'
      );
    }

    // Prepare headers
    const authHeaders = auth.getHeaders();
    const allHeaders = { ...(options.headers || {}), ...authHeaders };

    // Initialize HTTP client
    const httpOptions: HTTPClientOptions = {
      baseURL: options.baseURL || 'https://api.dispersl.com/v1',
      timeout: options.timeout || 30000,
      connectTimeout: options.connectTimeout || 10000,
      maxRetries: options.maxRetries || 3,
      backoffFactor: options.backoffFactor || 2.0,
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

  private readonly http: HTTPClient;

  constructor(options: ClientOptions = {}) {
    // Set up authentication
    const auth = createAuthHandler(options.auth || options.apiKey);
    if (!auth) {
      throw new DisperslError(
        'Authentication required. Provide apiKey or auth parameter, ' +
        'or set DISPERSL_API_KEY environment variable.'
      );
    }

    // Prepare headers
    const authHeaders = auth.getHeaders();
    const allHeaders = { ...(options.headers || {}), ...authHeaders };

    // Initialize HTTP client
    const httpOptions: HTTPClientOptions = {
      baseURL: options.baseURL || 'https://api.dispersl.com/v1',
      timeout: options.timeout || 30000,
      connectTimeout: options.connectTimeout || 10000,
      maxRetries: options.maxRetries || 3,
      backoffFactor: options.backoffFactor || 2.0,
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
   * Close the client and cleanup resources.
   */
  close(): void {
    this.http.close();
  }
}
