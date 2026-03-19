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
    # keep route for compatibility; auth UI moved into /settings
    return RedirectResponse(url="/settings#auth", status_code=303)


@router_password.post("/password/username")
async def username_save(
    request: Request,
    new_username: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    nu = (new_username or "").strip()
    if len(nu) < 3:
        return RedirectResponse(url="/password?err=1&msg=新账号至少3位", status_code=303)

    await kv_set(session, "app_username", nu)
    return RedirectResponse(url="/password?msg=账号已保存", status_code=303)


@router_password.post("/password/password")
async def password_save(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    stored_pass = (await kv_get(session, "app_password")) or ""

    if not secrets.compare_digest(current_password, stored_pass):
        return RedirectResponse(url="/password?err=1&msg=当前密码不正确", status_code=303)

    if len(new_password) < 6:
        return RedirectResponse(url="/password?err=1&msg=新密码至少6位", status_code=303)
    if new_password != confirm_password:
        return RedirectResponse(url="/password?err=1&msg=两次输入的新密码不一致", status_code=303)

    await kv_set(session, "app_password", new_password)
    return RedirectResponse(url="/password?msg=密码已保存", status_code=303)
