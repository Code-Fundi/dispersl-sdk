from __future__ import annotations

from typing import Any

from .http import AsyncHttpClient


class AsyncDisperslClient:
    def __init__(self, base_url: str, api_key: str, timeout_s: float = 120.0, retry_attempts: int = 3) -> None:
        self.http = AsyncHttpClient(base_url, api_key, timeout_s=timeout_s, retry_attempts=retry_attempts)

    # Agent endpoints
    async def agent(self, body: dict[str, Any]) -> Any:
        return await self.http.request("POST", "/agent", json_body=body)

    async def agent_chat(self, body: dict[str, Any]) -> Any:
        return await self.http.request("POST", "/agent/chat", json_body=body)

    async def agent_plan(self, body: dict[str, Any]) -> Any:
        return await self.http.request("POST", "/agent/plan", json_body=body)

    async def agent_code(self, body: dict[str, Any]) -> Any:
        return await self.http.request("POST", "/agent/code", json_body=body)

    async def agent_test(self, body: dict[str, Any]) -> Any:
        return await self.http.request("POST", "/agent/test", json_body=body)

    async def agent_git(self, body: dict[str, Any]) -> Any:
        return await self.http.request("POST", "/agent/git", json_body=body)

    async def agent_document_repo(self, body: dict[str, Any]) -> Any:
        return await self.http.request("POST", "/agent/document/repo", json_body=body)

    # Models
    async def models(self) -> Any:
        return await self.http.request("GET", "/models")

    # API keys
    async def keys(self) -> Any:
        return await self.http.request("GET", "/keys")

    async def keys_new(self, user_id: str, name: str | None = None) -> Any:
        return await self.http.request("POST", "/keys/new", json_body={"user_id": user_id, "name": name})

    # Tasks
    async def tasks_new(self) -> Any:
        return await self.http.request("POST", "/tasks/new")

    async def tasks_edit(self, task_id: str, body: dict[str, Any]) -> Any:
        return await self.http.request("POST", f"/tasks/{task_id}/edit", json_body=body)

    async def tasks(self, limit: int = 20, next_token: str | None = None) -> Any:
        query = f"limit={limit}" + (f"&nextToken={next_token}" if next_token else "")
        return await self.http.request("GET", f"/tasks?{query}")

    async def task(self, task_id: str) -> Any:
        return await self.http.request("GET", f"/tasks/{task_id}")

    async def task_delete(self, task_id: str) -> Any:
        return await self.http.request("DELETE", f"/tasks/{task_id}/delete")

    # Agents
    async def agents(self, limit: int = 20, next_token: str | None = None) -> Any:
        query = f"limit={limit}" + (f"&nextToken={next_token}" if next_token else "")
        return await self.http.request("GET", f"/agents?{query}")

    async def agent_by_id(self, agent_id: str) -> Any:
        return await self.http.request("GET", f"/agents/{agent_id}")

    # Steps
    async def steps_by_task(self, task_id: str, limit: int = 20, next_token: str | None = None) -> Any:
        query = f"limit={limit}" + (f"&nextToken={next_token}" if next_token else "")
        return await self.http.request("GET", f"/steps/task/{task_id}?{query}")

    async def step(self, step_id: str) -> Any:
        return await self.http.request("GET", f"/steps/{step_id}")

    async def step_delete(self, step_id: str) -> Any:
        return await self.http.request("DELETE", f"/steps/{step_id}/delete")

    # History
    async def history_task(self, task_id: str, limit: int = 20, next_token: str | None = None) -> Any:
        query = f"limit={limit}" + (f"&nextToken={next_token}" if next_token else "")
        return await self.http.request("GET", f"/history/task/{task_id}?{query}")

    async def history_step(self, step_id: str, limit: int = 20, next_token: str | None = None) -> Any:
        query = f"limit={limit}" + (f"&nextToken={next_token}" if next_token else "")
        return await self.http.request("GET", f"/history/step/{step_id}?{query}")

    async def aclose(self) -> None:
        await self.http.aclose()
