/**
 * Comprehensive unit tests for Dispersl client
 */

import { Dispersl } from '../../src/client';
import { AuthenticationError, DisperslError } from '../../src/exceptions';

describe('Dispersl Client', () => {
  const apiKey = 'test_api_key';
  const baseUrl = 'https://api.dispersl.ai/v1';

  describe('Initialization', () => {
    test('should initialize with API key', () => {
      const client = new Dispersl({ apiKey });
      expect(client).toBeDefined();
      expect(client.apiKey).toBe(apiKey);
    });

    test('should initialize with custom base URL', () => {
      const customUrl = 'https://custom.dispersl.ai/v1';
      const client = new Dispersl({ apiKey, baseUrl: customUrl });
      expect(client.baseUrl).toBe(customUrl);
    });

    test('should initialize with timeout', () => {
      const client = new Dispersl({ apiKey, timeout: 60000 });
      expect(client.timeout).toBe(60000);
    });

    test('should initialize with max retries', () => {
      const client = new Dispersl({ apiKey, maxRetries: 5 });
      expect(client.maxRetries).toBe(5);
    });

    test('should throw error without API key', () => {
      expect(() => new Dispersl({ apiKey: '' })).toThrow(AuthenticationError);
    });

    test('should initialize from environment variable', () => {
      process.env.DISPERSL_API_KEY = 'env_key';
      const client = new Dispersl();
      expect(client.apiKey).toBe('env_key');
      delete process.env.DISPERSL_API_KEY;
    });

    test('should throw error when no API key available', () => {
      delete process.env.DISPERSL_API_KEY;
      expect(() => new Dispersl()).toThrow(AuthenticationError);
    });
  });

  describe('Resource Initialization', () => {
    let client: Dispersl;

    beforeEach(() => {
      client = new Dispersl({ apiKey });
    });

    test('should initialize agents resource', () => {
      expect(client.agents).toBeDefined();
      expect(typeof client.agents.chat).toBe('function');
    });

    test('should initialize models resource', () => {
      expect(client.models).toBeDefined();
      expect(typeof client.models.list).toBe('function');
    });

    test('should initialize tasks resource', () => {
      expect(client.tasks).toBeDefined();
      expect(typeof client.tasks.create).toBe('function');
    });

    test('should initialize steps resource', () => {
      expect(client.steps).toBeDefined();
      expect(typeof client.steps.create).toBe('function');
    });

    test('should initialize history resource', () => {
      expect(client.history).toBeDefined();
      expect(typeof client.history.list).toBe('function');
    });

    test('should initialize auth resource', () => {
      expect(client.auth).toBeDefined();
    });
  });

  describe('Configuration', () => {
    test('should configure retry strategy', () => {
      const client = new Dispersl({
        apiKey,
        maxRetries: 3,
        retryBackoffFactor: 2.0
      });

      expect(client.maxRetries).toBe(3);
      expect(client.retryBackoffFactor).toBe(2.0);
    });

    test('should configure timeouts', () => {
      const client = new Dispersl({
        apiKey,
        timeout: 30000,
        connectTimeout: 10000
      });

      expect(client.timeout).toBe(30000);
      expect(client.connectTimeout).toBe(10000);
    });

    test('should handle invalid timeout', () => {
      expect(() => new Dispersl({ apiKey, timeout: -1 })).toThrow(Error);
    });

    test('should handle invalid max retries', () => {
      expect(() => new Dispersl({ apiKey, maxRetries: -1 })).toThrow(Error);
    });

    test('should normalize base URL', () => {
      const client = new Dispersl({
        apiKey,
        baseUrl: 'https://api.dispersl.ai/v1/'
      });

      expect(client.baseUrl).not.toEndWith('/');
    });

    test('should enable debug mode', () => {
      const client = new Dispersl({ apiKey, debug: true });
      expect(client.debug).toBe(true);
    });

    test('should set custom headers', () => {
      const customHeaders = { 'X-Custom-Header': 'value' };
      const client = new Dispersl({ apiKey, headers: customHeaders });
      expect(client).toBeDefined();
    });
  });

  describe('Methods', () => {
    let client: Dispersl;

    beforeEach(() => {
      client = new Dispersl({ apiKey });
    });

    test('should build request URL', () => {
      const url = client.buildUrl('/agents/chat');
      expect(url).toContain('/agents/chat');
    });

    test('should build URL with query params', () => {
      const url = client.buildUrl('/tasks', { status: 'pending', limit: 10 });
      expect(url).toContain('status=pending');
      expect(url).toContain('limit=10');
    });

    test('should get SDK version', () => {
      const version = client.getVersion();
      expect(version).toBeDefined();
      expect(typeof version).toBe('string');
      expect(version).toMatch(/\d+\.\d+\.\d+/);
    });

    test('should verify connection', async () => {
      const mockFetch = jest.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ status: 'healthy' })
      });
      global.fetch = mockFetch;

      const result = await client.verifyConnection();
      expect(result).toBe(true);
    });

    test('should handle connection verification failure', async () => {
      const mockFetch = jest.fn().mockRejectedValue(new Error('Connection failed'));
      global.fetch = mockFetch;

      const result = await client.verifyConnection();
      expect(result).toBe(false);
    });

    test('should perform health check', async () => {
      const mockFetch = jest.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ status: 'healthy' })
      });
      global.fetch = mockFetch;

      const health = await client.healthCheck();
      expect(health).toEqual({ status: 'healthy' });
    });
  });

  describe('Error Handling', () => {
    let client: Dispersl;

    beforeEach(() => {
      client = new Dispersl({ apiKey });
    });

    test('should handle API error', async () => {
      const mockFetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Server Error',
        json: async () => ({ error: 'Internal server error' })
      });
      global.fetch = mockFetch;

      await expect(client.agents.chat({
        prompt: 'test',
        default_dir: '/tmp',
        current_dir: '/tmp'
      })).rejects.toThrow(DisperslError);
    });

    test('should handle authentication error', async () => {
      const mockFetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: async () => ({ error: 'Invalid API key' })
      });
      global.fetch = mockFetch;

      await expect(client.agents.chat({
        prompt: 'test',
        default_dir: '/tmp',
        current_dir: '/tmp'
      })).rejects.toThrow(AuthenticationError);
    });

    test('should handle network error', async () => {
      const mockFetch = jest.fn().mockRejectedValue(new Error('Network error'));
      global.fetch = mockFetch;

      await expect(client.agents.chat({
        prompt: 'test',
        default_dir: '/tmp',
        current_dir: '/tmp'
      })).rejects.toThrow(DisperslError);
    });

    test('should handle timeout', async () => {
      const mockFetch = jest.fn().mockImplementation(
        () => new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 100))
      );
      global.fetch = mockFetch;

      await expect(client.agents.chat({
        prompt: 'test',
        default_dir: '/tmp',
        current_dir: '/tmp'
      })).rejects.toThrow(DisperslError);
    });
  });

  describe('Thread Safety', () => {
    test('should handle concurrent requests', async () => {
      const client = new Dispersl({ apiKey });

      const mockFetch = jest.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ result: 'success' })
      });
      global.fetch = mockFetch;

      const requests = Array.from({ length: 10 }, () =>
        client.agents.chat({
          prompt: 'test',
          default_dir: '/tmp',
          current_dir: '/tmp'
        })
      );

      const results = await Promise.all(requests);
      expect(results.length).toBe(10);
      expect(mockFetch).toHaveBeenCalledTimes(10);
    });

    test('should isolate multiple clients', () => {
      const client1 = new Dispersl({ apiKey: 'key1' });
      const client2 = new Dispersl({ apiKey: 'key2' });

      expect(client1.apiKey).not.toBe(client2.apiKey);
    });
  });

  describe('Cleanup', () => {
    test('should close client', () => {
      const client = new Dispersl({ apiKey });
      client.close();
      // Should not throw
      expect(client).toBeDefined();
    });

    test('should support using as resource', () => {
      const client = new Dispersl({ apiKey });
      // TypeScript doesn't have with statement, but test the concept
      client.close();
      expect(client).toBeDefined();
    });
  });

  describe('Configuration Validation', () => {
    test('should reject invalid base URL without scheme', () => {
      expect(() => new Dispersl({
        apiKey,
        baseUrl: 'api.dispersl.ai'
      })).toThrow(Error);
    });

    test('should accept valid HTTPS URL', () => {
      const client = new Dispersl({
        apiKey,
        baseUrl: 'https://api.dispersl.ai'
      });
      expect(client.baseUrl).toBe('https://api.dispersl.ai');
    });

    test('should validate API key format', () => {
      // Valid formats should work
      expect(() => new Dispersl({ apiKey: 'sk_test_1234567890' })).not.toThrow();
      expect(() => new Dispersl({ apiKey: 'any_key_format' })).not.toThrow();
    });
  });

  describe('Resource Sharing', () => {
    test('should share HTTP client across resources', () => {
      const client = new Dispersl({ apiKey });

      // All resources should use the same HTTP client instance
      const agentsClient = client.agents['_httpClient'];
      const tasksClient = client.tasks['_httpClient'];

      expect(agentsClient).toBe(tasksClient);
    });
  });

  describe('Custom Configuration', () => {
    test('should support proxy configuration', () => {
      const client = new Dispersl({
        apiKey,
        proxy: 'http://proxy.example.com:8080'
      });

      expect(client.proxy).toBe('http://proxy.example.com:8080');
    });

    test('should support custom user agent', () => {
      const customUserAgent = 'MyApp/1.0';
      const client = new Dispersl({
        apiKey,
        userAgent: customUserAgent
      });

      expect(client.userAgent).toContain(customUserAgent);
    });
  });
});

