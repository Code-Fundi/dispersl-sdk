/**
 * Authentication resource for API key management.
 * 
 * This module provides the AuthenticationResource class for interacting with
 * the Dispersl API's authentication endpoints.
 */

import { Resource } from './base';
import { HTTPClient } from '../http';
import { APIKeysResponse, NewAPIKeyRequest, NewAPIKeyResponse } from '../models';

/**
 * Resource for API key management.
 * 
 * Provides methods for retrieving and generating API keys.
 */
export class AuthenticationResource extends Resource {
  constructor(httpClient: HTTPClient) {
    super(httpClient);
  }

  /**
   * Get API keys.
   * 
   * Retrieves API keys for the authenticated user.
   * 
   * @returns List of API keys
   * @throws DisperslError - For various API errors
   */
  async getKeys(): Promise<APIKeysResponse> {
    return this.get<APIKeysResponse>('/keys');
  }

  /**
   * Generate new API key.
   * 
   * Generates new API key pair for the specified user.
   * 
   * @param request - New API key request parameters
   * @returns Generated API key information
   * @throws DisperslError - For various API errors
   */
  async generateNewKey(request: NewAPIKeyRequest): Promise<NewAPIKeyResponse> {
    return this.post<NewAPIKeyResponse>('/keys/new', request);
  }
}
