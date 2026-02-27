"""HTTP client for the Zube.io API with automatic token management."""

from __future__ import annotations

import json
import time
from typing import Any

import httpx

from .auth import create_refresh_jwt

BASE_URL = "https://zube.io/api"

_STATUS_MESSAGES = {
    401: "Authentication failed — token may have expired",
    403: "Permission denied — check your API key scopes",
    404: "Not found — the requested resource does not exist",
    422: "Validation error — check your request parameters",
    429: "Rate limited — wait a moment and try again",
}


class ZubeClient:
    def __init__(self, client_id: str, private_key: str):
        self._client_id = client_id
        self._private_key = private_key
        self._access_token: str | None = None
        self._token_expires_at: float = 0
        self._http = httpx.AsyncClient(base_url=BASE_URL, timeout=30)

    async def close(self) -> None:
        await self._http.aclose()

    async def _ensure_token(self) -> None:
        if self._access_token and time.time() < self._token_expires_at:
            return

        refresh_jwt = create_refresh_jwt(self._client_id, self._private_key)
        resp = await self._http.post(
            "/users/tokens",
            headers={
                "Authorization": f"Bearer {refresh_jwt}",
                "X-Client-ID": self._client_id,
                "Accept": "application/json",
            },
        )
        resp.raise_for_status()
        self._access_token = resp.json()["access_token"]
        self._token_expires_at = time.time() + 23 * 3600  # refresh before 24h expiry

    def _read_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "X-Client-ID": self._client_id,
            "Accept": "application/json",
        }

    def _write_headers(self) -> dict[str, str]:
        return {
            **self._read_headers(),
            "Content-Type": "application/json",
        }

    def _raise_friendly(self, resp: httpx.Response) -> None:
        if resp.is_success:
            return
        message = _STATUS_MESSAGES.get(resp.status_code)
        if message:
            detail = ""
            try:
                body = resp.json()
                if "message" in body:
                    detail = f": {body['message']}"
            except (ValueError, json.JSONDecodeError):
                pass
            raise httpx.HTTPStatusError(
                f"{message}{detail}",
                request=resp.request,
                response=resp,
            )
        resp.raise_for_status()

    async def get(self, path: str, params: Any = None) -> dict:
        await self._ensure_token()
        resp = await self._http.get(path, headers=self._read_headers(), params=params)
        self._raise_friendly(resp)
        return resp.json()

    async def post(self, path: str, data: dict[str, Any] | None = None) -> dict:
        await self._ensure_token()
        resp = await self._http.post(path, headers=self._write_headers(), json=data)
        self._raise_friendly(resp)
        return resp.json()

    async def put(self, path: str, data: dict[str, Any] | None = None) -> dict:
        await self._ensure_token()
        resp = await self._http.put(path, headers=self._write_headers(), json=data)
        self._raise_friendly(resp)
        return resp.json()

    async def delete(self, path: str) -> dict | str:
        await self._ensure_token()
        resp = await self._http.delete(path, headers=self._read_headers())
        self._raise_friendly(resp)
        try:
            return resp.json()
        except (ValueError, json.JSONDecodeError):
            return f"Deleted successfully (HTTP {resp.status_code})"
