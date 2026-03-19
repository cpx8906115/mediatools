# mediatools

> 工具集名称：**mediatools**

Monorepo for personal media automation tools.

- 中文说明：see [README.zh-CN.md](README.zh-CN.md)

## Projects

- `emby-tools/` — FastAPI + PostgreSQL web console for Emby stats + task center + pipeline ingest.
- `telegram-talk-bot/` — Telegram bot used as an entry point; forwards messages into `emby-tools` ingest endpoint.

## Notes

Secrets are not committed. Use `.env` files and/or bind-mounted `/secrets`.
