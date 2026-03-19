from __future__ import annotations

import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .pipeline_auth import get_ingest_secret, is_allowed_chat
from .pipeline_models import TaskType
from .pipeline_storage import task_create

router_ingest = APIRouter()


def _match_rule(text: str, rule: str) -> bool:
    if not rule:
        return True
    text_l = (text or "").lower()
    rule_l = rule.lower()
    if rule_l.startswith("contains:"):
        return rule_l[len("contains:") :] in text_l
    if rule_l.startswith("prefix:"):
        return text_l.startswith(rule_l[len("prefix:") :])
    if rule_l.startswith("hasurl"):
        return "http://" in text_l or "https://" in text_l
    # default: substring
    return rule_l in text_l


@router_ingest.post("/api/ingest/tg")
async def ingest_tg(request: Request, session: AsyncSession = Depends(get_session)):
    """Generic Telegram ingest endpoint.

    Expected payload: {"text": "...", "chat_id": <int>, "from_id": <int>, ...}

    Filtering:
      - ENV PIPELINE_INGEST_RULES: semicolon separated rules.
        examples:
          "hasurl"; "prefix:/add"; "contains:115"; "contains:123"
      - If rules exist, message must match at least one rule.
    """
    try:
        body = await request.json()
    except Exception:
        body = {"raw": (await request.body()).decode("utf-8", errors="ignore")}

    # Auth (optional): shared secret via header
    secret = get_ingest_secret()
    if secret:
        got = request.headers.get("X-Ingest-Secret") or request.headers.get("x-ingest-secret")
        if got != secret:
            return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)

    # Allowlist (optional)
    chat_id = None
    if isinstance(body, dict):
        try:
            chat_id = int(body.get("chat_id")) if body.get("chat_id") is not None else None
        except Exception:
            chat_id = None
    if not is_allowed_chat(chat_id):
        return JSONResponse({"ok": True, "skipped": True, "reason": "chat_not_allowed"})

    text = ""
    if isinstance(body, dict):
        text = body.get("text") or body.get("message") or ""

    rules_raw = os.environ.get("PIPELINE_INGEST_RULES", "").strip()
    if rules_raw:
        rules = [r.strip() for r in rules_raw.split(";") if r.strip()]
        if rules:
            ok = any(_match_rule(text, r) for r in rules)
            if not ok:
                return JSONResponse({"ok": True, "skipped": True, "reason": "rule_mismatch"})

    title = (text.strip().splitlines()[0][:80] if text else "TG消息")
    t = await task_create(session, type=TaskType.tg_message, title=title, payload=body if isinstance(body, dict) else {"value": body})
    return JSONResponse({"ok": True, "task_id": t.id})
