from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession

from .pipeline_models import PipelineTask, TaskStatus, TaskType
from .pipeline_storage import task_create, task_log, task_set_status


async def run_transfer(session: AsyncSession, task: PipelineTask, payload: dict) -> None:
    """Transfer worker.

    Current stage: no real transfer yet.
    - If media block is missing, try "scrape" (tmdb match) from tg text + link.
    - Then create organize + strm tasks.
    """

    media = payload.get("media") if isinstance(payload, dict) else None
    provider = payload.get("provider") if isinstance(payload, dict) else None
    text = payload.get("text") if isinstance(payload, dict) else ""
    source = payload.get("source") if isinstance(payload, dict) else None

    await task_log(session, task_id=task.id, level="info", message=f"transfer: provider={provider}（暂不做真实转存）")

    if not isinstance(media, dict) or not media.get("title"):
        # scrape: use tmdb to fill minimal metadata
        try:
            from .pipeline_scrape import guess_from_text, tmdb_match_tv, tmdb_category

            g = guess_from_text(text or "")
            if g:
                await task_log(session, task_id=task.id, level="info", message=f"scrape: 识别到链接 provider={g.provider}, query={g.query}, year={g.year}, S={g.season}, E={g.episode}, q={g.quality}")
                details = await tmdb_match_tv(g.query, year=g.year)
                if details:
                    title = details.get("name") or details.get("original_name") or g.query
                    first_air = (details.get("first_air_date") or "")
                    year = first_air.split("-")[0] if first_air else (str(g.year) if g.year else "")
                    cat = tmdb_category(details)
                    media = {
                        "tmdb_id": int(details.get("id")),
                        "media_type": "series",
                        "title": title,
                        "year": year,
                        "season": g.season or 1,
                        "episode": g.episode or 0,
                        "quality": g.quality or "",
                        "category": cat,
                    }
                    payload["media"] = media
                    payload["category"] = cat
                    await task_log(session, task_id=task.id, level="info", message=f"scrape: TMDB 匹配成功 id={media['tmdb_id']} 标题={title} 年份={year} 分类={cat}")
                else:
                    await task_log(session, task_id=task.id, level="error", message="scrape: TMDB 未匹配到结果（请补充标题/年份或直接给 TMDB ID）")
            else:
                await task_log(session, task_id=task.id, level="info", message="scrape: 未识别到可用线索（请补充标题/分类/SxxEyy 或 TMDB ID）")
        except Exception as e:
            await task_log(session, task_id=task.id, level="error", message=f"scrape: 异常 {type(e).__name__}: {e}")

    # Create organize/strm if we have enough media info now
    if isinstance(media, dict) and media.get("title"):
        src_url = ""
        if isinstance(source, dict):
            src_url = source.get("url") or ""
        org_payload = {"media": media, "category": payload.get("category") or media.get("category"), "source": {"task_id": task.id, "url": src_url}, "text": text}
        await task_create(session, type=TaskType.organize, title=f"整理 {media.get('title')} {media.get('year') or ''}".strip(), payload=org_payload)

        strm_payload = {"media": media, "category": payload.get("category") or media.get("category"), "source": {"task_id": task.id, "url": src_url}, "text": text}
        await task_create(session, type=TaskType.strm, title=f"生成STRM {media.get('title')}".strip(), payload=strm_payload)

        await task_create(session, type=TaskType.emby_refresh, title="刷新Emby（占位）", payload={"source": {"task_id": task.id}})
        await task_log(session, task_id=task.id, level="info", message="transfer: 已创建 organize/strm/emby_refresh 子任务")

    await task_set_status(session, task_id=task.id, status=TaskStatus.success, msg="transfer: 处理完成")


