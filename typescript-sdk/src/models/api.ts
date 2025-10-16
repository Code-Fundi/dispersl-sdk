/**
 * Request and response models for the Dispersl API.
 * 
 * This module contains all the data models used for API requests and responses,
 * generated from the OpenAPI specification.
 */

import { z } from 'zod';
import { BaseResponseSchema, MetadataSchema, PaginationSchema } from './base';

// Request Models

export const ChatRequestSchema = z.object({
  prompt: z.string(),
  model: z.string().optional(),
  context: z.string().optional(),
  memory: z.boolean().optional(),
  voice: z.boolean().optional(),
  task_id: z.string().optional(),
  knowledge: z.string().optional(),
  os: z.string().optional(),
  default_dir: z.string().optional(),
  current_dir: z.string().optional(),
  mcp: z.record(z.unknown()).optional(),
});

export type ChatRequest = z.infer<typeof ChatRequestSchema>;

export const DisperseRequestSchema = z.object({
  prompt: z.string(),
  model: z.string().optional(),
  agent_name: z.string().optional(),
  context: z.string().optional(),
  task_id: z.string().optional(),
  knowledge: z.string().optional(),
  os: z.string().optional(),
  default_dir: z.string().optional(),
  current_dir: z.string().optional(),
  memory: z.boolean().optional(),
});

export type DisperseRequest = z.infer<typeof DisperseRequestSchema>;

export const BuildRequestSchema = z.object({
  prompt: z.string(),
  model: z.string().optional(),
  context: z.string().optional(),
  task_id: z.string().optional(),
  knowledge: z.string().optional(),
  os: z.string().optional(),
  default_dir: z.string().optional(),
  current_dir: z.string().optional(),
  mcp: z.record(z.unknown()).optional(),
});

export type BuildRequest = z.infer<typeof BuildRequestSchema>;

export const RepoDocsRequestSchema = z.object({
  url: z.string().url(),
  branch: z.string(),
  model: z.string().optional(),
  team_access: z.boolean().optional(),
  task_id: z.string().optional(),
});

export type RepoDocsRequest = z.infer<typeof RepoDocsRequestSchema>;

export const NewAPIKeyRequestSchema = z.object({
  user_id: z.string(),
  name: z.string().optional(),
});

export type NewAPIKeyRequest = z.infer<typeof NewAPIKeyRequestSchema>;

export const TaskEditRequestSchema = z.object({
  name: z.string().optional(),
  status: z.string().optional(),
});

export type TaskEditRequest = z.infer<typeof TaskEditRequestSchema>;

export const HistoryRequestSchema = z.object({
  page: z.number().int().min(1).optional(),
  pageSize: z.number().int().min(1).max(100).optional(),
});

export type HistoryRequest = z.infer<typeof HistoryRequestSchema>;

// Response Models

export const ModelInfoSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  context_length: z.number().int(),
  tier_requirements: z.record(z.unknown()),
});

export type ModelInfo = z.infer<typeof ModelInfoSchema>;

export const ModelsResponseSchema = BaseResponseSchema.extend({
  models: z.array(ModelInfoSchema),
});

export type ModelsResponse = z.infer<typeof ModelsResponseSchema>;

export const APIKeyInfoSchema = z.object({
  name: z.string(),
  public_key: z.string(),
  created_at: z.string(),
});

export type APIKeyInfo = z.infer<typeof APIKeyInfoSchema>;

export const APIKeysResponseSchema = BaseResponseSchema.extend({
  api_keys: z.array(APIKeyInfoSchema),
});

export type APIKeysResponse = z.infer<typeof APIKeysResponseSchema>;

export const AgentInfoSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  status: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type AgentInfo = z.infer<typeof AgentInfoSchema>;

export const AgentResponseSchema = BaseResponseSchema.extend({
  data: z.array(AgentInfoSchema),
});

export type AgentResponse = z.infer<typeof AgentResponseSchema>;

export const PaginatedAgentResponseSchema = BaseResponseSchema.extend({
  data: z.array(AgentInfoSchema),
  pagination: PaginationSchema,
});

export type PaginatedAgentResponse = z.infer<typeof PaginatedAgentResponseSchema>;

export const NewAPIKeyResponseSchema = BaseResponseSchema.extend({
  public_key: z.string(),
});

export type NewAPIKeyResponse = z.infer<typeof NewAPIKeyResponseSchema>;

export const TaskInfoSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type TaskInfo = z.infer<typeof TaskInfoSchema>;

export const TaskResponseSchema = BaseResponseSchema.extend({
  data: z.array(TaskInfoSchema),
});

export type TaskResponse = z.infer<typeof TaskResponseSchema>;

export const PaginatedTaskResponseSchema = BaseResponseSchema.extend({
  data: z.array(TaskInfoSchema),
  pagination: PaginationSchema,
});

export type PaginatedTaskResponse = z.infer<typeof PaginatedTaskResponseSchema>;

