from __future__ import annotations

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # mediatools version
    app_version: str = os.environ.get("APP_VERSION", "0.5.3.19")

    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    database_url: str = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://emby:emby_change_me@db:5432/emby_inspector",
    )

    app_password: str = os.environ.get("APP_PASSWORD", "change_me")
    app_base_url: str = os.environ.get("APP_BASE_URL", "http://localhost:8787")

    tg_bot_token: str | None = os.environ.get("TG_BOT_TOKEN") or None
    tg_chat_id: str | None = os.environ.get("TG_CHAT_ID") or None
    webhook_url: str | None = os.environ.get("WEBHOOK_URL") or None

    log_level: str = os.environ.get("LOG_LEVEL", "INFO")

    # session
    session_secret: str = os.environ.get("SESSION_SECRET", "dev-secret-change-me")


settings = Settings()
