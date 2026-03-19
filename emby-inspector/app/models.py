from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class KVSetting(Base):
    __tablename__ = "kv_settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LibrarySnapshot(Base):
    __tablename__ = "library_snapshots"
    __table_args__ = (UniqueConstraint("day", name="uq_library_snapshots_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    total_items: Mapped[int] = mapped_column(Integer, nullable=False)
    created_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delta_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
