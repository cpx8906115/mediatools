from __future__ import annotations

import os
from dataclasses import dataclass

import httpx


@dataclass
class EmbyConfig:
    base_url: str
    api_key: str


def _connect_timeout() -> float:
    try:
        return float(os.environ.get("EMBY_CONNECT_TIMEOUT_SEC", "10"))
    except Exception:
        return 10.0


def make_client(cfg: EmbyConfig) -> httpx.AsyncClient:
    base = cfg.base_url.rstrip("/")
    headers = {
        "X-Emby-Token": cfg.api_key,
        "Accept": "application/json",
    }
    return httpx.AsyncClient(
        base_url=base,
        headers=headers,
        timeout=httpx.Timeout(30.0, connect=_connect_timeout()),
    )


async def test_connection(cfg: EmbyConfig) -> tuple[bool, str]:
    try:
        async with make_client(cfg) as client:
            r = await client.get("/System/Info")
            r.raise_for_status()
            js = r.json()
            name = js.get("ServerName") or "Emby"
            ver = js.get("Version") or "?"
            return True, f"OK: {name} v{ver}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {e}"


async def get_library_counts(cfg: EmbyConfig) -> dict:
    async with make_client(cfg) as client:
        r = await client.get("/Items/Counts")
        r.raise_for_status()
        js = r.json() or {}
        return js if isinstance(js, dict) else {}


async def get_library_total_count(cfg: EmbyConfig) -> int:
    js = await get_library_counts(cfg)
    keys = [
        "MovieCount",
        "SeriesCount",
        "EpisodeCount",
        "MusicVideoCount",
        "TrailerCount",
        "BookCount",
    ]
    total = 0
    for k in keys:
        v = js.get(k)
        if isinstance(v, int):
            total += v
    return total


async def get_recent_plays(cfg: EmbyConfig, limit: int = 20) -> list[dict]:
    """Current active playback sessions (MVP)."""
    async with make_client(cfg) as client:
        r = await client.get("/Sessions")
        r.raise_for_status()
        sessions = r.json() if isinstance(r.json(), list) else []

    items: list[dict] = []
    for s in sessions:
        now_playing = s.get("NowPlayingItem")
        if not now_playing:
            continue
        user = (s.get("UserName") or s.get("User", {}).get("Name") or "")
        client_name = s.get("Client") or ""
        device = s.get("DeviceName") or ""
        play_state = s.get("PlayState") or {}
        position_ticks = play_state.get("PositionTicks")

        items.append(
            {
                "kind": "session",
                "user": user,
                "title": now_playing.get("Name") or "",
                "type": now_playing.get("Type") or "",
                "id": now_playing.get("Id"),
                "series": (now_playing.get("SeriesName") or "") if now_playing.get("Type") == "Episode" else "",
                "season": now_playing.get("ParentIndexNumber"),
                "episode": now_playing.get("IndexNumber"),
                "client": client_name,
                "device": device,
                "position_ticks": position_ticks,
                "is_paused": bool(play_state.get("IsPaused")),
                "is_transcoding": bool(s.get("TranscodingInfo")),
            }
        )

    return items[:limit]


async def get_playback_history(cfg: EmbyConfig, limit: int = 50) -> list[dict]:
    """Playback history via Playback/Recent (requires Emby to have this endpoint enabled)."""
    params = {"Limit": str(limit)}
    async with make_client(cfg) as client:
        r = await client.get("/Playback/Recent", params=params)
        r.raise_for_status()
        js = r.json() or {}

    items = js.get("Items") if isinstance(js, dict) else None
    items = items if isinstance(items, list) else []

    out: list[dict] = []
    for it in items:
        out.append(
            {
                "kind": "history",
                "id": it.get("Id"),
                "title": it.get("Name") or "",
                "type": it.get("Type") or "",
                "series": it.get("SeriesName") or "",
                "season": it.get("ParentIndexNumber"),
                "episode": it.get("IndexNumber"),
                "played_at": it.get("DatePlayed"),
            }
        )
    return out


async def get_latest_items(cfg: EmbyConfig, limit: int = 12) -> list[dict]:
    """Latest added items for a poster wall (Movies + Series only)."""
    params = {
        "Limit": str(limit),
        "Recursive": "true",
        "SortBy": "DateCreated",
        "SortOrder": "Descending",
        "Fields": "DateCreated,PrimaryImageAspectRatio,Overview,ProductionYear",
        "IncludeItemTypes": "Movie,Series",
    }
    async with make_client(cfg) as client:
        r = await client.get("/Items", params=params)
        r.raise_for_status()
        js = r.json() or {}

    raw = js.get("Items") if isinstance(js, dict) else None
    items = raw if isinstance(raw, list) else []

    out: list[dict] = []
    for it in items:
        t = it.get("Type") or ""
        out.append(
            {
                "id": it.get("Id"),
                "name": it.get("Name") or "",
                "type": t,
                "type_cn": "电影" if t == "Movie" else ("剧集" if t == "Series" else t),
                "year": it.get("ProductionYear"),
            }
        )
    return out
