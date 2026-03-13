import pytest

from dispersl.ndjson import parse_ndjson_stream


@pytest.mark.asyncio
async def test_ndjson_parses_split_chunks() -> None:
    async def lines():
        yield '{"status":"processing","message":"Content'
        yield ' chunk","content":"A"}\n{"status":"complete","message":"done"}\n'

    out = []
    async for chunk in parse_ndjson_stream(lines()):
        out.append(chunk.message)
    assert out == ["Content chunk", "done"]
