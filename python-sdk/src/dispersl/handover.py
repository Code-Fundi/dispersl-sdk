from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NextAction:
    type: str
    to_agent: str | None = None
    prompt: str | None = None


def _clean(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    v = value.strip()
    return v if v else None


def _parse_loose_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        return {}
    parsed: Any = value
    for _ in range(2):
        if not isinstance(parsed, str):
            break
        try:
            parsed = json.loads(parsed)
        except Exception:
            return {}
    return parsed if isinstance(parsed, dict) else {}


def next_action_from_tool(raw_tool: dict[str, Any]) -> NextAction:
    function_raw = raw_tool.get("function")
    function = function_raw if isinstance(function_raw, dict) else {}
    name = (
        _clean(function.get("name")) or _clean(raw_tool.get("type")) or _clean(raw_tool.get("name"))
    )
    if not name:
        return NextAction(type="none")
    if name in {"end_session", "finish_task"}:
        return NextAction(type="end")
    if name != "handover_task":
        return NextAction(type="none")

    args = _parse_loose_object(function.get("arguments", raw_tool.get("arguments")))
    merged = {**raw_tool, **args}
    to_agent = (
        _clean(merged.get("agent_name"))
        or _clean(merged.get("to_agent"))
        or _clean(merged.get("agent"))
        or _clean(merged.get("name"))
    )
    prompt = (
        _clean(merged.get("prompt"))
        or _clean(merged.get("instructions"))
        or _clean(merged.get("message"))
    )
    if not to_agent:
        return NextAction(type="none")
    return NextAction(type="handover", to_agent=to_agent, prompt=prompt)
