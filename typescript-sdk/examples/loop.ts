import { AgenticExecutor, DisperslClient } from "../src";

const client = new DisperslClient({
  baseUrl: process.env.DISPERSL_API_URL ?? "https://api.dispersl.com/v1",
  apiKey: process.env.DISPERSL_API_KEY ?? ""
});

const executor = new AgenticExecutor(client, async (tool): Promise<{ toolName: string; status: "success"; output: string }> => {
  if (tool.function.name === "end_session") {
    return { toolName: "end_session", status: "success", output: "Session ended" };
  }
  return { toolName: tool.function.name, status: "success", output: tool.function.arguments };
});

const run = async () => {
  const out = await executor.runPlanAndAgentLoop({
    prompt: "Plan and build API SDK integration",
    agentChoices: ["code", "test", "git", "docs"]
  });
  console.log("taskId", out.taskId);
  console.log("eventCount", out.events.length);
};

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
