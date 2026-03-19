from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .pipeline_models import TaskType
from .pipeline_storage import task_create, task_list, task_get, task_logs

router_pipeline = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router_pipeline.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request, session: AsyncSession = Depends(get_session)):
    tasks = await task_list(session, limit=80)
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks})


@router_pipeline.get("/tasks/{task_id}", response_class=HTMLResponse)
async def task_detail_page(task_id: int, request: Request, session: AsyncSession = Depends(get_session)):
    t = await task_get(session, task_id)
    if not t:
        return templates.TemplateResponse(
            "tasks_detail.html",
            {"request": request, "task": None, "logs": [], "payload": "{}"},
        )
    logs = await task_logs(session, task_id, limit=300)
    payload = t.payload_json
    try:
        payload = json.dumps(json.loads(payload), ensure_ascii=False, indent=2)
    except Exception:
        pass
    return templates.TemplateResponse(
        "tasks_detail.html",
        {"request": request, "task": t, "logs": logs, "payload": payload},
    )


@router_pipeline.post("/tasks/new")
async def task_new(
    kind: str = Form(...),
    title: str = Form(""),
    payload_json: str = Form("{}"),
    session: AsyncSession = Depends(get_session),
):
    try:
        payload = json.loads(payload_json or "{}")
        if not isinstance(payload, dict):
            payload = {"value": payload}
    except Exception:
        payload = {"raw": payload_json}

    ttype = TaskType.tg_message
    if kind in TaskType.__members__:
        ttype = TaskType[kind]

    t = await task_create(session, type=ttype, title=title or ttype.value, payload=payload)
    return RedirectResponse(url=f"/tasks/{t.id}", status_code=303)
