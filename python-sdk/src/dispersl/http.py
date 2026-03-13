from __future__ import annotations

import asyncio
import random
from typing import Any

import httpx

from .errors import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)


def _map_status(code: int, message: str) -> Exception:
    if code in {401, 403}:
        return AuthenticationError(message)
    if code == 404:
        return NotFoundError(message)
    if code == 409:
        return ConflictError(message)
    if code == 429:
        return RateLimitError(message)
    if 400 <= code < 500:
        return ValidationError(message)
    return ServerError(message)


class AsyncHttpClient:
    def __init__(self, base_url: str, api_key: str, timeout_s: float = 120.0, retry_attempts: int = 3) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.retry_attempts = retry_attempts
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout_s,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )

    async def request(self, method: str, path: str, json_body: dict[str, Any] | None = None) -> Any:
        last_error: Exception | None = None
        for attempt in range(self.retry_attempts + 1):
            try:
                response = await self.client.request(method, path, json=json_body)
                if response.status_code < 400:
                    if "application/json" in response.headers.get("content-type", ""):
                        return response.json()
                    return response

                retryable = response.status_code in {408, 429} or response.status_code >= 500
                if retryable and attempt < self.retry_attempts:
                    delay = min(0.3 * (2**attempt) + random.random() * 0.1, 10.0)
                    await asyncio.sleep(delay)
                    continue
                raise _map_status(response.status_code, response.text)
            except httpx.TimeoutException as exc:
                last_error = TimeoutError(str(exc))
                if attempt < self.retry_attempts:
                    delay = min(0.3 * (2**attempt) + random.random() * 0.1, 10.0)
                    await asyncio.sleep(delay)
                    continue
            except Exception as exc:
                last_error = exc if isinstance(exc, Exception) else Exception(str(exc))
                if attempt < self.retry_attempts:
                    delay = min(0.3 * (2**attempt) + random.random() * 0.1, 10.0)
                    await asyncio.sleep(delay)
                    continue
        raise last_error if last_error else RuntimeError("Request failed")

    async def aclose(self) -> None:
        await self.client.aclose()
