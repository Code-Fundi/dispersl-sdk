/**
 * Task management resource for task lifecycle management.
 * 
 * This module provides the TaskManagementResource class for interacting with
 * the Dispersl API's task management endpoints.
 */

import { Resource } from './base';
import { HTTPClient } from '../http';
import { TaskEditRequest, TaskResponse } from '../models';

/**
 * Resource for task lifecycle management.
 * 
 * Provides methods for creating, editing, retrieving, and deleting tasks.
 */
export class TaskManagementResource extends Resource {
  constructor(httpClient: HTTPClient) {
    super(httpClient);
  }

  /**
   * Create a new task.
   * 
   * Creates a new task for the authenticated user.
   * 
   * @returns Created task information
   * @throws DisperslError - For various API errors
   */
  async create(): Promise<TaskResponse> {
    return this.post<TaskResponse>('/tasks/new');
  }

  /**
   * Edit a task by ID.
   * 
   * Edits a specific task by its ID.
   * 
   * @param taskId - Task ID to edit
   * @param request - Task edit request parameters
   * @returns Updated task information
   * @throws DisperslError - For various API errors
   */
  async edit(taskId: string, request: TaskEditRequest): Promise<TaskResponse> {
    return this.post<TaskResponse>(`/tasks/${taskId}/edit`, request);
  }

  /**
   * Get all tasks.
   * 
   * Retrieves all tasks for the authenticated user.
   * 
   * @returns List of tasks
   * @throws DisperslError - For various API errors
   */
  async list(): Promise<TaskResponse> {
    return super.get<TaskResponse>('/tasks');
  }

  /**
   * Get a task by ID.
   * 
   * Retrieves a specific task by its ID.
   * 
   * @param taskId - Task ID to retrieve
   * @returns Task information
   * @throws DisperslError - For various API errors
   */
  async getById(taskId: string): Promise<TaskResponse> {
    return super.get<TaskResponse>(`/tasks/${taskId}`);
  }

  /**
   * Cancel a task by ID.
   * 
   * Deletes a specific task by its ID.
   * 
   * @param taskId - Task ID to delete
   * @returns Deletion confirmation
   * @throws DisperslError - For various API errors
   */
  async cancel(taskId: string): Promise<TaskResponse> {
    return super.delete<TaskResponse>(`/tasks/${taskId}/delete`);
  }
}
