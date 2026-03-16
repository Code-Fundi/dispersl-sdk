import { describe, expect, it, vi } from "vitest";
import { AgenticExecutor } from "../src/executor";
import type { DisperslClient } from "../src/client";

describe("executor loop", () => {
  it("continues with tool feedback when tool executes and no explicit handover/end", async () => {
    const planStream = new ReadableStream<Uint8Array>({
      start(controller) {
        const enc = new TextEncoder();
        controller.enqueue(enc.encode('{"status":"processing","message":"Tool calls","tools":[{"function":{"name":"handover_task","arguments":"{\\"agent_name\\":\\"code\\",\\"prompt\\":\\"go\\"}"}}]}\n'));
        controller.enqueue(enc.encode('{"status":"complete","message":"done"}\n'));
        controller.close();
      }
    });

    const agentStream = new ReadableStream<Uint8Array>({
      start(controller) {
        const enc = new TextEncoder();
        controller.enqueue(enc.encode('{"status":"processing","message":"Tool calls","tools":[{"function":{"name":"end_session","arguments":"{}"}}]}\n'));
        controller.enqueue(enc.encode('{"status":"complete","message":"done"}\n'));
        controller.close();
      }
    });

    const client = {
      executePlan: vi.fn().mockResolvedValue(planStream),
      executeAgentCompletion: vi.fn().mockResolvedValue(agentStream)
    } as unknown as DisperslClient;

    const executor = new AgenticExecutor(client, async (tool) => ({
      toolName: tool.function.name,
      status: "success",
      output: tool.function.arguments
    }));

    const result = await executor.runPlanAndAgentLoop({ prompt: "build sdk", agentChoices: ["code"] });
    expect(result.events.length).toBeGreaterThan(0);
    expect(result.toolResults.map((t) => t.toolName)).toContain("end_session");
  });

  it("supports direct single-agent completion loop until end_session", async () => {
    const firstTurn = new ReadableStream<Uint8Array>({
      start(controller) {
        const enc = new TextEncoder();
        controller.enqueue(enc.encode('{"status":"processing","message":"Tool calls","tools":[{"function":{"name":"read_file","arguments":"{\\"path\\":\\"README.md\\"}"}}]}\n'));
        controller.enqueue(enc.encode('{"status":"complete","message":"turn1 done"}\n'));
        controller.close();
      }
    });

    const secondTurn = new ReadableStream<Uint8Array>({
      start(controller) {
        const enc = new TextEncoder();
        controller.enqueue(enc.encode('{"status":"processing","message":"Tool calls","tools":[{"function":{"name":"end_session","arguments":"{}"}}]}\n'));
        controller.enqueue(enc.encode('{"status":"complete","message":"turn2 done"}\n'));
        controller.close();
      }
    });

    const executeAgentCompletion = vi.fn()
      .mockResolvedValueOnce(firstTurn)
      .mockResolvedValueOnce(secondTurn);
    const client = {
      executeAgentCompletion
    } as unknown as DisperslClient;

    const executor = new AgenticExecutor(client, async (tool) => ({
      toolName: tool.function.name,
      status: "success",
      output: tool.function.arguments
    }));

    const result = await executor.runAgentCompletionLoop({
      nameId: "architect",
      prompt: "Audit architecture"
    });

    expect(executeAgentCompletion).toHaveBeenCalledTimes(2);
    expect(result.toolResults.map((t) => t.toolName)).toContain("end_session");
  });

  it("continues completion loop on text-only turn by feeding back merged content", async () => {
    const textOnlyTurn = new ReadableStream<Uint8Array>({
      start(controller) {
        const enc = new TextEncoder();
        controller.enqueue(enc.encode('{"status":"processing","message":"m","content":"Step 1: do X."}\n'));
        controller.enqueue(enc.encode('{"status":"complete","message":"done","content":"Step 2: do Y."}\n'));
        controller.close();
      }
    });

    const endTurn = new ReadableStream<Uint8Array>({
      start(controller) {
        const enc = new TextEncoder();
        controller.enqueue(enc.encode('{"status":"processing","message":"Tool calls","tools":[{"function":{"name":"end_session","arguments":"{}"}}]}\n'));
        controller.enqueue(enc.encode('{"status":"complete","message":"done"}\n'));
        controller.close();
      }
    });

    const executeAgentCompletion = vi.fn()
      .mockResolvedValueOnce(textOnlyTurn)
      .mockResolvedValueOnce(endTurn);
    const client = { executeAgentCompletion } as unknown as DisperslClient;
    const executor = new AgenticExecutor(client, async (tool) => ({
      toolName: tool.function.name,
      status: "success",
      output: tool.function.arguments
    }));

    await executor.runAgentCompletionLoop({ nameId: "architect", prompt: "Audit architecture" });

    expect(executeAgentCompletion).toHaveBeenCalledTimes(2);
    const secondCallBody = executeAgentCompletion.mock.calls[1][0] as { prompt: string };
    expect(secondCallBody.prompt).toContain("Step 1: do X.");
    expect(secondCallBody.prompt).toContain("Step 2: do Y.");
  });

  it("continues plan loop on text-only turn and re-invokes /agent/plan", async () => {
    const textOnlyPlanTurn = new ReadableStream<Uint8Array>({
      start(controller) {
        const enc = new TextEncoder();
        controller.enqueue(enc.encode('{"status":"processing","message":"m","content":"Draft plan: A then B."}\n'));
        controller.enqueue(enc.encode('{"status":"complete","message":"done","content":"Need specialist agent."}\n'));
        controller.close();
      }
    });

    const handoverPlanTurn = new ReadableStream<Uint8Array>({
      start(controller) {
        const enc = new TextEncoder();
        controller.enqueue(enc.encode('{"status":"processing","message":"Tool calls","tools":[{"function":{"name":"handover_task","arguments":"{\\"agent_name\\":\\"code\\",\\"prompt\\":\\"go\\"}"}}]}\n'));
        controller.enqueue(enc.encode('{"status":"complete","message":"done"}\n'));
        controller.close();
      }
    });

    const endAgentTurn = new ReadableStream<Uint8Array>({
      start(controller) {
        const enc = new TextEncoder();
        controller.enqueue(enc.encode('{"status":"processing","message":"Tool calls","tools":[{"function":{"name":"end_session","arguments":"{}"}}]}\n'));
        controller.enqueue(enc.encode('{"status":"complete","message":"done"}\n'));
        controller.close();
      }
    });

    const executePlan = vi.fn()
      .mockResolvedValueOnce(textOnlyPlanTurn)
      .mockResolvedValueOnce(handoverPlanTurn);
    const executeAgentCompletion = vi.fn().mockResolvedValue(endAgentTurn);
    const client = { executePlan, executeAgentCompletion } as unknown as DisperslClient;
    const executor = new AgenticExecutor(client, async (tool) => ({
      toolName: tool.function.name,
      status: "success",
      output: tool.function.arguments
    }));

    await executor.runPlanAndAgentLoop({ prompt: "build sdk", agentChoices: ["code"] });

    expect(executePlan).toHaveBeenCalledTimes(2);
    const secondCallBody = executePlan.mock.calls[1][0] as { prompt: string };
    expect(secondCallBody.prompt).toContain("Draft plan: A then B.");
    expect(secondCallBody.prompt).toContain("Need specialist agent.");
  });

  it("normalizes plan agentChoices='auto' to agent_choice ['auto']", async () => {
    const planStream = new ReadableStream<Uint8Array>({
      start(controller) {
        const enc = new TextEncoder();
        controller.enqueue(enc.encode('{"status":"complete","message":"done"}\n'));
        controller.close();
      }
    });

    const executePlan = vi.fn().mockResolvedValue(planStream);
    const client = { executePlan } as unknown as DisperslClient;
    const executor = new AgenticExecutor(client);

    await executor.runPlanAndAgentLoop({ prompt: "plan", agentChoices: "auto" });
    const firstCallArg = executePlan.mock.calls[0][0] as { agent_choice: string[] };
    expect(firstCallArg.agent_choice).toEqual(["auto"]);
  });
});
