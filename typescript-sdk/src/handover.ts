export type NextAction = { type: "handover" | "end" | "none"; toAgent?: string; prompt?: string };

function clean(value: unknown): string | undefined {
  if (typeof value !== "string") return undefined;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}

function parseLooseObject(value: unknown): Record<string, unknown> {
  if (typeof value === "object" && value !== null) return value as Record<string, unknown>;
  if (typeof value !== "string") return {};

  let parsed: unknown = value;
  for (let i = 0; i < 2; i += 1) {
    if (typeof parsed !== "string") break;
    try {
      parsed = JSON.parse(parsed);
    } catch {
      return {};
    }
  }
  return typeof parsed === "object" && parsed !== null ? (parsed as Record<string, unknown>) : {};
}

export function extractHandover(output: unknown): { toAgent?: string; prompt?: string } {
  const record = parseLooseObject(output);
  const toAgent = clean(record.agent_name) ?? clean(record.to_agent) ?? clean(record.agent) ?? clean(record.name);
  const prompt = clean(record.prompt) ?? clean(record.instructions) ?? clean(record.message);
  const result: { toAgent?: string; prompt?: string } = {};
  if (toAgent) result.toAgent = toAgent;
  if (prompt) result.prompt = prompt;
  return result;
}

export function nextActionFromTool(rawTool: unknown): NextAction {
  const record = typeof rawTool === "object" && rawTool !== null ? (rawTool as Record<string, unknown>) : {};
  const fn = typeof record.function === "object" && record.function !== null
    ? (record.function as Record<string, unknown>)
    : {};
  const name = clean(fn.name) ?? clean(record.type) ?? clean(record.name);

  if (!name) return { type: "none" };
  if (name === "end_session" || name === "finish_task") return { type: "end" };
  if (name !== "handover_task") return { type: "none" };

  const merged = { ...record, ...parseLooseObject(fn.arguments ?? record.arguments) };
  const toAgent = clean(merged.agent_name) ?? clean(merged.to_agent) ?? clean(merged.agent) ?? clean(merged.name);
  const prompt = clean(merged.prompt) ?? clean(merged.instructions) ?? clean(merged.message);
  if (!toAgent) return { type: "none" };
  return prompt ? { type: "handover", toAgent, prompt } : { type: "handover", toAgent };
}

export function mergeNextAction(current: NextAction, candidate: NextAction): NextAction {
  if (candidate.type === "none") return current;
  if (candidate.type === "end" || current.type === "end") return candidate.type === "end" ? candidate : current;
  if (candidate.type === "handover" && candidate.toAgent) return candidate;
  return current;
}
