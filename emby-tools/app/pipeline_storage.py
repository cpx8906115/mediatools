from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .pipeline_models import PipelineTask, PipelineTaskLog, TaskStatus, TaskType


def _now():
    return datetime.now(timezone.utc)


async def task_create(
    session: AsyncSession,
    *,
    type: TaskType,
    title: str,
    payload: dict,
) -> PipelineTask:
    t = PipelineTask(
        created_at=_now(),
        updated_at=_now(),
        type=type,
        status=TaskStatus.queued,
        title=title or "",
        payload_json=json.dumps(payload or {}, ensure_ascii=False),
    )
    session.add(t)
    await session.flush()
    await task_log(session, task_id=t.id, level="info", message="任务已创建")
    await session.commit()
    return t


async def task_log(session: AsyncSession, *, task_id: int, level: str, message: str) -> None:
    lg = PipelineTaskLog(task_id=task_id, created_at=_now(), level=level, message=message)
    session.add(lg)
    await session.flush()


async def task_get(session: AsyncSession, task_id: int) -> PipelineTask | None:
    return (await session.execute(select(PipelineTask).where(PipelineTask.id == task_id))).scalar_one_or_none()


async def task_logs(session: AsyncSession, task_id: int, limit: int = 200) -> list[PipelineTaskLog]:
    rows = (
        await session.execute(
            select(PipelineTaskLog)
            .where(PipelineTaskLog.task_id == task_id)
            .order_by(PipelineTaskLog.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(reversed(rows))


async def task_list(session: AsyncSession, limit: int = 50) -> list[PipelineTask]:
    rows = (await session.execute(select(PipelineTask).order_by(PipelineTask.created_at.desc()).limit(limit))).scalars().all()
    return list(rows)


async def task_set_status(session: AsyncSession, *, task_id: int, status: TaskStatus, msg: str | None = None) -> None:
    t = await task_get(session, task_id)
    if not t:
        return
    t.status = status
    t.updated_at = _now()
    if msg:
        await task_log(session, task_id=task_id, level="info" if status == TaskStatus.success else "error", message=msg)
    await session.commit()
