import { AgenticExecutor, DisperslClient } from "@codefundi/dispersl-sdk";

const client = new DisperslClient({
  baseUrl: process.env.DISPERSL_API_URL ?? "https://api.dispersl.com/v1",
  apiKey: process.env.DISPERSL_API_KEY ?? ""
});

async function main() {
  const executor = new AgenticExecutor(client, async (tool) => {
    if (tool.function.name === "get_release_calendar") {
      return {
        toolName: "get_release_calendar",
        status: "success" as const,
        output: JSON.stringify({ freezeDate: "2026-04-15", releaseDate: "2026-04-22" })
      };
    }
    return { toolName: tool.function.name, status: "success" as const, output: tool.function.arguments };
  });

  executor.mcpTools.register({
    name: "get_release_calendar",
    description: "Return release calendar dates for planning and rollout.",
    parameters: {
      type: "object",
      properties: {},
      required: []
    },
    execute: async () => ({ freezeDate: "2026-04-15", releaseDate: "2026-04-22" })
  });

  const planned = await executor.runPlanAndAgentLoop({
    prompt: "Create a release plan for onboarding automation in regulated environments.",
    agentChoices: "auto"
  });
  console.log("Planned task", planned.taskId);

  const completed = await executor.runAgentCompletionLoop({
    nameId: "release-manager",
    prompt: "Finalize the release checklist using available custom tools."
  });
  console.log("Completion events", completed.events.length);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
