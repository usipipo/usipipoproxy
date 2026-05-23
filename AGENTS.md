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
| Pagos        | TronDealer V2 — USDT BEP-20 BSC, webhook HMAC-SHA256, auto-sweep                                    |
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

### Go — Principios SOLID y Clean Code

Cada handler, struct y paquete debe adherirse a estos principios de forma explícita:

| Principio | Regla concreta |
|------------|----------------|
| **S**ingle Responsibility | Cada handler/structure/método tiene una sola razón para cambiar. No mezclar lógica de pagos, auth y dispositivos en el mismo tipo. |
| **O**pen/Closed | Abierto a extensión (tagged results, nuevos tipos), cerrado a modificación. Usar `type Switch` o funciones genéricas en lugar de modificar código existente para agregar un caso nuevo. |
| **L**iskov Substitution | Los tipos que satisfacen una interfaz (ej: `PaymentStore`, `DeviceStore`) deben poder usarse intercambiablemente sin comprobar el tipo concreto. |
| **I**nterface Segregation | Definir interfaces pequeñas y específicas aquí en el paquete que las consume, no interfaces grandes en el paquete que las implementa. Preferir 3 interfaces de 2 métodos a 1 interfaz de 6 métodos. |
| **D**ependency Inversion | Depender de interfaces, no de structs concretas. Los constructores reciben interfaces (`AuthStore`, `PaymentStore`, `*wg.Manager`), nunca `*sql.DB` o `*Store` directamente en handlers. |

#### Reglas de Clean Code adicionales

- **Tamaño de archivo**: máximo 300 líneas por archivo `.go`. Si un archivo supera ese límite, dividirlo antes de agregar más código.
- **Tamaño de función**: máximo 70 líneas. Las funciones largas deben descomponerse en helpers privados.
- **Profundidad de anidación**: máximo 3 niveles de `if`/`for` anidados. Extraer a funciones auxiliares o usar early returns para aplanar.
- **Nombres expresivos**: variables de una sola letra solo aceptables en `for i := range` o fórmulas matemáticas muy locales. Los parámetros de función deben ser auto-documentados.
- **Sin magic numbers**: extraer constantes con nombre descriptivo (ej: `defaultInvoiceTTL = 30 * time.Minute` en lugar de `time.Minute * 30` inline).
- **Return temprano**: preferir `if err != nil { return err }` al inicio de la función antes que bloques `else` profundos.
- **Sin comentarios-obvio**: no comentar lo que el código ya expresa claramente (ej: `// incrementar contador` sobre `count++`). Los comentarios explican el *porqué*, no el *qué*.
- **Zero valores explícitos**: cuando un valor cero de Go tiene significado de negocio, documentarlo con un comentario; no confundir `0`, `""`, `nil` por omisión.
- **Exportar solo lo público**: funciones/métodos que no se usan fuera del paquete van en minúsculas. La superficie de API pública de cada paquete debe ser deliberada y mínima.
- **DRY con interfaces, no copy-paste**: si dos bloques de código son idénticos, extraer a una función compartida; si difieren solo en el tipo, usar programación genérica (`[T any]`).

### Frontend

- Todo el código Go vive bajo `internal/` o `pkg/`. No exponer paquetes internos.
- **Nunca** usar `// TODO`, `// MVP`, `// fake`, `// FIXME`, `// contactar admin` o etiquetas similares en código fuente.
- Imports agrupados: stdlib primero, luego terceros, luego locales. Sin líneas en blanco entre grupos.
- Nombres de paquetes en minúsculas, sin guiones bajos a menos que sea por legibilidad.
- Funciones públicas documentadas con comentario GoDoc de una línea.
- Logging con `log/slog` estructurado (nunca `fmt.Println` en producción).
- Manejo de errores explícito: `if err != nil { return err }` — sin `panic` fuera de `init`.
- Nombres de campos JSON en `snake_case` (ej: `telegram_id`, `created_at`).

### Frontend

- El scaffolding Vite + React 19 + TS + Tailwind v4 está **funcional**: `npm install` completado sin conflictos, `npm run build` exitoso (0 errores), dev server en `localhost:5173`. Framer Motion, React Router y Lucide React instalados. Implementación en progreso por `docs/plans/frontend-design-plan.md`.
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
- Migraciones embebidas en `internal/db/migrations.go`. No hay archivos de migración separados.
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

## 9. Pagos — TronDealer V2

### Estrategia
- **Prepagado en días:** usuario elige cantidad de días; monto USDT = días × `rate` (`$1.99/30 días = 0.06633 USDT/día`).
- **Early adopters:** campo `early_adopter INTEGER DEFAULT 0` en tabla `users` → descuento 80% sobre monto pagado.
- **Red de depósito:** BSC BEP-20 USDT · Contrato: `0x55d398326f99059fF775485246999027B3197955` (18 decimales).
- **Expiración de invoice/wallet TronDealer:** 30 minutos desde generación.

### Flujo técnico
1. Backend → `POST /proxy/payments/invoice` con `{days, user_id}`
2. Backend calcula monto, aplica descuento early_adopter si corresponde
3. Backend llama a `POST https://www.trondealer.com/api/v2/wallets/assign` con `label=order-{uuid}` → recibe dirección BSC
4. Backend registra invoice en BD (estado `pending`)
5. Frontend genera QR a partir de dirección + monto → usuario escanea con wallet
6. Usuario envía USDT BEP-20 a la dirección
7. Webhook `notified` de TronDealer → valida `X-Signature-256` HMAC-SHA256 → marca `confirmed` → acredita días
8. Webhook `swept` → registra en bitácora (reconciliación)

