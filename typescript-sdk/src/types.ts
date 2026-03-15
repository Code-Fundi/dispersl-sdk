export interface DisperslConfig {
  baseUrl: string;
  apiKey: string;
  timeoutMs?: number;
  retryAttempts?: number;
}

export interface PaginationInfo {
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
  nextToken: string | null;
  prevToken: string | null;
}

export interface PaginatedResponse<T> {
  status: string;
  message: string;
  data: T[];
  pagination: PaginationInfo;
}

export interface ToolCall {
  id?: string;
  type?: string;
  function: {
    name: string;
    arguments: string;
  };
}

export interface NDJSONChunk {
  status: "processing" | "complete" | "error";
  message: string;
  content?: string;
  knowledge?: string[];
  tools?: ToolCall[];
  audio?: string;
  error?: { code: number; message: string };
  metadata?: Record<string, unknown>;
}

export interface Agent {
  id: string;
  name_id: string;
  name: string;
  description?: string;
  prompt?: string;
  model?: string;
  category?: string;
  public?: boolean;
  active?: boolean;
  stars_count?: number;
  clone_count?: number;
  created_at?: string;
  updated_at?: string;
}

export interface AgentCreateRequest {
  name: string;
  prompt: string;
  description?: string | null;
  model?: string | null;
  category?: string | null;
  public?: boolean;
}

export interface AgentEditRequest {
  name?: string;
  prompt?: string;
  description?: string | null;
  model?: string | null;
  category?: string | null;
  public?: boolean;
  active?: boolean;
}

export interface AgentResponse {
  status: string;
  message: string;
  data: Agent[];
}

export interface DeleteAgentResponse {
  status: string;
  message: string;
}

export interface AgentCompletionRequest extends AgentRequestBase {
  name_id: string;
}

export interface AgentRequestBase {
  prompt: string;
  model?: string;
  context?: string[];
  task_id?: string;
  knowledge?: string | string[];
  memory?: boolean;
  os?: string;
  default_dir?: string;
  current_dir?: string;
  mcp?: unknown;
}

export interface AgentPlanRequest extends AgentRequestBase {
  agent_choice: "auto" | string[];
}

export type AgentEndpoint =
  | "/agent/completion"
  | "/agent/plan"
  | "/agents"
  | "/agents/create"
  | "/agents/edit/{id}"
  | "/agents/{id}";
