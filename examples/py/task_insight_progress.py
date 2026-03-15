import asyncio

from dispersl import AsyncDisperslClient
from dispersl.ndjson import parse_ndjson_stream


async def main() -> None:
    client = AsyncDisperslClient(
        base_url="https://api.dispersl.com/v1",
        api_key="YOUR_API_KEY",
    )
    task_id = "replace-with-existing-task-id"
    stream_response = await client.agent_completion(
        {
            "name_id": "architect",
            "prompt": "Summarize current progress and list remaining risks.",
            "task_id": task_id,
        }
    )

    async def _lines():
        async for raw in stream_response.aiter_text():
            yield raw

    async for chunk in parse_ndjson_stream(_lines()):
        print(f"[{chunk.status}] {chunk.message}")
        if chunk.content:
            print(chunk.content)

    await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
