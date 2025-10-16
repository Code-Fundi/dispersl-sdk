/**
 * Unit tests for pagination functionality.
 */

import { Client } from '../../src/client';
import { MockHTTPClient } from '../fixtures/mockServer';
import { PaginationParams } from '../../src/models';

describe('Pagination Tests', () => {
  let client: Client;
  let mockHttpClient: MockHTTPClient;

  beforeEach(() => {
    mockHttpClient = new MockHTTPClient('http://localhost:3000', 'test-key');
    client = new Client({ apiKey: 'test-key' });
    // Replace the internal HTTP client with our mock
    (client as any).http = mockHttpClient;
  });

  afterEach(() => {
    mockHttpClient.reset();
  });

  describe('Tasks Pagination', () => {
    test('should list tasks with pagination parameters', async () => {
      const params: PaginationParams = {
        page: 1,
        pageSize: 10
      };

      const response = await client.tasks.list(params);

      expect(response).toBeDefined();
      expect(response.status).toBe('success');
      expect(response.data).toBeDefined();
      expect(response.pagination).toBeDefined();
      expect(response.pagination.page).toBe(1);
      expect(response.pagination.pageSize).toBe(20);
      expect(response.pagination.total).toBe(50);
      expect(response.pagination.hasNext).toBe(true);
      expect(response.pagination.hasPrev).toBe(false);

      // Verify the request was made with correct parameters
      const lastRequest = mockHttpClient.getLastRequest();
      expect(lastRequest.method).toBe('GET');
      expect(lastRequest.url).toBe('/tasks');
      expect(lastRequest.data).toEqual({ page: 1, pageSize: 10 });
    });

    test('should list tasks without pagination parameters (default)', async () => {
      const response = await client.tasks.list();

      expect(response).toBeDefined();
      expect(response.status).toBe('success');
      expect(response.pagination).toBeDefined();

      // Verify the request was made without parameters
      const lastRequest = mockHttpClient.getLastRequest();
      expect(lastRequest.method).toBe('GET');
      expect(lastRequest.url).toBe('/tasks');
      expect(lastRequest.data).toBeUndefined();
    });
  });

  describe('Agents Pagination', () => {
    test('should list agents with pagination parameters', async () => {
      const params: PaginationParams = {
        page: 1,
        pageSize: 5
      };

      const response = await client.agents.list(params);

      expect(response).toBeDefined();
      expect(response.status).toBe('success');
      expect(response.data).toBeDefined();
      expect(response.pagination).toBeDefined();
      expect(response.pagination.page).toBe(1);
      expect(response.pagination.pageSize).toBe(20);
      expect(response.pagination.total).toBe(5);
      expect(response.pagination.hasNext).toBe(false);
      expect(response.pagination.hasPrev).toBe(false);

      // Verify the request was made with correct parameters
      const lastRequest = mockHttpClient.getLastRequest();
      expect(lastRequest.method).toBe('GET');
      expect(lastRequest.url).toBe('/agents');
      expect(lastRequest.data).toEqual({ page: 1, pageSize: 5 });
    });

    test('should list agents without pagination parameters', async () => {
      const response = await client.agents.list();

      expect(response).toBeDefined();
      expect(response.status).toBe('success');
      expect(response.pagination).toBeDefined();

      // Verify the request was made without parameters
      const lastRequest = mockHttpClient.getLastRequest();
      expect(lastRequest.method).toBe('GET');
      expect(lastRequest.url).toBe('/agents');
      expect(lastRequest.data).toBeUndefined();
    });
  });

  describe('Steps Pagination', () => {
    test('should get steps by task ID with pagination parameters', async () => {
      const params: PaginationParams = {
        page: 2,
        pageSize: 15
      };

      const response = await client.steps.getByTaskId('task_123', params);

      expect(response).toBeDefined();
      expect(response.status).toBe('success');
      expect(response.data).toBeDefined();
      expect(response.pagination).toBeDefined();
      expect(response.pagination.page).toBe(1);
      expect(response.pagination.pageSize).toBe(20);
      expect(response.pagination.total).toBe(25);
      expect(response.pagination.hasNext).toBe(true);
      expect(response.pagination.hasPrev).toBe(false);

      // Verify the request was made with correct parameters
      const lastRequest = mockHttpClient.getLastRequest();
      expect(lastRequest.method).toBe('GET');
      expect(lastRequest.url).toBe('/steps/task/task_123');
      expect(lastRequest.data).toEqual({ page: 2, pageSize: 15 });
    });

    test('should get steps by task ID without pagination parameters', async () => {
      const response = await client.steps.getByTaskId('task_123');

      expect(response).toBeDefined();
      expect(response.status).toBe('success');
      expect(response.pagination).toBeDefined();

      // Verify the request was made without parameters
      const lastRequest = mockHttpClient.getLastRequest();
      expect(lastRequest.method).toBe('GET');
      expect(lastRequest.url).toBe('/steps/task/task_123');
      expect(lastRequest.data).toBeUndefined();
    });
  });

  describe('History Pagination', () => {
    test('should get task history with pagination parameters', async () => {
      const response = await client.history.getTaskHistory('task_123', {
        page: 1,
        pageSize: 10
      });

      expect(response).toBeDefined();
      expect(response.status).toBe('success');
      expect(response.data).toBeDefined();
      expect(response.pagination).toBeDefined();
      expect(response.pagination.page).toBe(1);
      expect(response.pagination.pageSize).toBe(20);
      expect(response.pagination.total).toBe(15);
      expect(response.pagination.hasNext).toBe(false);
      expect(response.pagination.hasPrev).toBe(false);

      // Verify the request was made with correct parameters
      const lastRequest = mockHttpClient.getLastRequest();
      expect(lastRequest.method).toBe('GET');
      expect(lastRequest.url).toBe('/history/task/task_123');
      expect(lastRequest.data).toEqual({ page: 1, pageSize: 10 });
    });

    test('should get step history with pagination parameters', async () => {
      const response = await client.history.getStepHistory('step_123', {
        page: 1,
        pageSize: 5
      });

      expect(response).toBeDefined();
      expect(response.status).toBe('success');
      expect(response.data).toBeDefined();
      expect(response.pagination).toBeDefined();

      // Verify the request was made with correct parameters
      const lastRequest = mockHttpClient.getLastRequest();
      expect(lastRequest.method).toBe('GET');
      expect(lastRequest.url).toBe('/history/step/step_123');
      expect(lastRequest.data).toEqual({ page: 1, pageSize: 5 });
    });
  });

  describe('Pagination Parameter Validation', () => {
    test('should handle invalid page numbers gracefully', async () => {
      const params: PaginationParams = {
        page: 0, // Invalid page number
        pageSize: 10
      };

      // This should not throw an error, but the API should handle it
      const response = await client.tasks.list(params);
      expect(response).toBeDefined();
    });

    test('should handle invalid page size gracefully', async () => {
      const params: PaginationParams = {
        page: 1,
        pageSize: 150 // Exceeds max page size
      };

      // This should not throw an error, but the API should handle it
      const response = await client.tasks.list(params);
      expect(response).toBeDefined();
    });
  });

  describe('Pagination Response Structure', () => {
    test('should have correct pagination object structure', async () => {
      const response = await client.tasks.list({ page: 1, pageSize: 10 });

      expect(response.pagination).toHaveProperty('page');
      expect(response.pagination).toHaveProperty('pageSize');
      expect(response.pagination).toHaveProperty('total');
      expect(response.pagination).toHaveProperty('totalPages');
      expect(response.pagination).toHaveProperty('hasNext');
      expect(response.pagination).toHaveProperty('hasPrev');

      expect(typeof response.pagination.page).toBe('number');
      expect(typeof response.pagination.pageSize).toBe('number');
      expect(typeof response.pagination.total).toBe('number');
      expect(typeof response.pagination.totalPages).toBe('number');
      expect(typeof response.pagination.hasNext).toBe('boolean');
      expect(typeof response.pagination.hasPrev).toBe('boolean');
    });

    test('should have correct data array structure', async () => {
      const response = await client.tasks.list({ page: 1, pageSize: 10 });

      expect(Array.isArray(response.data)).toBe(true);
      expect(response.data.length).toBeGreaterThan(0);

      // Check structure of first item
      const firstItem = response.data[0];
      expect(firstItem).toHaveProperty('id');
      expect(firstItem).toHaveProperty('name');
      expect(firstItem).toHaveProperty('status');
      expect(firstItem).toHaveProperty('created_at');
      expect(firstItem).toHaveProperty('updated_at');
    });
  });
});
