# SESSION_SUMMARY.md

> **READ FIRST** — Every new session must start by reading this file, then `TRACKING_LOG.md` and `LESSONS.md` in order.

_Last updated: 2026-05-22T21:44_

---

## 1. What is this project

uSipipo Proxy is a WireGuard VPN service (backend Go + frontend React) that lets people in Cuba and Latin America securely reach international SaaS and dev platforms. Backend is the single source of truth for identities, WireGuard devices, traffic, and subscription state (invoice → confirmed → days credited).

---

## 2. Current state by subsystem *(verified 2026-05-22T21:44, build+vet+gofmt clean)*

| Subsystem | Status | Notes |
|---|---|---|
| **DB** | ✅ Ready | SQLite, auto-migrations in `internal/db/store.go`, `users`/`devices`/`traffic_samples`/`invoices`/`webhook_events` tables. `private_key` column added to `devices`. |
| **Auth** | ✅ Ready + Cookie | Telegram HMAC-SHA256 → JWT HS256 30-day expiry; `POST /proxy/auth/telegram`; `POST /proxy/auth/cookie` sets `HttpOnly; Secure; SameSite=Strict` session cookie |
| **Auth Middleware** | ✅ Implemented | `middleware.AuthMiddleware` reads JWT from `Authorization: Bearer` header OR `session` cookie |
| **WireGuard** | ✅ Ready | Uses `wg` binary exclusively; `sync.Mutex` protected; `internal/wg/manager.go`, 244 lines |
| **Devices API** | ✅ Ready + /conf | CRUD + traffic + `.conf` download under `/proxy/devices/*`; JWT required; `DeviceResponse` for list; endpoint `GET /proxy/devices/{id}/conf` return `text/plain` attachment |
| **Telegram Bot** | ✅ Operativo | Commands `/start /status /connect /help`; inline keyboards; `callback_query` support; `SendMessage` via Telegram Bot API with `parse_mode MarkdownV2`; `/connect` creates device + button "📄 Descargar .conf" |
| **Payments (TronDealer V2)** | ✅ Ready | Invoice creation, webhook validation (HMAC-SHA256), async worker, `confirmed` → extends subscription |
| **Architecture** | ✅ Refactored | `Device` = pure BD entity; `DeviceResponse`/`CreateDeviceResponse` = API DTOs; `ClientConfig` only in `wg` package unexported; `deviceResponseFrom()` single DRY builder |
| **wg-exporter / Prometheus** | ❌ Not started | `cmd/exporter/` does not exist; Dockerfile points to non-existent path |
| **Frontend (React)** | ❌ Not started | All `frontend/src/*` empty dirs |
| **Android VPN app** | ❌ Not started | WireGuard `.conf` file download pending frontend |
| **CI/CD (GHCR)** | ⚠️ Partial | `scripts/build.sh` works; GitHub Actions workflow not yet configured |
| **Local `go vet`** | ⚠️ Docker only | Go 1.24 not installed on host; all build/vet verified in `golang:1.24-alpine` |

---

## 3. Key architectural decisions

| Decision | Location / Date |
|---|---|
| WireGuard via `wg` binary, not `wgctrl` | `internal/wg/manager.go`, 2026-05-19 |
| SQLite for DB | `internal/db/store.go` |
| Telegram Login → HMAC-SHA256 → JWT HS256 | `internal/http/handlers/handlers.go` |
| All API under `/proxy/*` prefix | `cmd/backend/main.go` |
| TronDealer: invoice → wallet/assign → webhook HMAC → confirmed | `handlers.go` |
| `ensureDir()` fixed: `os.MkdirAll(p, 0o755)` | `internal/db/store.go:40` |
| `wgManager` injected into bot `WebhookHandler` | `cmd/backend/main.go` |
| `Device` SRP: entidad BD sin campos de transporte | `pkg/models/models.go`, 2026-05-22 |
| `ClientConfig` solo en `internal/wg` (unexported `privateKey`) | `internal/wg/manager.go`, 2026-05-22 |
| `DeviceResponse` / `CreateDeviceResponse` — DTOs de API exclusivos | `pkg/models/models.go`, 2026-05-22 |
| `deviceResponseFrom()` — único punto de construcción de DTO | `internal/http/handlers/handlers.go`, 2026-05-22 |
| Bot inline keyboards desde su implementación inicial | `internal/bot/handler.go`, 2026-05-22 |
| Cookie de sesión HttpOnly para autenticación en navegador | `internal/http/middleware/auth.go`, 2026-05-22 |
| `GET /proxy/devices/{id}/conf` — descarga .conf por navegador | `internal/http/handlers/handlers.go`, 2026-05-22 |
| `AuthMiddleware` — lee JWT de header o cookie | `internal/http/middleware/auth.go`, 2026-05-22 |

---

## 4. Model update history (this session)

| Date | Change |
|---|---|
| 2026-05-22T21:44 | `bot.Store.CreateDevice` signature updated: `privKey` param added |
| 2026-05-22T21:44 | `devices` table + `CreateDevice`/`ListDevices`/`GetDeviceByID` now store `private_key` |
| 2026-05-22T21:44 | `GET /proxy/devices/{id}/conf` — ServeConf handler (Content-Disposition + wg.ClientConfig) |
| 2026-05-22T21:44 | Router: `strings.HasSuffix` → `path.Base()` para evitar colisiones |
| 2026-05-22T21:44 | `internal/bot/handler.go` full rewrite: cmdXXXX service layer, InlineKeyboardMarkup, SendMessage, answerCallback, callback_query support |
| 2026-05-22T21:44 | `internal/http/middleware/auth.go` — nuevo paquete: AuthMiddleware, tokenFromRequest (header+cookie), SetSessionCookie |
| 2026-05-22T21:44 | `handlers.go` userFromCtx ahora delega a `middleware.UserFromCtx` (una sola fuente de verdad) |
| 2026-05-22T21:44 | `cmd/backend/main.go`: rutas protegidas envueltas en `middleware.AuthMiddleware`; nuevo endpoint `POST /proxy/auth/cookie` |

---

## 5. Open issues — ranked by priority

| Priority | Issue | Details |
|---|---|---|
| **P1** | `handlers.go` **~960 líneas** (límite 300 AGENTS.md §3) | Split en `handlers/auth.go` + `handlers/devices.go` + `handlers/payments.go` + `handlers/health.go` |
| **P1** | `store.go` **380 líneas** (límite 300 AGENTS.md §3) | Split en `store/store.go` + `store/migrations.go` |
| **P2** | `genUUIDv4()` usa `math/rand` | LL-008; debería usar `crypto/rand` o `github.com/google/uuid` |
| **P2** | `cmd/exporter/` missing | `docker/wg-exporter.Dockerfile` apunta a ruta inexistente |
| **P3** | `go vet` no local Go 1.24 | CI-only; riesgo de cambios sin verificar localmente |
| **P3** | Frontend completamente vacío | React app — modo incógnito, QR WireGuard, dashboard, pagos |

---

## 6. How to resume

1. Leer `docs/LESSONS.md` para patrones aprendidos (LL-016 a LL-020 últimos)
2. Leer `docs/ROADMAP.md` para el plan de creación completo
3. Continuar en orden: **Fase 1-A (split handlers.go/store.go)** → **Fase 1-B (UUID refactor)** → **Fase 3 (App Web React)** → **Fase 1-C (CI/CD)** → **Fase 4 (Android)** → **Fase 5 (exporter)**
