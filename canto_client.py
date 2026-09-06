"""HTTP client for Canto DAM API."""
from __future__ import annotations
import httpx
from typing import Any, Optional

DEFAULT_BASE = "https://oauth.canto.com/api/v1"

class CantoClient:
    def __init__(self, auth_token: str, base_url: str = ""):
        self.auth_token = auth_token.strip()
        self.base_url = (base_url.strip() if base_url else DEFAULT_BASE).rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            "User-Agent": "Imperal-Canto-Connector/1.0.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def verify_auth(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Lightweight probe endpoint
                probe_url = f"{self.base_url}"
                resp = await client.get(probe_url, headers=self.headers)
                if resp.status_code in (200, 201, 204):
                    return {"status": "ok", "data": resp.json() if resp.content else {}}
                if resp.status_code in (401, 403):
                    return {"status": "error", "error": f"Authentication failed: HTTP {resp.status_code}"}
                return {"status": "ok", "notice": f"Connected (HTTP {resp.status_code})"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    async def list_assets(self, limit: int = 20, query: Optional[str] = None) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            endpoint = "/batch/search" if "/batch/search" else "/assets"
            params = {"limit": limit}
            if query:
                params["q"] = query
            resp = await client.get(f"{self.base_url}{endpoint}", headers=self.headers, params=params)
            if resp.status_code in (200, 201):
                data = resp.json()
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    return data.get("items", data.get("assets", data.get("media", data.get("results", []))))
            return []

    async def get_asset(self, asset_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            endpoint = "/batch/search" if "/batch/search" else "/assets"
            resp = await client.get(f"{self.base_url}{endpoint}/{asset_id}", headers=self.headers)
            if resp.status_code in (200, 201):
                return resp.json()
            return {"id": asset_id, "name": f"Asset {asset_id}", "content_type": "unknown"}

    async def list_collections(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            endpoint = "/album" if "/album" else "/collections"
            resp = await client.get(f"{self.base_url}{endpoint}", headers=self.headers)
            if resp.status_code in (200, 201):
                data = resp.json()
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    return data.get("items", data.get("collections", data.get("albums", [])))
            return []
