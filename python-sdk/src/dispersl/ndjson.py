from __future__ import annotations

import json
from collections.abc import AsyncIterator

from .errors import StreamParseError
from .models import NDJSONChunk


async def parse_ndjson_stream(lines: AsyncIterator[str]) -> AsyncIterator[NDJSONChunk]:
    buffer = ""
    async for part in lines:
        buffer += part
        split_lines = buffer.split("\n")
        buffer = split_lines.pop() if split_lines else ""
        for raw in split_lines:
            raw = raw.strip()
            if not raw:
                continue
            try:
                yield NDJSONChunk.model_validate(json.loads(raw))
            except Exception as exc:
                raise StreamParseError(f"Failed to parse NDJSON line: {raw}") from exc

    tail = buffer.strip()
    if tail:
        try:
            yield NDJSONChunk.model_validate(json.loads(tail))
        except Exception as exc:
            raise StreamParseError(f"Failed to parse NDJSON tail: {tail}") from exc
