# usipipo-telegram-bot

> Bot de Telegram para interacción con usuarios del ecosistema uSipipo

## Estado

- [ ] En desarrollo
- [ ] Alpha
- [ ] Beta
- [x] Producción

## Versión

**v0.3.0** - User Profile "Mis Datos" Feature

**v0.2.0** - VPN Key Management (En desarrollo)

**v0.1.0** - Invisible Authentication (Estable)

## Características

- 🔐 **Autenticación Invisible**: Auto-registro vía Telegram
- 👤 **Perfil de Usuario**: Ver información detallada del usuario, balance, referidos y lealtad
- 🔑 **Gestión de Claves VPN**: Crear, ver, renombrar y eliminar claves WireGuard/Outline
- 💰 **Sistema de Pagos**: Crypto (USDT-BSC) y Telegram Stars
- 📊 **Programa de Referidos**: Código único y estadísticas
- ⭐ **Programa de Lealtad**: Bonus por compras recurrentes
- 🎯 **Paquetes de Datos**: Compra de GB adicionales
- 🔄 **Suscripciones**: Planes mensuales renovables
- 💬 **Soporte Técnico**: Integración con bot de soporte

## Documentación

- [CHANGELOG](CHANGELOG.md)
- [Integration Tests](INTEGRATION-TEST-SUMMARY.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Commands](docs/COMMANDS.md)
- [Deployment](docs/DEPLOYMENT.md)

## Desarrollo

```bash
# Clonar
git clone https://github.com/uSipipo-Team/usipipo-telegram-bot.git
cd usipipo-telegram-bot

# Instalar dependencias
uv sync --dev

# Configurar entorno
cp example.env .env

# Ejecutar tests
uv run pytest

# Ejecutar bot
uv run python -m src
```

## Docker

```bash
# Build
docker build -t usipipo-telegram-bot .

# Ejecutar
docker run --env-file .env usipipo-telegram-bot
```

## License

MIT © uSipipo
