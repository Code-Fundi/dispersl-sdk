import { AgenticExecutor, DisperslClient } from "../src";

const client = new DisperslClient({
  baseUrl: process.env.DISPERSL_API_URL ?? "https://api.dispersl.com/v1",
  apiKey: process.env.DISPERSL_API_KEY ?? ""
});

const executor = new AgenticExecutor(client);
executor.mcpTools.register({
  name: "get_github_user",
  description: "Get public GitHub user profile",
  parameters: {
    type: "object",
    properties: { username: { type: "string" } },
    required: ["username"]
  },
  execute: async (args: Record<string, unknown>) => {
    const username = String(args.username);
    const res = await fetch(`https://api.github.com/users/${username}`);
    return res.json();
  }
});
