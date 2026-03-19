# mediatools

工具集名称：**mediatools**。

个人自用的媒体自动化工具集合（Monorepo）。

## 项目

- `emby-tools/`：基于 FastAPI + PostgreSQL 的 Web 控制台，用于 Emby 统计（最近播放/历史、库增长）、任务中心、以及流水线入队（支持 Telegram/Webhook 通知）。
- `telegram-talk-bot/`：Telegram 双向沟通机器人，可将消息按规则转发到 `emby-tools` 的入队接口。

## 安全与配置

- **不要提交密钥/Token/Cookie**：请使用 `.env` 文件或将敏感信息挂载到 `/secrets`（只读）。
- `emby-tools`：复制 `emby-tools/.env.example` 为 `.env`。
- `telegram-talk-bot`：复制 `telegram-talk-bot/.env.example` 为 `.env`。

## 运行（Docker Compose）

分别进入子目录运行：

```bash
cd emby-tools
docker compose up -d --build

cd ../telegram-talk-bot
docker compose up -d --build
```

> 如需 Telegram 消息入队到 emby-tools：请在 bot 的 `.env` 中设置 `PIPELINE_INGEST_URL`，并建议同时设置 `PIPELINE_INGEST_SECRET`。
