# Architecture

## Overview

Bot de Telegram para interacción con usuarios del ecosistema uSipipo.

## Tech Stack

- **Framework:** python-telegram-bot v21+
- **Package Manager:** uv
- **Shared Library:** usipipo-commons

## Project Structure

```
src/
├── __init__.py
├── __main__.py
├── main.py          # Bot handlers
├── config/          # Configuration
├── handlers/        # Command handlers
├── keyboards/       # Inline/reply keyboards
└── utils/           # Utilities
```

## Dependencies

- `usipipo-commons`: Entidades y schemas compartidos
- `python-telegram-bot`: Telegram Bot API
- `pydantic-settings`: Configuración
