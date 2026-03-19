from __future__ import annotations

import os
from dataclasses import dataclass

import httpx


@dataclass
class QuarkConfig:
    cookie: str


def make_client(cfg: QuarkConfig) -> httpx.AsyncClient:
    headers = {
        "Cookie": cfg.cookie,
        "User-Agent": os.environ.get(
            "QUARK_UA",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
        ),
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://pan.quark.cn",
        "Referer": "https://pan.quark.cn/",
    }
    return httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0), headers=headers, follow_redirects=True)


async def test_cookie(cfg: QuarkConfig) -> tuple[bool, str]:
    """Best-effort cookie validity test."""
    try:
        async with make_client(cfg) as client:
            # This endpoint may change; we just need a 200/401 signal.
            r = await client.get("https://pan.quark.cn/drive/api/v1/user/info")
            if r.status_code == 200:
                js = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
                name = (js.get("data") or {}).get("nickname") or "ok"
                return True, f"cookie ok: {name}"
            # include final url when redirected
            return False, f"cookie invalid: {r.status_code} final={str(r.url)}"
    except Exception as e:
        return False, f"cookie test error: {type(e).__name__}: {e}"


async def ensure_folder(cfg: QuarkConfig, dest_path: str) -> tuple[bool, str, str | None]:
    """Create folder path (best-effort). Returns (ok, msg, folder_id)."""
    # Placeholder: will implement once we lock Quark folder APIs.
    return False, "folder api not implemented yet", None


async def save_share_to(cfg: QuarkConfig, share_id: str, dest_path: str, pwd: str | None = None) -> tuple[bool, str]:
    """Placeholder for share save. Implement after confirming API contract."""
    return False, "quark transfer not implemented yet"
