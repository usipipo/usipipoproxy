# uSipipo Backend Documentation

## 📚 Documentation Index

### Payment Systems

- **[TronDealer API Documentation](trondealer-api.md)** - Complete API reference for TronDealer crypto payment gateway
- **[TronDealer Tutorial](TRONDEALER_TUTORIAL.md)** - Step-by-step guide for integrating USDT/USDC payments
- **Telegram Stars** - Telegram payment integration (see webhook docs)

### API Reference

- **[API Documentation](../src/infrastructure/api/v1/)** - Source code with inline documentation
- **[OpenAPI Spec](/docs)** - Available at `/docs` endpoint when running the server
- **[Webhooks](../src/infrastructure/api/v1/webhooks/)** - Webhook implementation details

### Architecture

- **[Database Schema](database_schema.md)** - PostgreSQL database structure
- **[Authentication](authentication.md)** - JWT and multi-client auth guide
- **[Error Codes](error_codes.md)** - HTTP error reference

### Deployment

- **[Configuration](configuration.md)** - Environment variables and settings
- **[Deployment Guide](deployment.md)** - Production deployment instructions
- **[Monitoring](monitoring.md)** - Logging and observability

---

## 🔗 Related Repositories

- **[usipipo-commons](https://github.com/uSipipo-Team/usipipo)** - Shared library with domain entities
- **[usipipo-landing](https://github.com/uSipipo-Team/usipipo-landing)** - Landing page
- **[usipipo-telegram-bot](https://github.com/uSipipo-Team/usipipo)** - Telegram bot
- **[usipipo-miniapp-web](https://github.com/uSipipo-Team/usipipo-miniapp-web)** - Mini App frontend

---

## 📖 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/uSipipo-Team/usipipo.git
   cd apps/backend
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run the server**
   ```bash
   uvicorn src.main:app --reload --port 8001
   ```

5. **Access documentation**
   - Swagger UI: http://localhost:8001/docs
   - ReDoc: http://localhost:8001/redoc

---

## 🆘 Support

- **GitHub Issues:** https://github.com/uSipipo-Team/usipipo/issues
- **Documentation:** https://github.com/uSipipo-Team/usipipo/wiki
- **Email:** support@usipipo.com

---

**Last Updated:** 2026-03-23
**Version:** v0.9.0
