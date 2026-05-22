# AGENTS.md — uSipipo Proxy

> Este archivo define las reglas y guías específicas para cualquier agente (IA o humano) que trabaje en el repositorio `usipipo/usipipoproxy`.

---

## 1. Propósito del proyecto

uSipipo Proxy es un servicio VPN WireGuard que permite a personas y empresas en Cuba y Latinoamérica acceder de forma segura a herramientas SaaS y plataformas de desarrollo internacionales. El backend Go gestiona identidades, dispositivos WireGuard y tráfico. El frontend React es una SPA servida por Caddy.

---

## 2. Stack tecnológico (no negociable)

| Capa         | Tecnología                                                                                           |
|--------------|------------------------------------------------------------------------------------------------------|
| Backend      | Go 1.24 · `net/http` (estándar) · `mattn/go-sqlite3` · `golang-jwt/jwt v5`                          |
| VPN          | WireGuard vía binario `wg` (NO wgctrl — ver §6)                                                      |
| DB           | SQLite 3 — auto-migraciones en `internal/db/store.go`                                                |
| Auth         | Telegram Login Web App — HMAC-SHA256 → JWT HS256                                                     |
| Bot          | Telegram Bot API — webhook `POST /bot/telegram`                                                      |
| Frontend     | Vite + React 19 + TypeScript + Tailwind CSS v4                                                       |
| Infra        | Docker Compose (imágenes locales, sin Docker Hub) · Caddy reverse proxy · AlphaVPS Belgium (€4.50/mes) |
| CI/CD        | GitHub Actions → GHCR (pendiente)                                                                    |

### Dependencias Go exactas (go.mod)

```go
module github.com/usipipo/usipipoproxy
go 1.24

require (
    github.com/golang-jwt/jwt/v5 v5.2.1
    github.com/mattn/go-sqlite3 v1.14.27
)
```

**No agregar dependencias externas sin justificación explícita.**

---

## 3. Convenciones de código

### Go

- Todo el código Go vive bajo `internal/` o `pkg/`. No exponer paquetes internos.
- **Nunca** usar `// TODO`, `// MVP`, `// fake`, `// FIXME`, `// contactar admin` o etiquetas similares en código fuente.
- Imports agrupados: stdlib primero, luego terceros, luego locales. Sin líneas en blanco entre grupos.
- Nombres de paquetes en minúsculas, sin guiones bajos a menos que sea por legibilidad.
- Funciones públicas documentadas con comentario GoDoc de una línea.
- Logging con `log/slog` estructurado (nunca `fmt.Println` en producción).
- Manejo de errores explícito: `if err != nil { return err }` — sin `panic` fuera de `init`.
- Nombres de campos JSON en `snake_case` (ej: `telegram_id`, `created_at`).

### Frontend

- El scaffolding actual (`src/App.tsx`, `src/main.tsx`, `vite.config.ts`, `tsconfig.json`) está completamente vacío.
- Cuando se implemente el frontend: componentes en `src/components/`, tipos en `src/types/`, hooks en `src/hooks/`, llamadas API en `src/api/`, estilos en `src/styles/`.
- Todas las llamadas API van bajo `/proxy/*`, autenticadas con `Authorization: Bearer <token>`.

### Comentarios y docs

- Código en inglés. Documentación/README en español o inglés según corresponda.
- Todos los mensajes de commit en inglés.
- Esta guía (AGENTS.md) está en español por el equipo del proyecto.

---

## 4. Estructura de carpetas del backend

```
cmd/
  backend/main.go          ← servidor HTTP + WireGuard + CLI flags
  telegram-bot/            ← (vacío) binario separado del bot (no implementado)
internal/
  auth/                    ← (vacío) lógica de autenticación
  bot/handler.go           ← webhook Telegram, comandos /start /status /connect /help
  db/store.go              ← SQLite + DDL migrations + CRUD
  http/
    handlers/handlers.go   ← todos los HTTP handlers (auth, devices, traffic, health)
    middleware/             ← (vacío)
  metrics/                 ← (vacío) métricas Prometheus
  wg/manager.go            ← gestión WireGuard vía binario `wg`
pkg/
  config/config.go         ← carga variables de entorno
  models/models.go         ← structs (Device, User, TrafficSummary, etc.)
  utils/                   ← (vacío)
migrations/                ← (vacío) — migrations están embebidas en store.go
docker/
  backend.Dockerfile       ← multi-stage: golang:1.24-alpine → alpine:3.21
  wg-exporter.Dockerfile   ← (pendiente: cmd/exporter/ no existe)
scripts/
  build.sh                 ← compilación 100% dockerizada
dist/
  index.html               ← (auxiliar) SPA placeholder
frontend/
  src/                     ← scaffolding vacío (TypeScript + React + Vite)
```