async def run_organize(session: AsyncSession, task: PipelineTask, payload: dict) -> None:
    """Path planning based on parsed media block.

    Rules (user decision):
      - library root: /影视
      - keep category as subdir: /影视/<分类>/
      - series dir: /影视/<分类>/<标题> (<年份>)/Season 01/
    """
    media = payload.get("media") if isinstance(payload, dict) else None
    category = payload.get("category") if isinstance(payload, dict) else None

    if not isinstance(media, dict):
        await task_log(session, task_id=task.id, level="error", message="organize: 缺少 media 块，无法规划路径")
        await task_set_status(session, task_id=task.id, status=TaskStatus.failed, msg="organize: payload 不完整")
        return

    title = (media.get("title") or media.get("name") or "未命名").strip()
    year = str(media.get("year") or "").strip()
    quality = (media.get("quality") or "").strip()
    season = int(media.get("season") or 1)
    episode = int(media.get("episode") or 0)

    if not category:
        category = (media.get("category") or "未分类").strip()
    if not category:
        category = "未分类"

    episode_code = f"S{season:02d}E{episode:02d}" if episode else f"S{season:02d}"
    basename = f"{title} - {episode_code}" + (f" - {quality}" if quality else "")

    # Plan (target path on your storage)
    library_root = "/影视"
    safe_year = f" ({year})" if year and year.isdigit() else (f" ({year})" if year else "")
    series_dir = f"{library_root}/{category}/{title}{safe_year}/Season {season:02d}"
    target_strm_path = f"{series_dir}/{basename}.strm"

    plan = {
        "library_root": library_root,
        "category": category,
        "title": title,
        "year": year,
        "season": season,
        "episode": episode,
        "episode_code": episode_code,
        "quality": quality,
        "basename": basename,
        "series_dir": series_dir,
        "target_strm_path": target_strm_path,
    }

    payload["plan"] = plan
    await task_log(session, task_id=task.id, level="info", message="organize: 已生成路径规划")
    await task_log(session, task_id=task.id, level="info", message=f"目标STRM路径: {target_strm_path}")
    await task_log(session, task_id=task.id, level="info", message=f"规划详情: {plan}")

    await task_set_status(session, task_id=task.id, status=TaskStatus.success, msg="organize: 路径规划完成")


async def run_strm(session: AsyncSession, task: PipelineTask, payload: dict) -> None:
    import os

    plan = payload.get("plan") if isinstance(payload, dict) else None
    if not isinstance(plan, dict):
        # fallback: compute plan here if organize hasn't run yet
        media = payload.get("media") if isinstance(payload, dict) else None
        category = payload.get("category") if isinstance(payload, dict) else None
        if not isinstance(media, dict) or not media.get("title"):
            await task_log(session, task_id=task.id, level="error", message="strm: 缺少 plan 且 media 不完整")
            await task_set_status(session, task_id=task.id, status=TaskStatus.failed, msg="strm: plan/media 缺失")
            return

        title = (media.get("title") or "未命名").strip()
        year = str(media.get("year") or "").strip()
        quality = (media.get("quality") or "").strip()
        season = int(media.get("season") or 1)
        episode = int(media.get("episode") or 0)
        if not category:
            category = (media.get("category") or "未分类").strip() or "未分类"

        episode_code = f"S{season:02d}E{episode:02d}" if episode else f"S{season:02d}"
        basename = f"{title} - {episode_code}" + (f" - {quality}" if quality else "")
        library_root = "/影视"
        safe_year = f" ({year})" if year and year.isdigit() else (f" ({year})" if year else "")
        series_dir = f"{library_root}/{category}/{title}{safe_year}/Season {season:02d}"
        target_strm_path = f"{series_dir}/{basename}.strm"
        plan = {"target_strm_path": target_strm_path, "basename": basename, "category": category}
        payload["plan"] = plan
        await task_log(session, task_id=task.id, level="info", message=f"strm: 未找到 plan，已自动生成目标路径: {target_strm_path}")

    # For safety we write to workspace output, not to /影视 directly.
    out_root = os.environ.get("STRM_OUT_ROOT", "/app/strm-out")
    target_strm_path = plan.get("target_strm_path") or ""

    # Map target path into out_root mirror
    rel = target_strm_path.lstrip("/")
    real_path = os.path.join(out_root, rel)
    os.makedirs(os.path.dirname(real_path), exist_ok=True)

    # Content: keep as original source url if present
    source_url = ""
    source = payload.get("source") if isinstance(payload, dict) else None
    if isinstance(source, dict):
        source_url = source.get("url") or ""
    if not source_url:
        source_url = payload.get("url") or payload.get("share_url") or ""

    content = source_url or "# TODO: replace with direct link / 302 url\n"

    with open(real_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

    await task_log(session, task_id=task.id, level="info", message="strm: 已生成 STRM 文件（写入到容器输出目录镜像）")
    await task_log(session, task_id=task.id, level="info", message=f"生成位置: {real_path}")
    await task_log(session, task_id=task.id, level="info", message=f"目标映射路径(供后续真实落盘): {target_strm_path}")

    await task_set_status(session, task_id=task.id, status=TaskStatus.success, msg="strm: 生成完成")


async def run_emby_refresh(session: AsyncSession, task: PipelineTask, payload: dict) -> None:
    await task_log(session, task_id=task.id, level="info", message="emby_refresh 占位：后续会调用 Emby Library Refresh")
    await task_set_status(session, task_id=task.id, status=TaskStatus.success, msg="emby_refresh 占位执行完成")


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
