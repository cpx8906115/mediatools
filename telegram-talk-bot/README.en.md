<div align="center">

# Telegram Communication Bot

**Lightweight, efficient, and ready-to-deploy bidirectional message relay bot for Telegram**

User messages are automatically forwarded to an admin group; admins reply directly in forum topics — seamless two-way communication with zero friction.

[![Go Version](https://img.shields.io/badge/Go-1.23-00ADD8?style=flat-square&logo=go)](https://go.dev/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=flat-square)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker)](docker-compose.yml)

[**English**](README.en.md) | [中文](README.md)

</div>

---

## Features

- **Bidirectional Forwarding** — Messages sent to the bot are relayed to the admin group; admin replies are pushed back to the user
- **Forum Topic Isolation** — Each user gets a dedicated Forum Topic, keeping conversations organized
- **Rich Media Support** — Text, photos, videos, documents, voice, stickers, locations, contacts, and media groups
- **CAPTCHA Verification** — New users must solve a math CAPTCHA before chatting, effectively blocking automated spam
- **Rate Limiting** — Configurable message cooldown to prevent spam
- **Admin Toolkit** — Broadcast / statistics / conversation cleanup / topic reset, all via commands
- **Ban System** — Permanent bans with optional "delete topic = ban" policy
- **Auto Recovery** — If a topic is accidentally deleted, a new one is created on the user's next message
- **Dual Mode** — Supports both Polling and Webhook, adapting to any deployment scenario
- **Lightweight** — Single binary + SQLite, one-command Docker deployment, no external dependencies

## Architecture

<div align="center">
<img src="architecture.png" alt="System Architecture" width="85%">
</div>

## Quick Start

### Prerequisites

| Step | Action | Purpose |
|------|--------|---------|
| 1 | Create a bot via [@BotFather](https://t.me/botfather) | Obtain `BOT_TOKEN` |
| 2 | Create a Supergroup with Topics enabled | Add the bot as an admin |
| 3 | Get the group ID (negative number) | Use [@userinfobot](https://t.me/userinfobot) |
| 4 | Get your admin user ID | Same as above |

### Deploy with Docker Compose (Recommended)

```bash
git clone https://github.com/PiPiLuLuDoggy/telegram-talk-bot.git
cd telegram-talk-bot

cp .env.example .env
```

Edit `.env` with the required values:

```bash
BOT_TOKEN=your_bot_token
ADMIN_GROUP_ID=-1001234567890
ADMIN_USER_IDS=123456789
```

Start the bot:

```bash
docker compose up -d
```

### Build from Source

```bash
# Build
make build

# Run
make run
```

> Polling mode is used by default. Set `WEBHOOK_URL` to enable Webhook mode.

## Usage

### For Users

1. Search for your bot on Telegram and send `/start`
2. If CAPTCHA is enabled, solve the math challenge by tapping the correct answer button
3. Once verified, send any message — it will be forwarded to the admin team
4. Admin replies will be delivered back through the bot

### For Admins

1. View incoming user messages in the admin group — one forum topic per user
2. New topics automatically display user info (username, ID)
3. Reply within the topic — your message is forwarded to the user

## Admin Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/start` | Check bot status | `/start` |
| `/stats` | View user & conversation statistics | `/stats` |
| `/broadcast` | Broadcast a message to all users | Reply to a message, then send `/broadcast` |
| `/clear <id>` | Clear a user's conversation | `/clear 123456789` |
| `/reset <id>` | Reset a user's topic (fix deleted topic issues) | `/reset 123456789` |

## Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `BOT_TOKEN` | Telegram Bot Token | — | ✅ |
| `ADMIN_GROUP_ID` | Admin group ID (negative) | — | ✅ |
| `ADMIN_USER_IDS` | Comma-separated admin user IDs | — | ✅ |
| `APP_NAME` | Application name | `TelegramCommunicationBot` | |
| `WELCOME_MESSAGE` | Welcome message on `/start` | Default Chinese text | |
| `CAPTCHA_ENABLED` | Enable CAPTCHA verification for new users | `false` | |
| `MESSAGE_INTERVAL` | Min interval between user messages (sec) | `5` | |
| `DELETE_TOPIC_AS_FOREVER_BAN` | Permanently ban user on topic deletion | `false` | |
| `DELETE_USER_MESSAGE_ON_CLEAR_CMD` | Delete messages on `/clear` | `false` | |
| `DATABASE_PATH` | SQLite database path | `./data/bot.db` | |
| `PORT` | Webhook listen port | `8090` | |
| `WEBHOOK_URL` | Webhook URL (empty = Polling mode) | — | |
| `DEBUG` | Debug mode | `false` | |

## Project Structure

```
telegram-talk-bot/
├── cmd/bot/main.go           # Entrypoint
├── internal/
│   ├── bot/bot.go            # Bot core (Polling / Webhook)
│   ├── config/config.go      # Configuration loading & validation
│   ├── handlers/
│   │   ├── handlers.go       # Message routing & dispatch
│   │   └── admin.go          # Admin command handlers
│   ├── services/
│   │   ├── message.go        # Message forwarding / mapping / media groups
│   │   ├── forum.go          # Forum topic management
│   │   ├── captcha.go        # CAPTCHA verification
│   │   └── ratelimiter.go    # Rate limiting
│   ├── database/database.go  # Database operations (GORM + SQLite)
│   └── models/models.go      # Data model definitions
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── .env.example
```

## FAQ

<details>
<summary><b>Bot not responding?</b></summary>

Verify your `BOT_TOKEN` and check the container logs:

```bash
docker compose logs -f telegram-bot
```
</details>

<details>
<summary><b>Cannot create forum topics?</b></summary>

Make sure:
1. The group has the "Topics" feature enabled (Group Settings → Topics)
2. The bot has admin permissions in the group
3. `ADMIN_GROUP_ID` is correct and negative
</details>

<details>
<summary><b>Accidentally deleted a user's topic?</b></summary>

The user's next message will automatically create a new topic. You can also manually run:

```
/reset <user_id>
```
</details>

<details>
<summary><b>How to back up data?</b></summary>

```bash
docker cp telegram-talk-bot:/app/data/bot.db ./backup.db
```
</details>

<details>
<summary><b>How to update to the latest version?</b></summary>

```bash
docker compose down
git pull
docker compose up -d --build
```
</details>

## License

This project is licensed under the [Apache License 2.0](LICENSE).