export const StepInfoSchema = z.object({
  id: z.string(),
  task_id: z.string(),
  name: z.string(),
  status: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type StepInfo = z.infer<typeof StepInfoSchema>;

export const StepResponseSchema = BaseResponseSchema.extend({
  data: z.array(StepInfoSchema),
});

export type StepResponse = z.infer<typeof StepResponseSchema>;

export const PaginatedStepResponseSchema = BaseResponseSchema.extend({
  data: z.array(StepInfoSchema),
  pagination: PaginationSchema,
});

export type PaginatedStepResponse = z.infer<typeof PaginatedStepResponseSchema>;

export const HistoryEntrySchema = z.object({
  id: z.string(),
  event: z.string(),
  timestamp: z.string(),
  details: z.record(z.unknown()),
});

export type HistoryEntry = z.infer<typeof HistoryEntrySchema>;

export const HistoryResponseSchema = BaseResponseSchema.extend({
  data: z.array(HistoryEntrySchema),
});

export type HistoryResponse = z.infer<typeof HistoryResponseSchema>;

export const PaginatedHistoryResponseSchema = BaseResponseSchema.extend({
  data: z.array(HistoryEntrySchema),
  pagination: PaginationSchema,
});

export type PaginatedHistoryResponse = z.infer<typeof PaginatedHistoryResponseSchema>;

export const StatsResponseSchema = BaseResponseSchema.extend({
  data: z.record(z.unknown()),
});

export type StatsResponse = z.infer<typeof StatsResponseSchema>;

// Tool Models

export const ToolParameterSchema = z.object({
  type: z.string(),
  description: z.string().optional(),
  required: z.array(z.string()).optional(),
});

export type ToolParameter = z.infer<typeof ToolParameterSchema>;

export const ToolDefinitionSchema = z.object({
  name: z.string(),
  description: z.string(),
  parameters: ToolParameterSchema,
  endpoints: z.array(z.string()),
});

export type ToolDefinition = z.infer<typeof ToolDefinitionSchema>;

export const ToolCallSchema = z.object({
  function: z.record(z.unknown()),
  arguments: z.string(),
});

export type ToolCall = z.infer<typeof ToolCallSchema>;

export const HandoverRequestSchema = z.object({
  agent_name: z.string(),
  prompt: z.string(),
  additional_args: z.record(z.unknown()).optional(),
});

export type HandoverRequest = z.infer<typeof HandoverRequestSchema>;

export const ToolResponseSchema = z.object({
  status: z.string(),
  message: z.string(),
  tool: z.string(),
  output: z.string(),
});

export type ToolResponse = z.infer<typeof ToolResponseSchema>;

export const AgenticSessionSchema = z.object({
  id: z.string(),
  context: z.record(z.unknown()).default({}),
  conversation_history: z.array(z.record(z.unknown())).default([]),
  active_tools: z.array(z.string()).default([]),
  tool_responses: z.array(ToolResponseSchema).default([]),
});

export type AgenticSession = z.infer<typeof AgenticSessionSchema>;

export const MCPToolSchema = z.object({
  name: z.string(),
  description: z.string(),
  parameters: z.record(z.unknown()),
  execute: z.function().optional(),
});

export type MCPTool = z.infer<typeof MCPToolSchema>;

export const MCPClientSchema = z.object({
  name: z.string(),
  command: z.string().optional(),
  args: z.array(z.string()).optional(),
  env: z.record(z.string()).optional(),
  url: z.string().optional(),
  headers: z.record(z.string()).optional(),
});

export type MCPClient = z.infer<typeof MCPClientSchema>;

// NDJSON Response Examples

export const NdjsonTextExampleSchema = z.object({
  status: z.literal('processing'),
  message: z.literal('Content chunk'),
  content: z.literal('Generated text...'),
});

export type NdjsonTextExample = z.infer<typeof NdjsonTextExampleSchema>;

export const NdjsonReasoningExampleSchema = z.object({
  status: z.literal('processing'),
  message: z.literal('Reasoning chunk'),
  content: z.literal('AI reasoning...'),
});

export type NdjsonReasoningExample = z.infer<typeof NdjsonReasoningExampleSchema>;

export const NdjsonToolExampleSchema = z.object({
  status: z.literal('processing'),
  message: z.literal('Tool calls'),
  tools: z.array(ToolCallSchema),
});

export type NdjsonToolExample = z.infer<typeof NdjsonToolExampleSchema>;

export const NdjsonKnowledgeExampleSchema = z.object({
  status: z.literal('processing'),
  message: z.literal('Knowledge sources'),
  knowledge: z.array(z.string()),
});

export type NdjsonKnowledgeExample = z.infer<typeof NdjsonKnowledgeExampleSchema>;

export const NdjsonAudioExampleSchema = z.object({
  status: z.literal('processing'),
  message: z.literal('Audio chunk'),
  audio: z.literal('base64_encoded_audio'),
});

export type NdjsonAudioExample = z.infer<typeof NdjsonAudioExampleSchema>;

export const NdjsonCompleteExampleSchema = z.object({
  status: z.literal('complete'),
  message: z.literal('Stream completed'),
  metadata: MetadataSchema,
});

export type NdjsonCompleteExample = z.infer<typeof NdjsonCompleteExampleSchema>;

export const NdjsonErrorExampleSchema = z.object({
  status: z.literal('error'),
  message: z.literal('Error occurred'),
  error: z.object({
    code: z.number().int(),
    message: z.string(),
  }),
});

export type NdjsonErrorExample = z.infer<typeof NdjsonErrorExampleSchema>;

// Re-export base types
export type { StandardNdjsonResponse, Metadata } from './base';
