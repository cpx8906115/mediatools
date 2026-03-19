from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .emby_client import EmbyConfig, test_connection, get_library_counts, get_latest_items
from .storage import kv_get, kv_set

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, session: AsyncSession = Depends(get_session)):
    base_url = await kv_get(session, "emby_base_url")
    api_key = await kv_get(session, "emby_api_key")

    counts = None
    latest = []
    err = None
    if base_url and api_key:
        try:
            cfg = EmbyConfig(base_url=base_url, api_key=api_key)
            counts = await get_library_counts(cfg)
            latest = await get_latest_items(cfg, limit=18)
        except Exception as e:
            err = f"{type(e).__name__}: {e}"

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "emby_url": base_url,
            "counts": counts,
            "latest": latest,
            "err": err,
            "emby_api_base": (base_url.rstrip('/') if base_url else None),
        },
    )


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, session: AsyncSession = Depends(get_session)):
    emby_url = await kv_get(session, "emby_base_url") or ""
    emby_key = await kv_get(session, "emby_api_key") or ""
    masked = ""
    if emby_key:
        masked = (emby_key[:4] + "…" + emby_key[-4:]) if len(emby_key) >= 8 else "****"

    app_user = await kv_get(session, "app_username") or "admin"

    test_msg = request.query_params.get("test")
    err = request.query_params.get("err")

    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "emby_url": emby_url,
            "emby_key_masked": masked,
            "app_username": app_user,
            "updated": request.query_params.get("updated") == "1",
            "test_msg": test_msg,
            "err": err,
        },
    )


@router.post("/settings")
async def settings_save(
    emby_base_url: str = Form(...),
    emby_api_key: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    emby_base_url = emby_base_url.strip()
    emby_api_key = emby_api_key.strip()

    ok, msg = await test_connection(EmbyConfig(base_url=emby_base_url, api_key=emby_api_key))
    if not ok:
        return RedirectResponse(url="/settings?err=1&test=" + msg, status_code=303)

    await kv_set(session, "emby_base_url", emby_base_url)
    await kv_set(session, "emby_api_key", emby_api_key)
    await kv_set(session, "settings_updated_at", datetime.now(timezone.utc).isoformat())
    return RedirectResponse(url="/settings?updated=1&test=" + msg, status_code=303)