### Endpoints nuevos
| Método | Ruta                        | Descripción                   |
|--------|----------------------------|-------------------------------|
| POST   | `/proxy/payments/invoice`   | Crea invoice TronDealer       |
| GET    | `/proxy/payments/invoices`  | Historial invoices del usuario|
| POST   | `/proxy/webhooks/trondealer`| Webhook TronDealer (valida firma)|

### Nuevas tablas BD
- `invoices`: `id, user_id, td_wallet_label, amount_usdt, days, status, tx_hash, td_order_id, created_at, confirmed_at, sweep_at`
- `users`: agregar columna `early_adopter INTEGER DEFAULT 0`

### Reglas estrictas
- **Nunca** liberar suscripción en estado `detected`. Solo en `confirmed`/`notified`.
- **Idempotencia:** usar `tx_hash + log_index` como clave única en `invoices`.
- `x-api-key` TronDealer SOLO en backend, nunca en frontend/mobile.
- Webhook: devolver `200` inmediatamente; procesar evento de forma asíncrona si hay lógica pesada.

---

## 10. VPS y producción

- **IP AlphaVPS**: `165.140.241.96`
- **Dominio**: `usipipo.dpdns.org` (DuckDNS)
- **Caddy** escucha en `:80/:443` y reenvía `/proxy/*` → `localhost:9001`
- **TASALO** ya ocupa puertos `:8001`, `:8000`, `:8040` — uSipipo usa `/proxy` para no colisionar
- El backend compilado se despliega directamente en el VPS (no Docker en producción), servido por Caddy

---

## 11. Bugs conocidos y deuda técnica

Resumen rápido (2026-05-22T22:48):

| # | Archivo / Área            | Descripción                                          | Estado    | Prioridad |
|---|---------------------------|------------------------------------------------------|-----------|-----------|
| 1 | `internal/bot/handler.go` | `h.wgManager` nil — **resuelto** (inyectado en `main.go:71`) | ✅ cerrado | — |
| 3 | `internal/db/`            | `ensureDir()` — **resuelto** (`os.MkdirAll`) | ✅ cerrado | — |
| 5 | `internal/http/handlers/` | Endpoints TronDealer — **resuelto** | ✅ cerrado | — |
| 6 | `pkg/models/` + `internal/wg/` | `Device`/`ClientConfig` duplicado — **resuelto por refactor** | ✅ cerrado | — |
| 7 | `handlers.go` (~960 l)    | Excede límite 300 líneas — **resuelto** → 7 archivos | ✅ cerrado | — |
| 8 | `store.go` (380 l)        | Excede límite 300 líneas — **resuelto** → 2 archivos | ✅ cerrado | — |
| 9 | Bot Telegram | SendMessage no enviaba replies — **resuelto** | ✅ cerrado | — |
| 9-a| `internal/http/middleware/` | AuthMiddleware cookie: verificado, compilación ✅ | ✅ cerrado | — |
| 10 | `cmd/exporter/` / Dockerfile | `docker/wg-exporter.Dockerfile` apunta a ruta inexistente | 🔄 abierto | **P2** |
| 11 | `scripts/vet.sh`          | Go 1.24 no instalado en host, solo vía Docker | 🔄 abierto | **P3** |
| 12 | `uuid.go` / `genUUIDv4()` | Usaba `math/rand` — **resuelto** por `crypto/rand` RFC 4122 | ✅ cerrado | — |
| 13 | Bot Telegram `/connect`   | `device` sin PSK guardado — pendiente | 🔄 abierto | **P2** |
| 14 | `docs/plans/frontend-design-plan.md` | Plan de implementación frontend escrito | 📄 fase | — |

> `go build ./...` ✅ | `go vet ./...` ✅ | CI/CD workflows creados | Dockerfile multi-arq corregido

---

## 12. Checklist de agentes antes de cualquier commit

- [ ] `go vet ./...` limpio
- [ ] No hay `// TODO`, `// MVP`, `// fake` en el código Go
- [ ] No se agregaron dependencias externas sin justificar
- [ ] `go.mod` y `go.sum` sincronizados
- [ ] Correspondencia entre cambios y descripción del commit
- [ ] El código cumple los principios SOLID (§3) y las reglas de Clean Code (§3)
- [ ] Cada archivo `.go` modificado no supera las 300 líneas
- [ ] Ninguna función supera las 70 líneas
- [ ] Profundidad de anidación ≤ 3 niveles en todo el código modificado
- [ ] Si se tocan handlers/DB/WG: revisar §5 y §6 de este archivo
- [ ] Si se tocan pagos: revisar §9 y §19 de CONTEXT.md

---

## 13. Roadmap — criterios de salida por fase

| Fase | Criterio de salida |
|------|-------------------|
| ✅ Fase 1-A | Handlers/Store divididos → compilación y `go vet ./...` limpios |
| ✅ Fase 1-B | UUID `crypto/rand` RFC 4122 → tests unitarios pasan |
| ✅ Fase 3-A cookie sesión → **Fase 3-B frontend arranca después** (diseño aprobado, plan en `docs/plans/frontend-design-plan.md`, scaffolding listo) |
| ⬜ Fase 1-C | CI/CD GitHub Actions completo + build multi-arq |
| ⬜ Fase 4 | App Android conecta con backend vía `/proxy/*` |
| ⬜ Fase 5 | Exporter Prometheus exponen métricasWG |

