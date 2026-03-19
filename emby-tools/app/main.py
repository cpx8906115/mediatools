from __future__ import annotations

import secrets
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .settings import settings
from .storage import init_db
from .routes import router
from .jobs import start_scheduler

# ensure initial password is stored in DB for web-based password changes
from .db import AsyncSessionLocal
from .storage import kv_get, kv_set

app = FastAPI(title="mediatools")
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)

templates = Jinja2Templates(directory="app/templates")


def require_login(request: Request) -> None:
    if request.session.get("authed") is True:
        return
    raise HTTPException(status_code=401, detail="Not logged in")


@app.on_event("startup")
async def _startup() -> None:
    await init_db()
    # bootstrap credentials into DB if not set
    async with AsyncSessionLocal() as s:
        if not (await kv_get(s, "app_username")):
            await kv_set(s, "app_username", "admin")
        if not (await kv_get(s, "app_password")):
            await kv_set(s, "app_password", settings.app_password)
    start_scheduler()


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # credentials are stored in DB (kv_settings)
    async with AsyncSessionLocal() as s:
        stored_user = await kv_get(s, "app_username")
        stored_pass = await kv_get(s, "app_password")

    stored_user = stored_user or "admin"
    stored_pass = stored_pass or settings.app_password

    ok_user = secrets.compare_digest((username or "").strip(), stored_user)
    ok_pass = secrets.compare_digest(password, stored_pass)

    if ok_user and ok_pass:
        request.session["authed"] = True
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/login?bad=1", status_code=303)


@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


app.include_router(router, dependencies=[Depends(require_login)])

from .routes_extra import router_extra
app.include_router(router_extra, dependencies=[Depends(require_login)])

# Pipeline task center
from .pipeline_routes import router_pipeline
app.include_router(router_pipeline, dependencies=[Depends(require_login)])

# Ingest endpoints (no login; protected by optional shared secret later)
from .pipeline_ingest_routes import router_ingest
app.include_router(router_ingest)

# Password management routes live on main app (authed)
from .password_routes import router_password
app.include_router(router_password, dependencies=[Depends(require_login)])
