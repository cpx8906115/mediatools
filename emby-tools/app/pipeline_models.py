from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class TaskStatus(str, Enum):
    queued = "queued"
    running = "running"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"


class TaskType(str, Enum):
    tg_message = "tg_message"
    transfer = "transfer"
    organize = "organize"
    strm = "strm"
    emby_refresh = "emby_refresh"
    notify = "notify"


class PipelineTask(Base):
    __tablename__ = "pipeline_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    type: Mapped[TaskType] = mapped_column(SAEnum(TaskType), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(SAEnum(TaskStatus), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


Index("ix_pipeline_tasks_status_created", PipelineTask.status, PipelineTask.created_at)


class PipelineTaskLog(Base):
    __tablename__ = "pipeline_task_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    level: Mapped[str] = mapped_column(String(16), nullable=False, default="info")
    message: Mapped[str] = mapped_column(Text, nullable=False, default="")


Index("ix_pipeline_task_logs_task_id_created", PipelineTaskLog.task_id, PipelineTaskLog.created_at)
