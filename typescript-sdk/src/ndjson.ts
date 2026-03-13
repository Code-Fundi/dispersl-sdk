import type { NDJSONChunk } from "./types";
import { StreamParseError } from "./errors";

export class NdjsonParser {
  async parse(
    stream: ReadableStream<Uint8Array>,
    onChunk?: (chunk: NDJSONChunk) => void | Promise<void>
  ): Promise<void> {
    const reader = stream.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const parsed = JSON.parse(line) as NDJSONChunk;
            if (onChunk) await onChunk(parsed);
          } catch (error) {
            throw new StreamParseError(`Failed parsing NDJSON line: ${line}`, String(error));
          }
        }
      }

      if (buffer.trim()) {
        try {
          const parsed = JSON.parse(buffer) as NDJSONChunk;
          if (onChunk) await onChunk(parsed);
        } catch (error) {
          throw new StreamParseError(`Failed parsing NDJSON tail: ${buffer}`, String(error));
        }
      }
    } finally {
      reader.releaseLock();
    }
  }
}
