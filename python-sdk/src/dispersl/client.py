from __future__ import annotations

from typing import Any

from .http import AsyncHttpClient


class AsyncDisperslClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout_s: float = 120.0,
        retry_attempts: int = 3,
    ) -> None:
        self.http = AsyncHttpClient(
            base_url,
            api_key,
            timeout_s=timeout_s,
            retry_attempts=retry_attempts,
        )

    # Agent execution endpoints
    async def agent_completion(self, body: dict[str, Any]) -> Any:
        return await self.http.request("POST", "/agent/completion", json_body=body)

    async def agent_plan(self, body: dict[str, Any]) -> Any:
        normalized_body = dict(body)
        if normalized_body.get("agent_choice") == "auto":
            normalized_body["agent_choice"] = ["auto"]
        return await self.http.request("POST", "/agent/plan", json_body=normalized_body)

    # Agent lifecycle endpoints
    async def agents(self, limit: int = 20, next_token: str | None = None) -> Any:
        query = f"limit={limit}" + (f"&nextToken={next_token}" if next_token else "")
        return await self.http.request("GET", f"/agents?{query}")

    async def agents_create(self, body: dict[str, Any]) -> Any:
        return await self.http.request("POST", "/agents/create", json_body=body)

    async def agents_edit(self, agent_id: str, body: dict[str, Any]) -> Any:
        return await self.http.request("POST", f"/agents/edit/{agent_id}", json_body=body)

    async def agent_by_id(self, agent_id: str) -> Any:
        return await self.http.request("GET", f"/agents/{agent_id}")

    async def agent_delete(self, agent_id: str) -> Any:
        return await self.http.request("DELETE", f"/agents/{agent_id}")

    async def aclose(self) -> None:
        await self.http.aclose()
