import { randomUUID } from "node:crypto";
import type { NDJSONChunk, ToolCall } from "./types";
import { DisperslClient } from "./client";
import { NdjsonParser } from "./ndjson";
import { McpConfigLoader, McpRegistry, type McpConfig } from "./mcp";
import { mergeNextAction, nextActionFromTool, type NextAction } from "./handover";
import { ToolExecutionError } from "./errors";

export interface ToolResult {
  toolName: string;
  status: "success" | "error";
  output: string;
  error?: string;
}

export type ToolExecutorFn = (tool: ToolCall) => Promise<ToolResult>;

export class AgenticExecutor {
  private normalizeAgentChoices(agentChoices: "auto" | string[]): string[] {
    return agentChoices === "auto" ? ["auto"] : agentChoices;
  }

  private cleanText(value: unknown): string | undefined {
    if (typeof value !== "string") return undefined;
    const t = value.trim();
    return t.length ? t : undefined;
  }

  private mergeTurnText(parts: string[]): string | undefined {
    const merged = parts.map((p) => p.trim()).filter(Boolean).join("\n");
    return merged.length ? merged : undefined;
  }

  private buildPlanTextContinuationPrompt(previousPrompt: string, turnText: string): string {
    return [
      "You previously responded with streamed text (no tool calls).",
      `Previous assignment: ${previousPrompt}`,
      "Your latest output:",
      turnText,
      "Continue planning and proceed with the workflow.",
      "If you need to hand over, call handover_task. If done, call end_session."
    ].join("\n");
  }

  private buildCompletionTextContinuationPrompt(agentId: string, previousPrompt: string, turnText: string): string {
    return [
      `You are ${agentId} continuing the same task.`,
      `Previous assignment: ${previousPrompt}`,
      "Your latest output:",
      turnText,
      "Continue with the next steps.",
      "If you need tools, call them. If done, call end_session."
    ].join("\n");
  }

  private readonly parser = new NdjsonParser();
  private readonly mcpLoader = new McpConfigLoader();
  readonly mcpTools = new McpRegistry();

  constructor(private readonly client: DisperslClient, private readonly toolExecutor?: ToolExecutorFn) {}

