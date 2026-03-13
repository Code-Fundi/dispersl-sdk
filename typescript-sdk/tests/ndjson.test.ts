import { describe, expect, it } from "vitest";
import { NdjsonParser } from "../src/ndjson";

function toStream(lines: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream({
    start(controller) {
      for (const line of lines) controller.enqueue(encoder.encode(line));
      controller.close();
    }
  });
}

describe("ndjson parser", () => {
  it("parses chunks split across frames", async () => {
    const parser = new NdjsonParser();
    const items: string[] = [];
    await parser.parse(
      toStream(['{"status":"processing","message":"Content', ' chunk","content":"A"}\n{"status":"complete","message":"done"}\n']),
      (chunk) => {
        items.push(chunk.message);
      }
    );
    expect(items).toEqual(["Content chunk", "done"]);
  });
});
