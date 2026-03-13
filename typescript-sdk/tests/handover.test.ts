import { describe, expect, it } from "vitest";
import { nextActionFromTool } from "../src/handover";

describe("handover parser", () => {
  it("supports top-level payload", () => {
    expect(nextActionFromTool({ type: "handover_task", agent_name: "risk-manager", prompt: "Check risk" }))
      .toEqual({ type: "handover", toAgent: "risk-manager", prompt: "Check risk" });
  });

  it("supports function payload and double-serialized args", () => {
    const inner = JSON.stringify({ to_agent: "technical-analyst", message: "Run analysis" });
    expect(nextActionFromTool({ function: { name: "handover_task", arguments: JSON.stringify(inner) } }))
      .toEqual({ type: "handover", toAgent: "technical-analyst", prompt: "Run analysis" });
  });

  it("prioritizes end marker detection", () => {
    expect(nextActionFromTool({ type: "end_session" })).toEqual({ type: "end" });
  });
});
