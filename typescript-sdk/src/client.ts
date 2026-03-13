import { HttpClient } from "./http";
import type { Agent, AgentPlanRequest, AgentRequestBase, DisperslConfig, NDJSONChunk, PaginatedResponse, Step, Task } from "./types";

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
  executeAgent(request: { name_id: string } & AgentRequestBase): Promise<ReadableStream<Uint8Array>> {
    return this.http.request<ReadableStream<Uint8Array>>("/agent", {
      method: "POST",
      body: JSON.stringify(request)
    });
  }

  executeChat(request: AgentRequestBase): Promise<ReadableStream<Uint8Array>> {
    return this.http.request<ReadableStream<Uint8Array>>("/agent/chat", {
      method: "POST",
      body: JSON.stringify(request)
    });
  }

  executePlan(request: AgentPlanRequest): Promise<ReadableStream<Uint8Array>> {
    return this.http.request<ReadableStream<Uint8Array>>("/agent/plan", {
      method: "POST",
      body: JSON.stringify(request)
    });
  }

  executeCode(request: AgentRequestBase): Promise<ReadableStream<Uint8Array>> {
    return this.http.request<ReadableStream<Uint8Array>>("/agent/code", {
      method: "POST",
      body: JSON.stringify(request)
    });
  }

  executeTest(request: AgentRequestBase): Promise<ReadableStream<Uint8Array>> {
    return this.http.request<ReadableStream<Uint8Array>>("/agent/test", {
      method: "POST",
      body: JSON.stringify(request)
    });
  }

  executeGit(request: AgentRequestBase): Promise<ReadableStream<Uint8Array>> {
    return this.http.request<ReadableStream<Uint8Array>>("/agent/git", {
      method: "POST",
      body: JSON.stringify(request)
    });
  }

  generateRepoDocs(request: { url: string; branch: string; model?: string; team_access?: boolean; task_id?: string }): Promise<ReadableStream<Uint8Array>> {
    return this.http.request<ReadableStream<Uint8Array>>("/agent/document/repo", {
      method: "POST",
      body: JSON.stringify(request)
    });
  }

  // ----- Models -----
  getModels(): Promise<{ models: Array<{ id: string; name: string }>; status: string }> {
    return this.http.request("/models", { method: "GET" });
  }

  // ----- API keys -----
  getKeys(): Promise<{ apiKeys: Array<{ name: string; publicKey: string; created_at: string }> }> {
    return this.http.request("/keys", { method: "GET" });
  }

  createKey(user_id: string, name?: string): Promise<{ publicKey: string; message: string }> {
    return this.http.request("/keys/new", {
      method: "POST",
      body: JSON.stringify({ user_id, name })
    });
  }

  // ----- Tasks -----
  createTask(): Promise<{ status: string; message: string; data: Task[] }> {
    return this.http.request("/tasks/new", { method: "POST" });
  }

  editTask(id: string, body: { name?: string; status?: string }): Promise<{ status: string; message: string; data: Task[] }> {
    return this.http.request(`/tasks/${id}/edit`, {
      method: "POST",
      body: JSON.stringify(body)
    });
  }

  getTasks(limit = 20, nextToken?: string): Promise<PaginatedResponse<Task>> {
    const q = new URLSearchParams({ limit: String(limit) });
    if (nextToken) q.set("nextToken", nextToken);
    return this.http.request(`/tasks?${q.toString()}`, { method: "GET" });
  }

  getTask(id: string): Promise<{ status: string; message: string; data: Task[] }> {
    return this.http.request(`/tasks/${id}`, { method: "GET" });
  }

  deleteTask(id: string): Promise<{ status: string; message: string; data: Task[] }> {
    return this.http.request(`/tasks/${id}/delete`, { method: "DELETE" });
  }

  // ----- Agents -----
  getAgents(limit = 20, nextToken?: string): Promise<PaginatedResponse<Agent>> {
    const q = new URLSearchParams({ limit: String(limit) });
    if (nextToken) q.set("nextToken", nextToken);
    return this.http.request(`/agents?${q.toString()}`, { method: "GET" });
  }

  getAgent(id: string): Promise<{ status: string; message: string; data: Agent[] }> {
    return this.http.request(`/agents/${id}`, { method: "GET" });
  }

  // ----- Steps -----
  getStepsByTask(taskId: string, limit = 20, nextToken?: string): Promise<PaginatedResponse<Step>> {
    const q = new URLSearchParams({ limit: String(limit) });
    if (nextToken) q.set("nextToken", nextToken);
    return this.http.request(`/steps/task/${taskId}?${q.toString()}`, { method: "GET" });
  }

  getStep(id: string): Promise<{ status: string; message: string; data: Step[] }> {
    return this.http.request(`/steps/${id}`, { method: "GET" });
  }

  deleteStep(id: string): Promise<{ status: string; message: string; data: Step[] }> {
    return this.http.request(`/steps/${id}/delete`, { method: "DELETE" });
  }

  // ----- History -----
  getTaskHistory(taskId: string, limit = 20, nextToken?: string): Promise<PaginatedResponse<Record<string, unknown>>> {
    const q = new URLSearchParams({ limit: String(limit) });
    if (nextToken) q.set("nextToken", nextToken);
    return this.http.request(`/history/task/${taskId}?${q.toString()}`, { method: "GET" });
  }

  getStepHistory(stepId: string, limit = 20, nextToken?: string): Promise<PaginatedResponse<Record<string, unknown>>> {
    const q = new URLSearchParams({ limit: String(limit) });
    if (nextToken) q.set("nextToken", nextToken);
    return this.http.request(`/history/step/${stepId}?${q.toString()}`, { method: "GET" });
  }

  static isDone(chunk: NDJSONChunk): boolean {
    return chunk.status === "complete" || chunk.status === "error";
  }
}
