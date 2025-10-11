/**
 * Models resource for LLM model management.
 * 
 * This module provides the ModelsResource class for interacting with
 * the Dispersl API's model management endpoints.
 */

import { Resource } from './base';
import { HTTPClient } from '../http';
import { ModelsResponse } from '../models';

/**
 * Resource for LLM model management.
 * 
 * Provides methods for listing available AI models and their specifications.
 */
export class ModelsResource extends Resource {
  constructor(httpClient: HTTPClient) {
    super(httpClient);
  }

  /**
   * List available AI models.
   * 
   * Retrieves all available AI models with their specifications.
   * 
   * @returns List of available models
   * @throws DisperslError - For various API errors
   */
  async list(): Promise<ModelsResponse> {
    return this.get<ModelsResponse>('/models');
  }
}
