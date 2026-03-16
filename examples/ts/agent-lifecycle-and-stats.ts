import { DisperslClient } from "@codefundi/dispersl-sdk";

const client = new DisperslClient({
  baseUrl: process.env.DISPERSL_API_URL ?? "https://api.dispersl.com/v1",
  apiKey: process.env.DISPERSL_API_KEY ?? ""
});

async function main() {
  const created = await client.createAgent({
    name: "Security Auditor",
    prompt: "Perform threat-model and compliance-oriented architecture reviews.",
    description: "Internal security review specialist",
    category: "security",
    public: false
  });

  const agentId = created.data[0]?.id;
  if (!agentId) throw new Error("Agent creation response did not include id");

  await client.editAgent(agentId, {
    description: "Updated description from lifecycle example",
    active: true
  });

  const fetched = await client.getAgent(agentId);
  console.log("Fetched agent", fetched.data[0]);

  const list = await client.getAgents(20);
  for (const agent of list.data) {
    console.log({
      id: agent.id,
      nameId: agent.name_id,
      stars: agent.stars_count ?? 0,
      clones: agent.clone_count ?? 0
    });
  }

  await client.deleteAgent(agentId);
  console.log("Deleted agent", agentId);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
