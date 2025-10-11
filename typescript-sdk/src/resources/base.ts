/**
 * Base resource class for API endpoints.
 * 
 * This module provides the base Resource class that all API resource
 * classes inherit from, providing common functionality for making
 * HTTP requests and handling responses.
 */

import { AxiosResponse } from 'axios';
import { DisperslError } from '../exceptions';
import { HTTPClient } from '../http';
import { deserializeResponseData, serializeRequestData } from '../serializers';

export interface RequestOptions {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  params?: Record<string, unknown>;
  data?: unknown;
  headers?: Record<string, string>;
}

/**
 * Base resource class for API endpoints.
 * 
 * Provides common functionality for making HTTP requests and
 * handling responses across all API resources.
 */
export abstract class Resource {
  protected readonly http: HTTPClient;

  constructor(httpClient: HTTPClient) {
    this.http = httpClient;
  }

  /**
   * Make an HTTP request and handle the response.
   * 
   * @param options - Request options
   * @returns Response data
   * @throws DisperslError - For various API errors
   */
  protected async makeRequest<T = unknown>(options: RequestOptions): Promise<T> {
    try {
      // Serialize request data
      let serializedData: unknown;
      if (options.data !== undefined) {
        serializedData = serializeRequestData(options.data);
      }

      // Make the request
      const response: AxiosResponse<T> = await this.http.request({
        method: options.method,
        path: options.path,
        params: options.params,
        data: serializedData,
        headers: options.headers,
      });

      // Deserialize response
      return deserializeResponseData<T>(response.data);

    } catch (error) {
      if (error instanceof DisperslError) {
        throw error;
      }
      const errorMessage = error instanceof Error ? error.message : String(error);
      throw new DisperslError(`Request failed: ${errorMessage}`, { originalError: error as Error });
    }
  }

  /**
   * Make a GET request.
   * 
   * @param path - Request path
   * @param params - Query parameters
   * @param headers - Additional headers
   * @returns Response data
   */
  protected async get<T = unknown>(
    path: string,
    params?: Record<string, unknown>,
    headers?: Record<string, string>
  ): Promise<T> {
    return this.makeRequest<T>({
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
   * @returns Response data
   */
  protected async post<T = unknown>(
    path: string,
    data?: unknown,
    params?: Record<string, unknown>,
    headers?: Record<string, string>
  ): Promise<T> {
    return this.makeRequest<T>({
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
   * @returns Response data
   */
  protected async put<T = unknown>(
    path: string,
    data?: unknown,
    params?: Record<string, unknown>,
    headers?: Record<string, string>
  ): Promise<T> {
    return this.makeRequest<T>({
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
   * @returns Response data
   */
  protected async delete<T = unknown>(
    path: string,
    params?: Record<string, unknown>,
    headers?: Record<string, string>
  ): Promise<T> {
    return this.makeRequest<T>({
      method: 'DELETE',
      path,
      params,
      headers,
    });
  }
}
