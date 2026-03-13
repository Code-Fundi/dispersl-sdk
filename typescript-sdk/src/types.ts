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
  name: string;
  name_id: string;
  description: string;
  prompt?: string;
}

export interface Task {
  id?: string;
  task_id?: string;
  name?: string;
  description?: string;
  status?: string;
  created_at?: string;
}

export interface Step {
  id: string;
  task_id: string;
  name: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface AgentRequestBase {
  prompt: string;
  model?: string;
  context?: string[];
  task_id?: string;
  knowledge?: string[];
  memory?: boolean;
  os?: string;
  default_dir?: string;
  current_dir?: string;
  mcp?: unknown;
}

export interface AgentPlanRequest extends AgentRequestBase {
  agent_choice: string[];
}

export type AgentEndpoint =
  | "/agent"
  | "/agent/chat"
  | "/agent/plan"
  | "/agent/code"
  | "/agent/test"
  | "/agent/git"
  | "/agent/document/repo";
