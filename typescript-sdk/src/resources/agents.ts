/**
 * Agents resource for AI operations.
 * 
 * This module provides the AgentsResource class for interacting with
 * the Dispersl API's agent endpoints, including chat, planning,
 * code generation, testing, and documentation.
 */

import { Resource } from './base';
import { HTTPClient } from '../http';
import {
  BuildRequest,
  ChatRequest,
  DisperseRequest,
  RepoDocsRequest,
  StandardNdjsonResponse,
  PaginatedAgentResponse,
  PaginationParams,
} from '../models';
import { StandardNdjsonResponseSchema } from '../models/base';

/**
 * Resource for AI agent operations.
 * 
 * Provides methods for interacting with various AI agents including
 * chat, planning, code generation, testing, and documentation.
 */
export class AgentsResource extends Resource {
  constructor(httpClient: HTTPClient) {
    super(httpClient);
  }

  /**
   * Get all agents.
   * 
   * Retrieves all available agents.
   * 
   * @param params - Pagination parameters
   * @returns List of agents with pagination info
   * @throws DisperslError - For various API errors
   */
  async list(params?: PaginationParams): Promise<PaginatedAgentResponse> {
    return super.get<PaginatedAgentResponse>('/agents', params);
  }

  /**
   * Chat with AI to understand internal codebase insights, task progress and documentation.
   * 
   * @param request - Chat request parameters
   * @returns Async generator yielding streaming response chunks
   * @throws DisperslError - For various API errors
   */
  async *chat(request: ChatRequest): AsyncGenerator<StandardNdjsonResponse, void, unknown> {
    const response = await this.http.post(
      '/agent/chat',
      request,
      undefined,
      { 'Accept': 'application/x-ndjson' }
    );

    // Parse NDJSON stream
    const lines = (response.data as string).split('\n');
    for (const line of lines) {
      if (line.trim()) {
        try {
          const chunkData: unknown = JSON.parse(line);
          const validated = StandardNdjsonResponseSchema.parse(chunkData);
          yield validated;
        } catch (error) {
          // Skip invalid JSON lines
          continue;
        }
      }
    }
  }

  /**
   * Multi-agent task dispersion.
   * 
   * Distributes a complex task across multiple specialized AI agents
   * following SDLC principles.
   * 
   * @param request - Disperse request parameters
   * @returns Async generator yielding streaming response chunks
   * @throws DisperslError - For various API errors
   */
  async *plan(request: DisperseRequest): AsyncGenerator<StandardNdjsonResponse, void, unknown> {
    const response = await this.http.post(
      '/agent/plan',
      request,
      undefined,
      { 'Accept': 'application/x-ndjson' }
    );

    // Parse NDJSON stream
    const lines = (response.data as string).split('\n');
    for (const line of lines) {
      if (line.trim()) {
        try {
          const chunkData: unknown = JSON.parse(line);
          const validated = StandardNdjsonResponseSchema.parse(chunkData);
          yield validated;
        } catch (error) {
          // Skip invalid JSON lines
          continue;
        }
      }
    }
  }

  /**
   * Code generation with agentic flow and tool execution.
   * 
   * Generates and builds code based on the provided prompt.
   * 
   * @param request - Build request parameters
   * @returns Async generator yielding streaming response chunks
   * @throws DisperslError - For various API errors
   */
  async *code(request: BuildRequest): AsyncGenerator<StandardNdjsonResponse, void, unknown> {
    const response = await this.http.post(
      '/agent/code',
      request,
      undefined,
      { 'Accept': 'application/x-ndjson' }
    );

    // Parse NDJSON stream
    const lines = (response.data as string).split('\n');
    for (const line of lines) {
      if (line.trim()) {
        try {
          const chunkData: unknown = JSON.parse(line);
          const validated = StandardNdjsonResponseSchema.parse(chunkData);
          yield validated;
        } catch (error) {
          // Skip invalid JSON lines
          continue;
        }
      }
    }
  }

  /**
   * Test generation with agentic flow and tool execution.
   * 
   * Generates and builds tests based on the provided prompt.
   * 
   * @param request - Build request parameters
   * @returns Async generator yielding streaming response chunks
   * @throws DisperslError - For various API errors
   */
  async *test(request: BuildRequest): AsyncGenerator<StandardNdjsonResponse, void, unknown> {
    const response = await this.http.post(
      '/agent/test',
      request,
      undefined,
      { 'Accept': 'application/x-ndjson' }
    );

    // Parse NDJSON stream
    const lines = (response.data as string).split('\n');
    for (const line of lines) {
      if (line.trim()) {
        try {
          const chunkData: unknown = JSON.parse(line);
          const validated = StandardNdjsonResponseSchema.parse(chunkData);
          yield validated;
        } catch (error) {
          // Skip invalid JSON lines
          continue;
        }
      }
    }
  }

  /**
   * Git versioning with agentic flow and tool execution.
   * 
   * Handles Git versioning operations.
   * 
   * @param request - Build request parameters
   * @returns Async generator yielding streaming response chunks
   * @throws DisperslError - For various API errors
   */
  async *git(request: BuildRequest): AsyncGenerator<StandardNdjsonResponse, void, unknown> {
    const response = await this.http.post(
      '/agent/git',
      request,
      undefined,
      { 'Accept': 'application/x-ndjson' }
    );

    // Parse NDJSON stream
    const lines = (response.data as string).split('\n');
    for (const line of lines) {
      if (line.trim()) {
        try {
          const chunkData: unknown = JSON.parse(line);
          const validated = StandardNdjsonResponseSchema.parse(chunkData);
          yield validated;
        } catch (error) {
          // Skip invalid JSON lines
          continue;
        }
      }
    }
  }

  /**
   * Generate end to end documentation for a repository.
   * 
   * Generates documentation for a repository with agentic flow
   * and tool execution.
   * 
   * @param request - Repository documentation request parameters
   * @returns Async generator yielding streaming response chunks
   * @throws DisperslError - For various API errors
   */
  async *documentRepo(request: RepoDocsRequest): AsyncGenerator<StandardNdjsonResponse, void, unknown> {
    const response = await this.http.post(
      '/agent/document/repo',
      request,
      undefined,
      { 'Accept': 'application/x-ndjson' }
    );

    // Parse NDJSON stream
    const lines = (response.data as string).split('\n');
    for (const line of lines) {
      if (line.trim()) {
        try {
          const chunkData: unknown = JSON.parse(line);
          const validated = StandardNdjsonResponseSchema.parse(chunkData);
          yield validated;
        } catch (error) {
          // Skip invalid JSON lines
          continue;
        }
      }
    }
  }
}
