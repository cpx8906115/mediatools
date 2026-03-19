from __future__ import annotations

import os
from typing import Any

import httpx


TMDB_BASE = "https://api.themoviedb.org/3"


class TMDBClient:
    def __init__(self, api_key: str | None = None, language: str = "zh-CN"):
        self.api_key = api_key or os.environ.get("TMDB_API_KEY")
        self.language = language

    def _params(self, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        p: dict[str, Any] = {"language": self.language}
        if self.api_key:
            p["api_key"] = self.api_key
        if extra:
            p.update(extra)
        return p

    async def search_tv(self, query: str, year: int | None = None) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            params = self._params({"query": query})
            if year:
                params["first_air_date_year"] = year
            r = await client.get(f"{TMDB_BASE}/search/tv", params=params)
            r.raise_for_status()
            return r.json()

    async def tv_details(self, tmdb_id: int) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{TMDB_BASE}/tv/{tmdb_id}", params=self._params())
            r.raise_for_status()
            return r.json()

    async def genres_tv(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{TMDB_BASE}/genre/tv/list", params=self._params())
            r.raise_for_status()
            return r.json()
