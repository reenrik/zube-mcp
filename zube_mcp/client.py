"""HTTP client for the Zube.io API with automatic token management."""

from __future__ import annotations

import time
from typing import Any

import httpx

from .auth import create_refresh_jwt

BASE_URL = "https://zube.io/api"


class ZubeClient:
    def __init__(self, client_id: str, private_key: str):
        self._client_id = client_id
        self._private_key = private_key
        self._access_token: str | None = None
        self._token_expires_at: float = 0
        self._http = httpx.AsyncClient(base_url=BASE_URL, timeout=30)

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

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "X-Client-ID": self._client_id,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get(self, path: str, params: Any = None) -> dict:
        await self._ensure_token()
        resp = await self._http.get(path, headers=self._headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    async def post(self, path: str, data: dict[str, Any] | None = None) -> dict:
        await self._ensure_token()
        resp = await self._http.post(path, headers=self._headers(), json=data)
        resp.raise_for_status()
        return resp.json()

    async def put(self, path: str, data: dict[str, Any] | None = None) -> dict:
        await self._ensure_token()
        resp = await self._http.put(path, headers=self._headers(), json=data)
        resp.raise_for_status()
        return resp.json()

    async def delete(self, path: str) -> dict | str:
        await self._ensure_token()
        resp = await self._http.delete(path, headers=self._headers())
        resp.raise_for_status()
        try:
            return resp.json()
        except Exception:
            return f"Deleted successfully (HTTP {resp.status_code})"
