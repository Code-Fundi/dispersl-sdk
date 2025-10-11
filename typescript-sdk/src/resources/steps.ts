/**
 * Step management resource for task step operations.
 * 
 * This module provides the StepManagementResource class for interacting with
 * the Dispersl API's step management endpoints.
 */

import { Resource } from './base';
import { HTTPClient } from '../http';
import { StepResponse } from '../models';

/**
 * Resource for task step operations.
 * 
 * Provides methods for retrieving and deleting task steps.
 */
export class StepManagementResource extends Resource {
  constructor(httpClient: HTTPClient) {
    super(httpClient);
  }

  /**
   * Get a step by Task ID.
   * 
   * Retrieves a specific step by its Task ID.
   * 
   * @param taskId - Task ID to retrieve steps for
   * @returns Step information
   * @throws DisperslError - For various API errors
   */
  async getByTaskId(taskId: string): Promise<StepResponse> {
    return super.get<StepResponse>(`/steps/task/${taskId}`);
  }

  /**
   * Get a step by ID.
   * 
   * Retrieves a specific step by its ID.
   * 
   * @param stepId - Step ID to retrieve
   * @returns Step information
   * @throws DisperslError - For various API errors
   */
  async getById(stepId: string): Promise<StepResponse> {
    return super.get<StepResponse>(`/steps/${stepId}`);
  }

  /**
   * Cancel a step by ID.
   * 
   * Deletes a specific step by its ID.
   * 
   * @param stepId - Step ID to delete
   * @returns Deletion confirmation
   * @throws DisperslError - For various API errors
   */
  async cancel(stepId: string): Promise<StepResponse> {
    return super.delete<StepResponse>(`/steps/${stepId}/delete`);
  }
}
