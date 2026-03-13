from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class MCPTool:
    name: str
    description: str
    parameters: dict[str, Any]
    execute: Callable[[dict[str, Any]], Any]


@dataclass
class MCPConfig:
    version: str = "1"
    servers: dict[str, dict[str, Any]] = field(default_factory=dict)
    tool_policies: dict[str, list[str]] = field(default_factory=lambda: {"allow": ["*"], "deny": []})
    defaults: dict[str, Any] = field(default_factory=lambda: {"max_tool_calls_per_turn": 20})


class MCPRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, MCPTool] = {}

    def register(self, tool: MCPTool) -> None:
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        self._tools.pop(name, None)

    def list(self) -> list[MCPTool]:
        return list(self._tools.values())


class MCPConfigLoader:
    def load_default(self, cwd: str | None = None) -> MCPConfig:
        root = Path(cwd or os.getcwd())
        config_path = root / ".dispersl" / "mcp.json"
        if not config_path.exists():
            return MCPConfig()
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        return self._interpolate(raw)

    def merge(self, base: MCPConfig, override: dict[str, Any] | None) -> MCPConfig:
        if not override:
            return base
        merged = {
            "version": override.get("version", base.version),
            "servers": {**base.servers, **override.get("servers", {})},
            "tool_policies": {**base.tool_policies, **override.get("tool_policies", {})},
            "defaults": {**base.defaults, **override.get("defaults", {})},
        }
        return MCPConfig(**merged)

    def _interpolate(self, raw: dict[str, Any]) -> MCPConfig:
        text = json.dumps(raw)
        for key, value in os.environ.items():
            text = text.replace(f"${{{key}}}", value)
        return MCPConfig(**json.loads(text))
