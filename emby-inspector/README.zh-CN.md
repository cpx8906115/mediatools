# Emby Inspector（MVP）

基于 FastAPI + Jinja2 + Tailwind 的 Emby 统计与任务控制台：

- 最近播放 / 历史
- 库增长（按天快照）
- 设置页（无需重部署即可修改 Emby Base URL / API Key）
- 通知：Telegram + Webhook
- 任务中心：TG 入队 + 流水线任务（transfer/organize/strm/emby_refresh）

## 启动（开发/自用）

```bash
docker compose up -d --build
```

- Web：<http://localhost:8787>

## 配置

复制 `.env.example` 为 `.env` 并填写：

- `APP_PASSWORD`（登录密码）
- `TG_BOT_TOKEN`, `TG_CHAT_ID`（可选：Telegram 通知）
- `WEBHOOK_URL`（可选：Webhook 通知）

启动后在 WebUI 的「设置」页面填写：
- Emby Base URL
- Emby API Key

## 安全建议（TG 入队）

如果你启用了 `/api/ingest/tg`：

- 建议设置 `PIPELINE_INGEST_SECRET` 并要求上游通过 `X-Ingest-Secret` 传入
- 可选设置 `PIPELINE_INGEST_ALLOWED_CHATS`（逗号分隔 chat_id 白名单）
