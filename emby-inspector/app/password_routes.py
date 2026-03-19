from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .storage import kv_get, kv_set

router_password = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router_password.get("/password", response_class=HTMLResponse)
async def password_page(request: Request):
    msg = request.query_params.get("msg")
    err = request.query_params.get("err")
    return templates.TemplateResponse(
        "password.html",
        {"request": request, "msg": msg, "err": err},
    )


@router_password.post("/password")
async def password_save(
    request: Request,
    current: str = Form(...),
    new: str = Form(...),
    confirm: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    stored = await kv_get(session, "app_password")
    stored = stored or ""

    if not secrets.compare_digest(current, stored):
        return RedirectResponse(url="/password?err=1&msg=当前密码不正确", status_code=303)
    if len(new) < 6:
        return RedirectResponse(url="/password?err=1&msg=新密码至少6位", status_code=303)
    if new != confirm:
        return RedirectResponse(url="/password?err=1&msg=两次输入的新密码不一致", status_code=303)

    await kv_set(session, "app_password", new)
    # keep session, no forced logout
    return RedirectResponse(url="/password?msg=已保存", status_code=303)
