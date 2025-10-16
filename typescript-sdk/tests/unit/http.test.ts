/**
 * Comprehensive unit tests for HTTP client
 */

import { HTTPClient } from '../../src/http';
import { DisperslError, AuthenticationError, RateLimitError } from '../../src/exceptions';
import MockAdapter from 'axios-mock-adapter';
import axios from 'axios';

describe('HTTPClient', () => {
  let client: HTTPClient;
  let mockAdapter: MockAdapter;
  const baseUrl = 'https://api.dispersl.ai/v1';
  const apiKey = 'test_api_key';

  beforeEach(() => {
    client = new HTTPClient(baseUrl, apiKey);
    mockAdapter = new MockAdapter(axios);
  });

  afterEach(() => {
    mockAdapter.restore();
  });

  describe('Initialization', () => {
    test('should initialize with base URL and API key', () => {
      expect(client).toBeDefined();
      expect(client.baseUrl).toBe(baseUrl);
    });

    test('should set default headers', () => {
      const headers = client.getHeaders();
      expect(headers['Authorization']).toBe(`Bearer ${apiKey}`);
      expect(headers['Content-Type']).toBe('application/json');
    });

    test('should include user agent', () => {
      const headers = client.getHeaders();
      expect(headers['User-Agent']).toContain('dispersl-typescript');
    });

    test('should throw error without API key', () => {
      expect(() => new HTTPClient(baseUrl, '')).toThrow(AuthenticationError);
    });
  });

  describe('Request Building', () => {
    test('should build correct URL', () => {
      const url = client.buildUrl('/agents/chat');
      expect(url).toBe(`${baseUrl}/agents/chat`);
    });

    test('should handle leading slash in path', () => {
      const url1 = client.buildUrl('/agents');
      const url2 = client.buildUrl('agents');
      expect(url1).toBe(url2);
    });

    test('should build URL with query parameters', () => {
      const url = client.buildUrl('/tasks', { status: 'pending', limit: 10 });
      expect(url).toContain('status=pending');
      expect(url).toContain('limit=10');
    });

    test('should handle custom headers', () => {
      const customHeaders = { 'X-Custom-Header': 'value' };
      const headers = client.getHeaders(customHeaders);
      expect(headers['X-Custom-Header']).toBe('value');
      expect(headers['Authorization']).toBe(`Bearer ${apiKey}`);
    });
  });

  describe('Error Handling', () => {
    test('should handle 401 authentication error', async () => {
      mockAdapter.onGet('/test').reply(401, { error: 'Invalid API key' });

      await expect(client.get('/test')).rejects.toThrow(AuthenticationError);
    });

    test('should handle 403 forbidden error', async () => {
      mockAdapter.onGet('/test').reply(403, { error: 'Access denied' });

      await expect(client.get('/test')).rejects.toThrow(DisperslError);
    });

    test('should handle 404 not found error', async () => {
      mockAdapter.onGet('/test').reply(404, { error: 'Resource not found' });

      await expect(client.get('/test')).rejects.toThrow(DisperslError);
    });

    test('should handle 429 rate limit error', async () => {
      mockAdapter.onGet('/test').reply(429, { error: 'Rate limit exceeded' }, {
        'Retry-After': '60'
      });

      await expect(client.get('/test')).rejects.toThrow(RateLimitError);
    });

    test('should handle 500 server error', async () => {
      mockAdapter.onGet('/test').reply(500, { error: 'Server error' });

      await expect(client.get('/test')).rejects.toThrow(DisperslError);
    });

    test('should handle 503 service unavailable', async () => {
      mockAdapter.onGet('/test').reply(503, { error: 'Service unavailable' });

      await expect(client.get('/test')).rejects.toThrow(DisperslError);
    });

    test('should handle network error', async () => {
      mockAdapter.onGet('/test').networkError();

      await expect(client.get('/test')).rejects.toThrow(DisperslError);
    });

    test('should handle timeout error', async () => {
      mockAdapter.onGet('/test').timeout();

      await expect(client.get('/test')).rejects.toThrow(DisperslError);
    });
  });

  describe('GET Requests', () => {
    test('should make successful GET request', async () => {
      const mockData = { result: 'success' };
      mockAdapter.onGet('/test').reply(200, mockData);

      const result = await client.get('/test');
      expect(result.data).toEqual(mockData);
    });

    test('should make GET request with query params', async () => {
      const mockData = { items: [] };
      mockAdapter.onGet('/items').reply(200, mockData);

      const params = { page: 1, limit: 10 };
      const result = await client.get('/items', { params });

      expect(result.data).toEqual(mockData);
      expect(mockAdapter.history.get[0].params).toEqual(params);
    });

    test('should handle empty response', async () => {
      mockAdapter.onGet('/test').reply(204);

      const result = await client.get('/test');
      expect(result.status).toBe(204);
    });
  });

  describe('POST Requests', () => {
    test('should make successful POST request', async () => {
      const mockData = { id: '123', created: true };
      mockAdapter.onPost('/test').reply(201, mockData);

      const payload = { name: 'Test' };
      const result = await client.post('/test', payload);

      expect(result.data).toEqual(mockData);
      expect(mockAdapter.history.post[0].data).toEqual(JSON.stringify(payload));
    });

    test('should make POST request with custom headers', async () => {
      const mockData = { result: 'success' };
      mockAdapter.onPost('/test').reply(200, mockData);

      const customHeaders = { 'X-Request-ID': 'req123' };
      const result = await client.post('/test', {}, { headers: customHeaders });

      expect(result.data).toEqual(mockData);
      expect(mockAdapter.history.post[0].headers['X-Request-ID']).toBe('req123');
    });

    test('should handle POST with FormData', async () => {
      const mockData = { uploaded: true };
      mockAdapter.onPost('/upload').reply(200, mockData);

      const formData = new FormData();
      formData.append('file', 'test');

      const result = await client.post('/upload', formData);
      expect(result.data).toEqual(mockData);
    });
  });

  describe('PATCH Requests', () => {
    test('should make successful PATCH request', async () => {
      const mockData = { id: '123', updated: true };
      mockAdapter.onPatch('/test/123').reply(200, mockData);

      const updates = { status: 'completed' };
      const result = await client.patch('/test/123', updates);

      expect(result.data).toEqual(mockData);
      expect(mockAdapter.history.patch[0].data).toEqual(JSON.stringify(updates));
    });
  });

  describe('DELETE Requests', () => {
    test('should make successful DELETE request', async () => {
      const mockData = { deleted: true };
      mockAdapter.onDelete('/test/123').reply(200, mockData);

      const result = await client.delete('/test/123');
      expect(result.data).toEqual(mockData);
    });

    test('should handle DELETE with no content', async () => {
      mockAdapter.onDelete('/test/123').reply(204);

      const result = await client.delete('/test/123');
      expect(result.status).toBe(204);
    });
  });

  describe('Streaming Requests', () => {
    test('should handle streaming response', async () => {
      // Mock a successful streaming response
      mockAdapter.onPost('/test').reply(200, { type: 'content', delta: 'Hello World' });

      const stream = client.postStream('/test', {});
      const results: any[] = [];

      for await (const chunk of stream) {
        results.push(chunk);
      }

      expect(results.length).toBeGreaterThan(0);
    });

    test('should handle streaming error', async () => {
      mockAdapter.onPost('/test').reply(500, { error: 'Stream error' });

      await expect(async () => {
        const stream = client.postStream('/test', {});
        for await (const chunk of stream) {
          // Should not reach here
        }
      }).rejects.toThrow(DisperslError);
    });
  });

  describe('Retry Logic', () => {
    test('should retry on retryable error', async () => {
      mockAdapter.onGet('/test')
        .replyOnce(503, { error: 'Service unavailable' })
        .replyOnce(200, { result: 'success' });

      const result = await client.get('/test', { maxRetries: 2 });
      expect(result.data).toEqual({ result: 'success' });
      expect(mockAdapter.history.get).toHaveLength(2);
    });

    test('should not retry on non-retryable error', async () => {
      mockAdapter.onGet('/test').reply(400, { error: 'Bad request' });

      await expect(client.get('/test', { maxRetries: 2 })).rejects.toThrow();
      expect(mockAdapter.history.get).toHaveLength(1);
    });

    test('should respect maximum retry count', async () => {
      mockAdapter.onGet('/test').reply(503, { error: 'Service unavailable' });

      await expect(client.get('/test', { maxRetries: 3 })).rejects.toThrow();
      expect(mockAdapter.history.get).toHaveLength(4); // Initial + 3 retries
    });
  });

  describe('Timeout Handling', () => {
    test('should timeout request', async () => {
      mockAdapter.onGet('/test').timeout();

      await expect(client.get('/test', { timeout: 100 })).rejects.toThrow();
    });

    test('should use default timeout', async () => {
      const clientWithTimeout = new HTTPClient(baseUrl, apiKey, { timeout: 5000 });
      expect(clientWithTimeout).toBeDefined();
    });
  });

  describe('Request Cancellation', () => {
    test('should cancel request with AbortSignal', async () => {
      const controller = new AbortController();
      mockAdapter.onGet('/test').reply(() => {
        return new Promise((_, reject) => {
          controller.signal.addEventListener('abort', () => {
            reject(new DOMException('Aborted', 'AbortError'));
          });
        });
      });

      const requestPromise = client.get('/test', { signal: controller.signal });

      controller.abort();

      await expect(requestPromise).rejects.toThrow();
    });
  });
});

