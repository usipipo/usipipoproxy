# Telegram Bot Migration Design (Phase 1)

**Date:** 2026-03-23
**Goal:** Migrate basic commands (/start, /help, /menu) to a lightweight Telegram Bot client.
**Approach:** Decouple bot logic from monorepo. The bot acts as a stateless client communicating with the backend API via HTTP.

## Architecture
- **Bot Core:** `python-telegram-bot` (as in monorepo).
- **Communication:** HTTP API client for backend communication.
- **Storage:** Stateless (bot state is offloaded to backend API).

## Components
- `src/bot/handlers/`: Handlers for basic commands.
- `src/bot/keyboards/`: UI for bot commands.
- `src/infrastructure/api_client.py`: HTTP client.
- `src/main.py`: Entry point, application config.

## Testing
- Unit tests for API client.
- Unit tests for command handlers.

## Next Steps
- Implement `api_client.py`.
- Migrate `/start` command.
