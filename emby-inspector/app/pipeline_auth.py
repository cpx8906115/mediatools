from __future__ import annotations

import os


def get_ingest_secret() -> str | None:
    return os.environ.get("PIPELINE_INGEST_SECRET")


def is_allowed_chat(chat_id: int | None) -> bool:
    allowed = os.environ.get("PIPELINE_INGEST_ALLOWED_CHATS", "").strip()
    if not allowed:
        return True  # default allow when unset
    if chat_id is None:
        return False
    allow_set = set([x.strip() for x in allowed.split(",") if x.strip()])
    return str(chat_id) in allow_set
