# mediatools

Monorepo for personal media automation tools.

## Projects

- `emby-inspector/` — FastAPI + PostgreSQL web console for Emby stats + task center + pipeline ingest.
- `telegram-communication-bot/` — Telegram bot used as an entry point; forwards messages into `emby-inspector` ingest endpoint.

## Notes

Secrets are not committed. Use `.env` files and/or bind-mounted `/secrets`.
