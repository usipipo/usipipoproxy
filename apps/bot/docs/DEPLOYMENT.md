# Deployment

## Local Development

```bash
# Clonar repositorio
git clone https://github.com/uSipipo-Team/usipipo-telegram-bot.git
cd usipipo-telegram-bot

# Instalar dependencias
uv sync --dev

# Configurar entorno
cp example.env .env
# Editar .env con el token del bot

# Ejecutar
uv run python -m src
```

## Docker

```bash
# Build
docker build -t usipipo-telegram-bot .

# Ejecutar
docker run --env-file .env usipipo-telegram-bot
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram | Required |
| `APP_ENV` | Environment (development/production) | development |
| `DEBUG` | Enable debug mode | false |
| `LOG_LEVEL` | Logging level | INFO |
| `BACKEND_API_URL` | Backend API URL | http://localhost:8000/api/v1 |

## Production Deployment

TBD
