import { HttpClient } from "./http";
import type {
  Agent,
  AgentCompletionRequest,
  AgentCreateRequest,
  AgentEditRequest,
  AgentPlanRequest,
  AgentResponse,
  DeleteAgentResponse,
  DisperslConfig,
  NDJSONChunk,
  PaginatedResponse
} from "./types";

export class DisperslClient {
  private readonly http: HttpClient;

  constructor(private readonly config: DisperslConfig) {
    this.http = new HttpClient(
      config.baseUrl,
      config.apiKey,
      config.timeoutMs ?? 120_000,
      config.retryAttempts ?? 3
    );
  }

  // ----- Agent endpoints -----
  executeAgentCompletion(request: AgentCompletionRequest): Promise<ReadableStream<Uint8Array>> {
    return this.http.request<ReadableStream<Uint8Array>>("/agent/completion", {
      method: "POST",
      body: JSON.stringify(request)
    });
  }

  executePlan(request: AgentPlanRequest): Promise<ReadableStream<Uint8Array>> {
    const normalizedRequest = {
      ...request,
      agent_choice: request.agent_choice === "auto" ? ["auto"] : request.agent_choice
    };
    return this.http.request<ReadableStream<Uint8Array>>("/agent/plan", {
      method: "POST",
      body: JSON.stringify(normalizedRequest)
    });
  }

  // ----- Agents -----
  getAgents(limit = 20, nextToken?: string): Promise<PaginatedResponse<Agent>> {
    const q = new URLSearchParams({ limit: String(limit) });
    if (nextToken) q.set("nextToken", nextToken);
    return this.http.request(`/agents?${q.toString()}`, { method: "GET" });
  }

  createAgent(body: AgentCreateRequest): Promise<AgentResponse> {
    return this.http.request("/agents/create", {
      method: "POST",
      body: JSON.stringify(body)
    });
  }

  editAgent(id: string, body: AgentEditRequest): Promise<AgentResponse> {
    return this.http.request(`/agents/edit/${id}`, {
      method: "POST",
      body: JSON.stringify(body)
    });
  }

  getAgent(id: string): Promise<AgentResponse> {
    return this.http.request(`/agents/${id}`, { method: "GET" });
  }

  deleteAgent(id: string): Promise<DeleteAgentResponse> {
    return this.http.request(`/agents/${id}`, { method: "DELETE" });
  }

  static isDone(chunk: NDJSONChunk): boolean {
    return chunk.status === "complete" || chunk.status === "error";
  }
}
