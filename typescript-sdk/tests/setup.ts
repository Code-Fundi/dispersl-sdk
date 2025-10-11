/**
 * Test setup and configuration
 * Supports dynamic API URLs via environment variables
 */

// Set default API URL for testing
process.env.DISPERSL_API_URL = process.env.DISPERSL_API_URL || 'http://localhost:3000';
process.env.DISPERSL_API_KEY = process.env.DISPERSL_API_KEY || 'test_api_key';

// Log the API URL being used for tests
console.log(`Running tests against: ${process.env.DISPERSL_API_URL}`);

// Mock configurations
global.console = {
  ...console,
  // Suppress console.log during tests unless DEBUG is set
  log: process.env.DEBUG ? console.log : jest.fn(),
  debug: process.env.DEBUG ? console.debug : jest.fn(),
  info: process.env.DEBUG ? console.info : jest.fn(),
  warn: console.warn,
  error: console.error,
};

// Export test utilities
export const getTestApiUrl = (): string => {
  return process.env.DISPERSL_API_URL || 'http://localhost:3000';
};

export const getTestApiKey = (): string => {
  return process.env.DISPERSL_API_KEY || 'test_api_key';
};

export const isIntegrationTest = (): boolean => {
  return process.env.RUN_INTEGRATION_TESTS === 'true';
};
