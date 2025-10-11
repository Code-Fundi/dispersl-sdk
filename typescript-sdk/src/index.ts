/**
 * Dispersl TypeScript SDK
 * 
 * Official TypeScript SDK for the Dispersl API - an agentic workflow platform 
 * for AI-driven software development.
 */

export { Client } from './client';
export { AsyncClient } from './client';

export { AgenticExecutor } from './agentic';

export {
  DisperslError,
  AuthenticationError,
  NotFoundError,
  ValidationError,
  RateLimitError,
  ServerError,
  TimeoutError,
  NetworkError,
  SerializationError,
  CircuitBreakerOpenError,
} from './exceptions';

export type {
  AuthHandler,
} from './auth';

export {
  APIKeyAuth,
  BearerTokenAuth,
  OAuth2Auth,
  BasicAuth,
  createAuthHandler,
  getAuthFromEnv,
} from './auth';

export type { HTTPClientOptions, RequestOptions } from './http';

export {
  HTTPClient,
} from './http';

export {
  retryWithBackoff,
  CircuitBreaker,
  RetryPresets,
} from './retry';

export type {
  RetryOptions,
  CircuitBreakerOptions,
} from './retry';

export {
  serializeRequestData,
  deserializeResponseData,
  serializeDateTime,
  deserializeDateTime,
  cleanNullValues,
  validateRequiredFields,
  convertCamelToSnake,
  convertSnakeToCamel,
  CommonSchemas,
} from './serializers';

export {
  isValidUrl,
  buildUrl,
  sanitizeFilename,
  deepMergeObjects,
  flattenObject,
  unflattenObject,
  chunkArray,
  removeNullValues,
  formatBytes,
  truncateString,
  extractDomainFromUrl,
  isValidEmail,
  generateRequestId,
  retryAfterToSeconds,
  isPlainObject,
  isNonEmptyString,
  isPositiveNumber,
} from './utils';

// Re-export types from models
export type {
  AgenticSession,
  ChatRequest,
  DisperseRequest,
  BuildRequest,
  RepoDocsRequest,
  HandoverRequest,
  MCPClient,
  MCPTool,
  NewAPIKeyRequest,
  TaskEditRequest,
  HistoryRequest,
  ModelInfo,
  ModelsResponse,
  APIKeyInfo,
  APIKeysResponse,
  NewAPIKeyResponse,
  TaskInfo,
  TaskResponse,
  StepInfo,
  StepResponse,
  HistoryEntry,
  HistoryResponse,
  StatsResponse,
  ToolParameter,
  ToolDefinition,
  ToolCall,
  ToolResponse,
  StandardNdjsonResponse,
  Metadata,
} from './models';

// Version information
export const VERSION = '0.1.0';
