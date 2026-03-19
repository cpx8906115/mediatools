from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession

from .pipeline_models import PipelineTask, TaskStatus, TaskType
from .pipeline_storage import task_create, task_log, task_set_status


async def run_transfer(session: AsyncSession, task: PipelineTask, payload: dict) -> None:
    """Placeholder transfer worker.

    For now: mark success and fan-out next steps if media metadata is present.
    """
    media = payload.get("media") if isinstance(payload, dict) else None
    provider = payload.get("provider") if isinstance(payload, dict) else None

    await task_log(session, task.id, "info", f"transfer 占位执行器：provider={provider}（未做真实转存）")

    # Fan-out: create organize/strm/emby_refresh tasks (skeleton)
    if isinstance(media, dict) and media.get("tmdb_id"):
        org_payload = {"tmdb_id": media.get("tmdb_id"), "media": media, "source": {"task_id": task.id}}
        await task_create(session, type=TaskType.organize, title=f"整理 TMDB {media.get('tmdb_id')}", payload=org_payload)

        strm_payload = {"media": media, "source": {"task_id": task.id}}
        await task_create(session, type=TaskType.strm, title=f"生成STRM {media.get('title') or ''}".strip(), payload=strm_payload)

        refresh_payload = {"source": {"task_id": task.id}}
        await task_create(session, type=TaskType.emby_refresh, title="刷新Emby（占位）", payload=refresh_payload)

        await task_log(session, task.id, "info", "已创建 organize/strm/emby_refresh 子任务（骨架）")

    await task_set_status(session, task.id, TaskStatus.success, "transfer 占位执行完成")


async def run_organize(session: AsyncSession, task: PipelineTask, payload: dict) -> None:
    tmdb_id = payload.get("tmdb_id") if isinstance(payload, dict) else None
    await task_log(session, task.id, "info", f"organize 占位：tmdb_id={tmdb_id}")
    await task_set_status(session, task.id, TaskStatus.success, "organize 占位执行完成")


async def run_strm(session: AsyncSession, task: PipelineTask, payload: dict) -> None:
    media = payload.get("media") if isinstance(payload, dict) else None
    await task_log(session, task.id, "info", f"strm 占位：media={media or {}}")
    await task_set_status(session, task.id, TaskStatus.success, "strm 占位执行完成")


async def run_emby_refresh(session: AsyncSession, task: PipelineTask, payload: dict) -> None:
    await task_log(session, task.id, "info", "emby_refresh 占位：后续会调用 Emby Library Refresh")
    await task_set_status(session, task.id, TaskStatus.success, "emby_refresh 占位执行完成")


async def dispatch(session: AsyncSession, task: PipelineTask) -> bool:
    """Return True if handled."""
    try:
        payload = json.loads(task.payload_json or "{}")
    except Exception:
        payload = {}

    if task.type == TaskType.transfer:
        await run_transfer(session, task, payload)
        return True
    if task.type == TaskType.organize:
        await run_organize(session, task, payload)
        return True
    if task.type == TaskType.strm:
        await run_strm(session, task, payload)
        return True
    if task.type == TaskType.emby_refresh:
        await run_emby_refresh(session, task, payload)
        return True

    return False
