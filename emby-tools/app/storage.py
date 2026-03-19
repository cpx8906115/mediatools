from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from .db import engine
from .models import Base, KVSetting


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def kv_get(session, key: str) -> str | None:
    row = (await session.execute(select(KVSetting).where(KVSetting.key == key))).scalar_one_or_none()
    return row.value if row else None


async def kv_set(session, key: str, value: str) -> None:
    now = datetime.now(timezone.utc)
    row = (await session.execute(select(KVSetting).where(KVSetting.key == key))).scalar_one_or_none()
    if row:
        row.value = value
        row.updated_at = now
    else:
        session.add(KVSetting(key=key, value=value, updated_at=now))
    await session.commit()
