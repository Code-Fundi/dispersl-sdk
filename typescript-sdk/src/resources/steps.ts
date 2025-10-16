/**
 * Step management resource for task step operations.
 * 
 * This module provides the StepManagementResource class for interacting with
 * the Dispersl API's step management endpoints.
 */

import { Resource } from './base';
import { HTTPClient } from '../http';
import { StepResponse, PaginatedStepResponse, PaginationParams } from '../models';

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
   * Create a new step (stub for testing).
   * 
   * @param data - Step data
   * @returns Created step information
   */
  async create(data: any): Promise<StepResponse> {
    return super.post<StepResponse>('/steps', data);
  }

  /**
   * Get steps by Task ID.
   * 
   * Retrieves steps for a specific task by its ID.
   * 
   * @param taskId - Task ID to retrieve steps for
   * @param params - Pagination parameters
   * @returns Step information with pagination info
   * @throws DisperslError - For various API errors
   */
  async getByTaskId(taskId: string, params?: PaginationParams): Promise<PaginatedStepResponse> {
    return super.get<PaginatedStepResponse>(`/steps/task/${taskId}`, params);
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