---

## 5. WireGuard — reglas y restricciones

- **Usar el binario `wg` exclusivamente**. No usar la biblioteca Go `wgctrl` por incompatibilidad CGO/Alpine.
- El archivo de configuración del cliente (`ClientConfig`) se genera dinámicamente y se entrega al usuario **una sola vez** al crear el dispositivo. La clave privada no se vuelve a mostrar.
- El backend **nunca elimina** un peer de WireGuard si la eliminación falla — continua y registra el warning.
- Todas las operaciones `wg set` están protegidas por `sync.Mutex` en el `Manager`.
- El endpoint WireGuard de producción es `165.140.241.96:64000` (hardcoded en `main.go` cuando `WG_ENDPOINT_HOST` está vacío).

---

## 6. Base de datos

- SQLite en `./data/usipipo.db` por defecto.
- Migraciones embebidas en `internal/db/store.go`. No hay archivos de migración separados.
- **Bug conocido**: `ensureDir()` no crea directorios — esto puede causar fallo si `DB_PATH` apunta a una ruta cuyo directorio no existe (ver Bug #3 en CONTEXT.md).
- Tablas: `users`, `devices`, `traffic_samples`. Índices sobre `user_id` y `(device_id, timestamp)`.

---

## 7. Autenticación

- Flujo: Telegram Login Web App → HMAC-SHA256 del data_check_string con el BOT_TOKEN → JWT HS256 (30 días).
- El JWT se envía en `Authorization: Bearer <token>`.
- Todos los handlers de dispositivos requieren JWT válido (middleware `userFromCtx`).
- El endpoint del bot de Telegram NO requiere autenticación — se valida por `chat_id` de Telegram.

---

## 8. Docker / docker-compose.yml

### Servicios
| Servicio     | Imagen                | Puerto interno | Roles                           |
|--------------|-----------------------|----------------|---------------------------------|
| `wg-api`     | `usipipo/backend`     | 8001           | API + WireGuard                 |
| `frontend`   | `usipipo/frontend`    | 3000→80        | SPA React                       |
| `wg-exporter`| `usipipo/wg-exporter` | (no expuesto)  | Métricas Prometheus — NO IMPLEMENTADO |

### Permisos WireGuard (requeridos)
```yaml
cap_add:   [NET_ADMIN]
devices:   [/dev/net/tun:/dev/net/tun]
volumes:
  - /run/wireguard:/run/wireguard:ro
```

---

## 9. VPS y producción

- **IP AlphaVPS**: `165.140.241.96`
- **Dominio**: `usipipo.dpdns.org` (DuckDNS)
- **Caddy** escucha en `:80/:443` y reenvía `/proxy/*` → `localhost:9001`
- **TASALO** ya ocupa puertos `:8001`, `:8000`, `:8040` — uSipipo usa `/proxy` para no colisionar
- El backend compilado se despliega directamente en el VPS (no Docker en producción), servido por Caddy

---

## 10. Bugs conocidos

Ver §17 de CONTEXT.md. Resumen rápido:

| # | Archivo              | Descripción                                          | Estado      |
|---|----------------------|------------------------------------------------------|-------------|
| 1 | `internal/bot/handler.go` | `h.wgManager` nil — no se inicializa en constructor | pendiente   |
| 2 | `docker/wg-exporter.Dockerfile` | `cmd/exporter/` no existe                    | pendiente   |
| 3 | `internal/db/store.go`     | `ensureDir()` no crea directorios                 | pendiente   |
| 4 | `frontend/src/*`           | Todo el código frontend está vacío               | pendiente   |

---

## 11. Checklist de agentes antes de cualquier commit

- [ ] `go vet ./...` limpio
- [ ] No hay `// TODO`, `// MVP`, `// fake` en el código Go
- [ ] No se agregaron dependencias externas sin justificar
- [ ] `go.mod` y `go.sum` sincronizados
- [ ] Correspondencia entre cambios y descripción del commit
- [ ] Si se tocan handlers/DB/WG: revisar §5 y §6 de este archivo
