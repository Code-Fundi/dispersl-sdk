/**
 * History resource for task and step history tracking.
 * 
 * This module provides the HistoryResource class for interacting with
 * the Dispersl API's history endpoints.
 */

import { Resource } from './base';
import { HTTPClient } from '../http';
import { HistoryRequest, HistoryResponse } from '../models';

/**
 * Resource for task and step history tracking.
 * 
 * Provides methods for retrieving task and step history.
 */
export class HistoryResource extends Resource {
  constructor(httpClient: HTTPClient) {
    super(httpClient);
  }

  /**
   * Get task history by ID.
   * 
   * Retrieves the history for a specific task by its ID.
   * 
   * @param taskId - Task ID to retrieve history for
   * @param request - History request parameters
   * @returns Task history
   * @throws DisperslError - For various API errors
   */
  async getTaskHistory(taskId: string, request?: HistoryRequest): Promise<HistoryResponse> {
    return this.get<HistoryResponse>(`/history/task${taskId}`, request);
  }

  /**
   * Get step history by ID.
   * 
   * Retrieves the history for a specific step by its ID.
   * 
   * @param stepId - Step ID to retrieve history for
   * @param request - History request parameters
   * @returns Step history
   * @throws DisperslError - For various API errors
   */
  async getStepHistory(stepId: string, request?: HistoryRequest): Promise<HistoryResponse> {
    return this.get<HistoryResponse>(`/history/step/${stepId}`, request);
  }
}
