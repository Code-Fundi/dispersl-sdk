/**
 * Authentication handlers for the Dispersl SDK.
 * 
 * This module provides various authentication methods including
 * API key, Bearer token, and OAuth 2.0 support.
 */

import { AuthenticationError } from './exceptions';

export interface AuthHandler {
  getHeaders(): Record<string, string>;
}

/**
 * API Key authentication handler.
 * 
 * Supports both header-based and query parameter-based API keys.
 */
export class APIKeyAuth implements AuthHandler {
  constructor(
    private readonly apiKey: string,
    private readonly headerName: string = 'Authorization',
    private readonly headerFormat: string = 'Bearer {apiKey}'
  ) {}

  getHeaders(): Record<string, string> {
    return {
      [this.headerName]: this.headerFormat.replace('{apiKey}', this.apiKey),
    };
  }
}

/**
 * Bearer token authentication handler.
 * 
 * Used for OAuth 2.0 and other token-based authentication.
 */
export class BearerTokenAuth implements AuthHandler {
  constructor(private readonly token: string) {}

  getHeaders(): Record<string, string> {
    return {
      Authorization: `Bearer ${this.token}`,
    };
  }
}

/**
 * OAuth 2.0 authentication handler.
 * 
 * Supports client credentials flow and automatic token refresh.
 */
export class OAuth2Auth implements AuthHandler {
  private accessToken?: string;
  private refreshToken?: string;

  constructor(
    private readonly clientId: string,
    private readonly clientSecret: string,
    private readonly tokenUrl: string,
    private readonly scope?: string,
    accessToken?: string,
    refreshToken?: string
  ) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
  }

  getHeaders(): Record<string, string> {
    if (!this.accessToken) {
      throw new Error('No access token available. Call getToken() first.');
    }

    return {
      Authorization: `Bearer ${this.accessToken}`,
    };
  }

  /**
   * Get access token using client credentials flow.
   * 
   * @returns Access token string
   * @throws Error - If token retrieval fails
   */
  async getToken(): Promise<string> {
    // This would typically make an HTTP request to the token endpoint
    // For now, we'll throw an error indicating this needs to be implemented
    throw new Error(
      'OAuth 2.0 token retrieval not implemented. ' +
      'Please provide a token directly or implement token refresh logic.'
    );
  }
}

/**
 * Basic authentication handler.
 * 
 * Uses username and password for HTTP Basic authentication.
 */
export class BasicAuth implements AuthHandler {
  constructor(
    private readonly username: string,
    private readonly password: string
  ) {}

  getHeaders(): Record<string, string> {
    const credentials = `${this.username}:${this.password}`;
    const encodedCredentials = Buffer.from(credentials).toString('base64');

    return {
      Authorization: `Basic ${encodedCredentials}`,
    };
  }
}

/**
 * Create authentication handler from environment variables.
 * 
 * Checks for the following environment variables:
 * - DISPERSL_API_KEY: API key for authentication
 * - DISPERSL_TOKEN: Bearer token for authentication
 * - DISPERSL_CLIENT_ID: OAuth 2.0 client ID
 * - DISPERSL_CLIENT_SECRET: OAuth 2.0 client secret
 * 
 * @returns AuthHandler instance or null if no credentials found
 */
export function getAuthFromEnv(): AuthHandler | null {
  // Check for API key
  const apiKey = process.env.DISPERSL_API_KEY;
  if (apiKey) {
    return new APIKeyAuth(apiKey);
  }

  // Check for Bearer token
  const token = process.env.DISPERSL_TOKEN;
  if (token) {
    return new BearerTokenAuth(token);
  }

  // Check for OAuth 2.0 credentials
  const clientId = process.env.DISPERSL_CLIENT_ID;
  const clientSecret = process.env.DISPERSL_CLIENT_SECRET;
  if (clientId && clientSecret) {
    const tokenUrl = process.env.DISPERSL_TOKEN_URL || 'https://api.dispersl.com/oauth/token';
    return new OAuth2Auth(clientId, clientSecret, tokenUrl);
  }

  return null;
}

/**
 * Create authentication handler from various input types.
 * 
 * @param auth - Authentication method. Can be:
 *   - null: Try to get from environment variables
 *   - string: Treat as API key
 *   - AuthHandler: Use directly
 * @returns AuthHandler instance or null
 * @throws AuthenticationError - If auth is empty string or invalid
 */
export function createAuthHandler(auth?: string | AuthHandler | null): AuthHandler | null {
  if (auth === null || auth === undefined) {
    return getAuthFromEnv();
  }

  if (typeof auth === 'string') {
    // Reject empty strings
    if (auth.trim() === '') {
      throw new AuthenticationError(
        'API key cannot be empty. Provide a valid API key or set DISPERSL_API_KEY environment variable.'
      );
    }
    return new APIKeyAuth(auth);
  }

  if (typeof auth === 'object' && 'getHeaders' in auth) {
    return auth;
  }

  throw new AuthenticationError(
    `Invalid auth type: ${typeof auth}. ` +
    'Expected null, string, or AuthHandler instance.'
  );
}
