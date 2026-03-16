import { DisperslClient } from "@codefundi/dispersl-sdk";

const client = new DisperslClient({
  baseUrl: process.env.DISPERSL_API_URL ?? "https://api.dispersl.com/v1",
  apiKey: process.env.DISPERSL_API_KEY ?? ""
});

async function main() {
  const taskId = process.env.DISPERSL_TASK_ID ?? "replace-with-existing-task-id";
  const stream = await client.executeAgentCompletion({
    name_id: "architect",
    prompt: "Summarize current progress and list remaining risks.",
    task_id: taskId
  });

  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.trim()) continue;
      const chunk = JSON.parse(line) as { status: string; message: string; content?: string };
      console.log(`[${chunk.status}] ${chunk.message}`);
      if (chunk.content) {
        console.log(chunk.content);
      }
    }
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
