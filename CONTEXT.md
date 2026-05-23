# uSipipo Proxy — CONTEXTO DEL PROYECTO

> **§1–§13** están documentados en los commits anteriores. Este archivo continúa en §14.

---

## 14. USUARIOS BETA

Hardcodeados en `cmd/backend/main.go`:

| Nombre  | Telegram ID |
|---------|-------------|
| mowgli  | `891835105` |
| ersu    | `634873279` |

Se cargan con `--seed`. El `WG_ENDPOINT_HOST` se leería de la env en despliegue real.

## 15. VPS PRODUCCIÓN — INFRAESTRUCTURA EXISTENTE

| Servicio         | Puerto   | Tecnología         |
|------------------|----------|--------------------|
| Caddy            | 80/443   | HTTPS + proxy      |
| TASALO API 1     | 8001     | Flask (localhost:5040)| ⚠️ Backend uSipipo NO usa el 8001 externo |
| TASALO API 2     | 8000     | Flask              |
| TASALO API 3     | 8040     | FastAPI             |
| Freqtrade 1      | 8081     | Python              |
| Freqtrade 2      | 8082     | Python              |
| Blocky DNS       | 4000     | DNS proxy           |
| DuckDNS cron     | */5 min  | Actualiza IP dinámica|
| ──────────────────────────────────────── |
| **uSipipo backend** | 9001  | Go (nuevo, via Caddyfile) |
| **uSipipo frontend** | verificado por Caddy | |

**Regla TASALO atendida**: el backend escucha en `API_PORT=8001` (Docker), pero Caddy rutea a `localhost:9001`. El frontend Vue/React se sirve por `usipipo.dpdns.org` y llama a `http://localhost:8001` (Docker) o `http://localhost:9001` (producción) mediante `VITE_API_BASE_URL`.

## 16. RESTRICCIONES Y CONVENCIONES

1. **No wgctrl**: causalmente eliminado de `go.mod` por broken checksum + CGO/Alpine con Go 1.24.
2. **No `// TODO`**: removidos en Go; committed.
3. **No `// MVP` / `// fake` / `// FAKE`**: prohibidos, revisar antes de cada commit.
4. **WireGuard endpoint es la IP pública AlphaVPS**: `165.140.241.96:64000` — hardcoded en `main.go` si `WG_ENDPOINT_HOST` vacío.
5. **Backend es la fuente de toda verdad**: identities, dispositivos, tráfico — WireGuard solo ejecuta.
6. **Todo bajo `/proxy`**: Caddyfile debe insertar `reverse_proxy /proxy/* localhost:9001` antes de cualquier catch-all.
7. **Frontend de producción se compila y sirve por Caddy**, no por Docker local.
8. **Lenguaje de commits y comentarios**: se prefiere inglés cuando el código es en inglés; la documentación puede estar en español según preferencia.

---

## 17. BUGS CONOCIDOS Y DEUDA TÉCNICA (última actualización: 2026-05-22T20:51)

### ✅ Resueltos (verificados 2026-05-22)

| # | Bug | Fix |
|---|---|---|
| 1 | `h.wgManager` nil en `bot/handler.go` | `WebhookHandler` struct recibe `wgManager *wg.Manager`; inyectado en `main.go` línea 71 |
| 3 | `ensureDir()` no crea directorios | Reemplazado por `os.MkdirAll(p, 0o755)` en `store.go` línea 40 |
| 5 | Endpoints de pago TronDealer V2 no implementados | Completamente implementados: invoice create, list, webhook HMAC-SHA256, async `PaymentWorker`, `processNotified`/`processSwept`/`processExpired` |
| 6 | `models.Device` `BytesRx`/`BytesTx`; `wg.ClientConfig` vs `models.ClientConfig` duplicado | Resuelto por **refactor arquitectónico 2026-05-22** (ver §17-A abajo) |
| 9 | `baseUrl()` hardcoded en `bot/handler.go` | Función `baseUrl()` removida (dead code); `h.baseURL` inyectado por `NewWebhookHandler` y usado en todas las respuestas |

### 🔄 En progreso / Abiertos

| # | Archivo | Problema | Estado |
|---|---|---|---|
| 7 | `handlers.go` (**904 l**) | Excede límite 300 líneas AGENTS.md §3 — necesita split en `devices.go`/`payments.go`/`auth.go` | **P1** pendiente |
| 8 | `store.go` (**380 l**) | Excede límite 300 líneas AGENTS.md §3 | **P1** pendiente |
| 9-a | Bot Telegram | `SendMessage` no implementado — bot NO envía replies a chats de Telegram, solo loguea internamente | **P0** pendiente |
| 10 | `cmd/exporter/` | Directorio no existe; `docker/wg-exporter.Dockerfile` no puede build | **P2** pendiente crear o reducir scope |
| 11 | `scripts/vet.sh` | Go 1.24 no instalado en host; `go vet` solo vía Docker | **P3** pendiente automatizar |
| 12 | `genUUIDv4()` | Usa `math/rand` inseguro; debería usar `crypto/rand` o `github.com/google/uuid` | **P2** pendiente refactor |

---

## 17-A. Refactor arquitectónico 2026-05-22 — Separación de responsabilidades en modelos

### Problema original

`models.Device` tenía 3 responsabilidades fusionadas:
1. **Entidad de BD** — campos que mapean a tabla `devices`
2. **DTO de API** — serializado directamente por JSON cuando un handler lo devuelve
3. **Portador de `Conf`** — incluía `ClientConfig` con la clave privada, mezclando secreto criptográfico con entidad BD

`models.ClientConfig` y `wg.ClientConfig` eran tipos duplicados que divergían silenciosamente.

### Cambios realizados

**`pkg/models/models.go`:**
- `Device.Conf` eliminado — `Device` es ahora entidad de BD pura
- `ClientConfig` eliminado — solo existe en `internal/wg/manager.go`
- `DeviceResponse` agregado — DTO seguro para `GET /proxy/devices` (sin clave privada, sin `Conf`)
- `CreateDeviceResponse` agregado — DTO para `POST /proxy/devices` (incluye `wg.ClientConfig` una sola vez)

**`internal/wg/manager.go`:**
- `ClientConfig.PrivateKey` → `privateKey` (unexported)
- `PrivateKey()` getter explícito — acceso controlado
- `NewClientConfig()` único constructor público

**`internal/http/handlers/handlers.go`:**
- `deviceResponseFrom()` — único punto de construcción de `DeviceResponse` (DRY)
- `List()` construye `[]DeviceResponse` explícitamente, no serializa `Device` en crudo
- `Create()` usa `wg.NewClientConfig()` + `deviceResponseFrom()`, devuelve `CreateDeviceResponse`
- `DeviceStore` declarada una sola vez (duplicado pre-refactor eliminado)

### Política de claves privadas

La clave privada existe en el objeto `ClientConfig` **exactamente una vez** en memoria: durante la construcción en `POST /proxy/devices`. Se serializa en la respuesta JSON y desaparece. No hay endpoint `GET /proxy/devices/{id}/conf`.

---