  async runAgentCompletionLoop(args: {
    nameId: string;
    prompt: string;
    model?: string;
    taskId?: string;
    mcpOverride?: Partial<McpConfig>;
    maxLoops?: number;
  }): Promise<{ taskId: string; events: NDJSONChunk[]; toolResults: ToolResult[] }> {
    const taskId = args.taskId ?? randomUUID();
    const maxLoops = args.maxLoops ?? 50;
    const events: NDJSONChunk[] = [];
    const toolResults: ToolResult[] = [];

    const localMcp = this.mcpLoader.loadFromDefaultPath();
    const mergedMcp = this.mcpLoader.merge(localMcp, args.mcpOverride);
    const runtimeTools = this.mcpTools.list().map((tool) => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.parameters
    }));

    let currentPrompt = args.prompt;
    let loop = 0;
    let keepRunning = true;

    while (keepRunning && loop < maxLoops) {
      loop += 1;
      const stream = await this.client.executeAgentCompletion({
        name_id: args.nameId,
        prompt: currentPrompt,
        ...(args.model ? { model: args.model } : {}),
        task_id: taskId,
        mcp: { ...mergedMcp, tools: runtimeTools }
      });

      let nextAction: NextAction = { type: "none" };
      const turnToolResults: ToolResult[] = [];
      let sawTools = false;
      const turnTextParts: string[] = [];

      await this.parser.parse(stream, async (chunk) => {
        events.push(chunk);
        const text = this.cleanText(chunk.content) ?? this.cleanText(chunk.message);
        if (text) turnTextParts.push(text);
        if (!chunk.tools?.length) return;
        sawTools = true;
        for (const tool of chunk.tools) {
          nextAction = mergeNextAction(nextAction, nextActionFromTool(tool));
          if (!this.toolExecutor) continue;
          const result = await this.toolExecutor(tool);
          turnToolResults.push(result);
          toolResults.push(result);
          if (result.status === "error") {
            throw new ToolExecutionError(`Tool ${result.toolName} failed: ${result.error ?? "unknown"}`);
          }
        }
      });

      if (nextAction.type === "end") {
        keepRunning = false;
        continue;
      }

      if (turnToolResults.length > 0) {
        currentPrompt = this.buildSingleAgentToolFeedbackPrompt(args.nameId, currentPrompt, turnToolResults);
      } else if (!sawTools) {
        const mergedText = this.mergeTurnText(turnTextParts);
        if (mergedText) {
          currentPrompt = this.buildCompletionTextContinuationPrompt(args.nameId, currentPrompt, mergedText);
        }
        continue;
      } else if (!this.toolExecutor) {
        keepRunning = false;
      }
    }

    return { taskId, events, toolResults };
  }

  async runPlanAndAgentLoop(args: {
    prompt: string;
    agentChoices: "auto" | string[];
    model?: string;
    taskId?: string;
    mcpOverride?: Partial<McpConfig>;
    maxLoops?: number;
  }): Promise<{ taskId: string; events: NDJSONChunk[]; toolResults: ToolResult[] }> {
    const taskId = args.taskId ?? randomUUID();
    const maxLoops = args.maxLoops ?? 50;
    const events: NDJSONChunk[] = [];
    const toolResults: ToolResult[] = [];
    const agentChoices = this.normalizeAgentChoices(args.agentChoices);

    const localMcp = this.mcpLoader.loadFromDefaultPath();
    const mergedMcp = this.mcpLoader.merge(localMcp, args.mcpOverride);
    const runtimeTools = this.mcpTools.list().map((tool) => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.parameters
    }));

    let step: "plan" | "agent" = "plan";
    let currentAgent: string | undefined;
    let currentPrompt = args.prompt;
    let loop = 0;
    let keepRunning = true;

    while (keepRunning && loop < maxLoops) {
      loop += 1;
      const stream = step === "plan"
        ? await this.client.executePlan({
            prompt: currentPrompt,
            agent_choice: agentChoices,
            ...(args.model ? { model: args.model } : {}),
            task_id: taskId,
            mcp: { ...mergedMcp, tools: runtimeTools }
          })
        : await this.client.executeAgentCompletion({
            name_id: currentAgent ?? "",
            prompt: currentPrompt,
            ...(args.model ? { model: args.model } : {}),
            task_id: taskId,
            mcp: { ...mergedMcp, tools: runtimeTools }
          });

      let nextAction: NextAction = { type: "none" };
      const turnToolResults: ToolResult[] = [];
      let sawTools = false;
      const turnTextParts: string[] = [];

      await this.parser.parse(stream, async (chunk) => {
        events.push(chunk);
        const text = this.cleanText(chunk.content) ?? this.cleanText(chunk.message);
        if (text) turnTextParts.push(text);
        if (!chunk.tools?.length) return;
        sawTools = true;
        for (const tool of chunk.tools) {
          nextAction = mergeNextAction(nextAction, nextActionFromTool(tool));
          if (!this.toolExecutor) continue;
          const result = await this.toolExecutor(tool);
          turnToolResults.push(result);
          toolResults.push(result);
          if (result.status === "error") {
            throw new ToolExecutionError(`Tool ${result.toolName} failed: ${result.error ?? "unknown"}`);
          }
          if (tool.function.name === "handover_task") {
            try {
              const payload = JSON.parse(result.output) as Record<string, unknown>;
              nextAction = mergeNextAction(nextAction, nextActionFromTool({
                type: "handover_task",
                ...payload
              }));
            } catch {
              // no-op: keep parsed action from raw tool
            }
          }
        }
      });

      if (nextAction.type === "handover" && nextAction.toAgent) {
        step = "agent";
        currentAgent = nextAction.toAgent;
        currentPrompt = nextAction.prompt ?? "Continue with the same task.";
        continue;
      }

      if (nextAction.type === "end") {
        keepRunning = false;
        continue;
      }

      if (step === "plan") {
        if (!sawTools) {
          // Plan responded with text-only content and no tools; per spec,
          // call /agent/plan again with the same parameters to continue.
          const mergedText = this.mergeTurnText(turnTextParts);
          if (mergedText) {
            currentPrompt = this.buildPlanTextContinuationPrompt(currentPrompt, mergedText);
          }
          continue;
        }
        keepRunning = false;
        continue;
      }

      if (turnToolResults.length > 0) {
        currentPrompt = this.buildToolFeedbackPrompt(currentAgent ?? "agent", currentPrompt, turnToolResults);
      } else if (!sawTools) {
        const mergedText = this.mergeTurnText(turnTextParts);
        if (mergedText) {
          currentPrompt = this.buildCompletionTextContinuationPrompt(currentAgent ?? "agent", currentPrompt, mergedText);
        }
        continue;
      } else if (!this.toolExecutor) {
        keepRunning = false;
      }
    }

    return { taskId, events, toolResults };
  }

  private buildToolFeedbackPrompt(agentId: string, previousPrompt: string, toolResults: ToolResult[]): string {
    const lines = toolResults.map((r, idx) => {
      const resultText = r.status === "success" ? r.output : `ERROR: ${r.error ?? "unknown"}`;
      return `${idx + 1}. ${r.toolName} => ${r.status.toUpperCase()} => ${resultText}`;
    });
    return [
      `You are ${agentId} continuing the same task.`,
      `Previous assignment: ${previousPrompt}`,
      "Tool results:",
      ...lines,
      "Decide your next step. If another specialist is needed, call handover_task. If done, call end_session."
    ].join("\n");
  }

  private buildSingleAgentToolFeedbackPrompt(agentId: string, previousPrompt: string, toolResults: ToolResult[]): string {
    const lines = toolResults.map((r, idx) => {
      const resultText = r.status === "success" ? r.output : `ERROR: ${r.error ?? "unknown"}`;
      return `${idx + 1}. ${r.toolName} => ${r.status.toUpperCase()} => ${resultText}`;
    });
    return [
      `You are ${agentId} continuing the same task.`,
      `Previous assignment: ${previousPrompt}`,
      "Tool results:",
      ...lines,
      "Continue as the same agent and call end_session when complete. Do not hand over to another agent."
    ].join("\n");
  }
}
