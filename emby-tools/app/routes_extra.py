from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .emby_client import EmbyConfig, get_recent_plays, get_playback_history
from .models import LibrarySnapshot
from .storage import kv_get

router_extra = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router_extra.get("/recent", response_class=HTMLResponse)
async def recent_page(request: Request, session: AsyncSession = Depends(get_session)):
    base_url = await kv_get(session, "emby_base_url")
    api_key = await kv_get(session, "emby_api_key")
    items = []
    err = None
    if base_url and api_key:
        try:
            cfg = EmbyConfig(base_url=base_url, api_key=api_key)
            # 1) playback history (if supported)
            try:
                items.extend(await get_playback_history(cfg, limit=50))
            except Exception:
                pass
            # 2) current sessions
            items.extend(await get_recent_plays(cfg, limit=30))
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
    return templates.TemplateResponse(
        "recent.html",
        {"request": request, "items": items, "err": err, "emby_api_base": (base_url.rstrip('/') if base_url else None)},
    )


@router_extra.get("/growth", response_class=HTMLResponse)
async def growth_page(request: Request, session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(select(LibrarySnapshot).order_by(LibrarySnapshot.day.desc()).limit(30))).scalars().all()
    rows = list(reversed(rows))
    msg = request.query_params.get("msg")
    err = request.query_params.get("err")
    return templates.TemplateResponse(
        "growth.html",
        {"request": request, "rows": rows, "msg": msg, "err": err},
    )


@router_extra.post("/growth/snapshot")
async def growth_snapshot(session: AsyncSession = Depends(get_session)):
    # lazy import to avoid circulars
    from .jobs import run_snapshot

    try:
        msg = await run_snapshot()
        return RedirectResponse(url="/growth?msg=" + msg, status_code=303)
    except Exception as e:
        return RedirectResponse(url="/growth?err=1&msg=" + f"{type(e).__name__}: {e}", status_code=303)
