from __future__ import annotations

from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import AsyncSessionLocal
from .emby_client import EmbyConfig, get_library_total_count
from .storage import kv_get
from .models import LibrarySnapshot
from .pipeline_runner import process_queue


async def run_snapshot() -> str:
    async with AsyncSessionLocal() as session:
        base_url = await kv_get(session, "emby_base_url")
        api_key = await kv_get(session, "emby_api_key")
        if not base_url or not api_key:
            return "skip: emby not configured"

        total = await get_library_total_count(EmbyConfig(base_url=base_url, api_key=api_key))
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        prev = (await session.execute(
            select(LibrarySnapshot).order_by(LibrarySnapshot.day.desc()).limit(1)
        )).scalars().first()
        prev_total = prev.total_items if prev else 0
        delta = total - prev_total

        existing = (await session.execute(select(LibrarySnapshot).where(LibrarySnapshot.day == day))).scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if existing:
            existing.total_items = total
            existing.delta_items = delta
            existing.updated_at = now
        else:
            session.add(LibrarySnapshot(day=day, total_items=total, delta_items=delta, updated_at=now))
        await session.commit()
        return f"ok: day={day} total={total} delta={delta}"


async def run_pipeline_tick() -> None:
    async with AsyncSessionLocal() as session:
        await process_queue(session, limit=10)


def start_scheduler() -> AsyncIOScheduler:
    sched = AsyncIOScheduler(timezone="UTC")
    # daily at 00:10 UTC (08:10 Asia/Shanghai)
    sched.add_job(run_snapshot, CronTrigger(hour=0, minute=10), id="daily_snapshot", replace_existing=True)
    # pipeline tick
    sched.add_job(run_pipeline_tick, "interval", seconds=10, id="pipeline_tick", replace_existing=True)
    sched.start()
    return sched
