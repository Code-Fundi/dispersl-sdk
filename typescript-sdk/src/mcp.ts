import fs from "node:fs";
import path from "node:path";
import { z } from "zod";

const ServerSchema = z.object({
  transport: z.enum(["stdio", "http"]).default("stdio"),
  command: z.string().optional(),
  args: z.array(z.string()).default([]),
  env: z.record(z.string()).default({}),
  enabled: z.boolean().default(true),
  timeout_ms: z.number().int().positive().default(30_000)
});

const McpSchema = z.object({
  version: z.string().default("1"),
  servers: z.record(ServerSchema).default({}),
  tool_policies: z.object({
    allow: z.array(z.string()).default(["*"]),
    deny: z.array(z.string()).default([])
  }).default({ allow: ["*"], deny: [] }),
  defaults: z.object({
    max_tool_calls_per_turn: z.number().int().positive().default(20)
  }).default({ max_tool_calls_per_turn: 20 })
});

export type McpConfig = z.infer<typeof McpSchema>;

export interface CustomTool {
  name: string;
  description: string;
  parameters: Record<string, unknown>;
  execute: (args: Record<string, unknown>) => Promise<unknown> | unknown;
}

export class McpRegistry {
  private readonly tools = new Map<string, CustomTool>();
  register(tool: CustomTool): void {
    this.tools.set(tool.name, tool);
  }
  unregister(name: string): void {
    this.tools.delete(name);
  }
  list(): CustomTool[] {
    return [...this.tools.values()];
  }
}

export class McpConfigLoader {
  loadFromDefaultPath(cwd = process.cwd()): McpConfig {
    const p = path.join(cwd, ".dispersl", "mcp.json");
    if (!fs.existsSync(p)) return McpSchema.parse({});
    const raw = JSON.parse(fs.readFileSync(p, "utf-8")) as Record<string, unknown>;
    return this.interpolateEnv(raw);
  }

  merge(base: McpConfig, override?: Partial<McpConfig>): McpConfig {
    if (!override) return base;
    return McpSchema.parse({
      ...base,
      ...override,
      servers: { ...base.servers, ...(override.servers ?? {}) }
    });
  }

  private interpolateEnv(raw: Record<string, unknown>): McpConfig {
    const text = JSON.stringify(raw).replace(/\$\{([A-Z0-9_]+)\}/g, (_m, name: string) => process.env[name] ?? "");
    return McpSchema.parse(JSON.parse(text));
  }
}
