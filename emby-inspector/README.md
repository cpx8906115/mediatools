# Emby Inspector (MVP)

FastAPI + Jinja2 + Tailwind UI for Emby analytics:
- Recent plays
- Library growth (daily snapshots)
- Settings page (update Emby base URL + API key without redeploy)
- Notifications: Telegram + Webhook

## Dev
- `docker compose up -d --build`
- App: http://localhost:8787

## Config
Copy `.env.example` to `.env` and fill:
- `APP_PASSWORD`
- `TG_BOT_TOKEN`, `TG_CHAT_ID` (optional)
- `WEBHOOK_URL` (optional)

Then set Emby base URL + key in the web UI Settings page.
