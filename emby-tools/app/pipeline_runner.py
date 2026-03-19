from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .pipeline_models import PipelineTask, TaskStatus, TaskType
from .pipeline_storage import task_create, task_log, task_set_status
from .pipeline_parser import extract_urls, classify_link, parse_media_block
from .pipeline_workers import dispatch


def _now():
    return datetime.now(timezone.utc)


async def process_one(session: AsyncSession, task: PipelineTask) -> None:
    if task.status != TaskStatus.queued:
        return

    # mark running
    task.status = TaskStatus.running
    task.updated_at = _now()
    await task_log(session, task_id=task.id, level="info", message="开始处理")
    await session.commit()

    try:
        payload = {}
        try:
            payload = json.loads(task.payload_json or "{}")
        except Exception:
            payload = {"raw": task.payload_json}

        if task.type == TaskType.tg_message:
            text = ""
            if isinstance(payload, dict):
                text = payload.get("text") or payload.get("message") or ""

            meta = parse_media_block(text)
            urls = extract_urls(text)
            await task_log(session, task_id=task.id, level="info", message=f"提取到 {len(urls)} 个链接")

            created = 0
            created_keys: set[str] = set()
            for u in urls:
                hit = classify_link(u)
                if not hit:
                    continue
                provider, info = hit

                # de-dup: provider + share_id/url
                key = f"{provider}:{info.get('share_id') or info.get('url')}"
                if key in created_keys:
                    continue
                created_keys.add(key)

                child_payload = {
                    "provider": provider,
                    **info,
                    "source": {
                        "task_id": task.id,
                        "chat_id": payload.get("chat_id"),
                        "from_id": payload.get("from_id"),
                        "message_id": payload.get("message_id"),
                    },
                    "media": meta,
                    "raw_text": text,
                }
                title = f"转存({provider}) {meta.get('title') or ''}".strip()
                await task_create(session, type=TaskType.transfer, title=title, payload=child_payload)
                created += 1

            if created == 0:
                await task_set_status(session, task_id=task.id, status=TaskStatus.success, msg="未识别到 123/115 链接（已跳过）")
            else:
                await task_set_status(session, task_id=task.id, status=TaskStatus.success, msg=f"已创建 {created} 个转存任务")
            return

        handled = await dispatch(session, task)
        if handled:
            return

        # other types not implemented yet
        await task_set_status(session, task_id=task.id, status=TaskStatus.success, msg="该任务类型暂未实现执行器（已占位）")

    except Exception as e:
        await task_set_status(session, task_id=task.id, status=TaskStatus.failed, msg=f"{type(e).__name__}: {e}")


async def process_queue(session: AsyncSession, limit: int = 20) -> int:
    rows = (
        await session.execute(
            select(PipelineTask)
            .where(PipelineTask.status == TaskStatus.queued)
            .order_by(PipelineTask.created_at.asc())
            .limit(limit)
        )
    ).scalars().all()

    n = 0
    for t in rows:
        await process_one(session, t)
        n += 1
    return n
