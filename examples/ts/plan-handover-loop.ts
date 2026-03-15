import { AgenticExecutor, DisperslClient, type ToolCall } from "@codefundi/dispersl-sdk";

const client = new DisperslClient({
  baseUrl: process.env.DISPERSL_API_URL ?? "https://api.dispersl.com/v1",
  apiKey: process.env.DISPERSL_API_KEY ?? ""
});

async function localToolRunner(tool: ToolCall) {
  if (tool.function.name === "end_session" || tool.function.name === "finish_task") {
    return { toolName: tool.function.name, status: "success" as const, output: "{}" };
  }
  return {
    toolName: tool.function.name,
    status: "success" as const,
    output: tool.function.arguments
  };
}

async function main() {
  const executor = new AgenticExecutor(client, localToolRunner);
  const out = await executor.runPlanAndAgentLoop({
    prompt: "Design and implement an audit-ready API release workflow.",
    agentChoices: "auto",
    maxLoops: 50
  });
  console.log({ taskId: out.taskId, events: out.events.length, tools: out.toolResults.length });
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
