/**
 * Integration tests for Dispersl SDK.
 * 
 * These tests require a running API server.
 */

import { Client } from '../../src/client';

describe('Integration Tests', () => {
  test('client initialization', () => {
    const client = new Client({ apiKey: 'test_key' });
    expect(client).toBeDefined();
  });

  test.skip('list models', async () => {
  });
});
