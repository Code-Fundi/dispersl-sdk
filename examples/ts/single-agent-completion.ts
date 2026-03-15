import { AgenticExecutor, DisperslClient, type ToolCall } from "@codefundi/dispersl-sdk";

const client = new DisperslClient({
  baseUrl: process.env.DISPERSL_API_URL ?? "https://api.dispersl.com/v1",
  apiKey: process.env.DISPERSL_API_KEY ?? ""
});

async function toolRunner(tool: ToolCall) {
  if (tool.function.name === "end_session") {
    return { toolName: "end_session", status: "success" as const, output: "{}" };
  }
  return { toolName: tool.function.name, status: "success" as const, output: tool.function.arguments };
}

async function main() {
  const executor = new AgenticExecutor(client, toolRunner);
  const out = await executor.runAgentCompletionLoop({
    nameId: "architect",
    prompt: "Review backend resilience and produce concrete hardening actions.",
    maxLoops: 50
  });
  console.log({ taskId: out.taskId, events: out.events.length, tools: out.toolResults.length });
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
