# ROADMAP.md — uSipipo Proxy

> Estado del proyecto: **Backend completo | Bot Telegram operativo | Endpoint /conf | Frontend vacío | Apps pendientes**
> Última actualización: 2026-05-22T21:44 | Build: ✅ `go build ./...` | Vet: ✅ `go vet ./...`

---

## Resumen ejecutivo

| Capa | Estado | Completo |
|------|--------|----------|
| Backend Go (API + WireGuard + TronDealer) | ✅ Funcional | ~90 % |
| Telegram Bot (webhook + botones inline) | ✅ Funcional | ~90 % |
| Endpoint `GET /proxy/devices/{id}/conf` | ✅ Implementado | 100 % |
| App Web React | 🔄 En progreso — diseño aprobado | 5 % |
| App Android | ❌ No empezada | 0 % |
| wg-exporter (Prometheus) | ❌ No empezada | 0 % |
| CI/CD (GitHub Actions → GHCR) | ⏸ Pospuesto hasta completar frontend | — |

---

## Fase 0 — Setup y prerequisitos ✅ COMPLETADO

| Item | Estado |
|------|--------|
| API spec extraído del backend | ✅ 13 endpoints documentados |
| Vite + React 19 + TS + Tailwind v4 | ✅ `npm install` sin conflictos |
| Framer Motion + React Router | ✅ instalado |
| `docs/plans/frontend-design-plan.md` | ✅ plan de implementación escrito |

---

## Fase 1 — Backend: deuda técnica (P1)

### 1-A. Dividir archivos que exceden límite 300 líneas AGENTS.md §3

| Archivo | Líneas | Objetivo |
|---------|--------|----------|
| `internal/http/handlers/handlers.go` | **~960** | → `handlers/auth.go` + `handlers/devices.go` + `handlers/payments.go` + `handlers/health.go` |
| `internal/db/store.go` | **380** | → `store/store.go` + `store/migrations.go` |

**Criterio de salida:** cada archivo ≤ 300 líneas; `go build ./...` verde; `go vet ./...` verde.

---

### 1-B. Refactor UUID (`genUUIDv4`)

- Reemplazar `math/rand` por `github.com/google/uuid` o `crypto/rand`
- Afecta: `internal/http/handlers/handlers.go:~836`
- **Criterio de salida:** `grep -rn "math/rand" internal/` sin resultados

---

### 1-C. CI/CD GitHub Actions

- `.github/workflows/ci.yml`: `go vet ./...` + `go build ./...` en cada PR
- `.github/workflows/release.yml`: build multi-arch → `ghcr.io/usipipo/backend:tag`
- **Criterio de salida:** push a `main` dispara ambos workflows sin fallos

---

## Fase 2 — Bot Telegram ✅ (en progreso)

### 2-A. Envío de mensajes a Telegram ✅ IMPLEMENTADO

| Item | Estado |
|------|--------|
| `SendMessage(chatID, text, keyboard)` | ✅ Llamada HTTP directa a `api.telegram.org` |
| `parse_mode: MarkdownV2` | ✅ |
| `InlineKeyboardMarkup` por comando | ✅ |
| `/connect` → botón "📄 Descargar .conf" por `url` | ✅ |
| `/start`, `/help` → botones por `callback_data` | ✅ |
| `answerCallback` (acknowledge) | ✅ |
| `WebhookPayload` con `CallbackQuery` | ✅ |
| Servicio por comando (`cmdStart`, `cmdStatus`, etc.) | ✅ |

### 2-B. Endpoint `GET /proxy/devices/{id}/conf` ✅ IMPLEMENTADO

| Item | Estado |
|------|--------|
| Handler `ServeConf` | ✅ Content-Type text/plain + attachment |
| Verificación de propiedad (`d.UserID == uid`) | ✅ |
| Router usa `path.Base()` en vez de `HasSuffix` | ✅ |
| Columna `private_key` en BD + migración | ✅ |
| `wg.ClientConfig` generado desde BD | ✅ |

### 2-C. Pendiente de compilación

| Val | Descripción |
|-----|-------------|
| Build | El código está escrito pero falta verificar compilación después de los últimos edits |
| Vet | Idem |
| Sesión cookie (ver Fase 3-A) | El botón `.conf` en Telegram requiere auth por cookie o JWT en navegador |

---

## Fase 3 — App Web React ✅ EN PROGRESO *(P0)*

### 3. Diseño aprobado ✅ EN PROGRESO

| Dimensión | Decisión |
|-----------|---------|
| Estilo | Glassmorphism dark mode |
| Primary | Electric Blue #3b82f6 |
| Tipografía | Space Grotesk (headings) + DM Sans (body) |
| Layout pattern | Bento Grid |
| Animaciones | Framer Motion — stagger, parallax, scroll-reveal |
| Autenticación | Telegram Login → JWT → HttpOnly cookie |
| Tech stack | Vite + React 19 + TS + Tailwind CSS v4 |

**Plan de implementación:** `docs/plans/frontend-design-plan.md`
**Tracking:** `docs/tracking/implementation-status.md`

### 3-A. Autenticación por cookie de sesión

Flujo planeado:
1. Frontend recibe JWT de `POST /proxy/auth/telegram`
2. Frontend envía JWT a `POST /proxy/auth/cookie` → backend valida y seta cookie `HttpOnly; Secure; SameSite=Strict`
3. Navegador envía cookie automáticamente en `/proxy/devices/{id}/conf`

**Criterio de salida:** clic en botón "📄 Descargar .conf" desde Telegram → navegador descarga `.conf` sin pedir login.

---

### 3-B. Módulos a construir

| Módulo | Carpeta | Funcionalidad | Estado |
|--------|---------|---------------|--------|
| API client | `src/api/client.ts` | `fetch` wrapper con `Authorization: Bearer` automático | planned |
| Tipos | `src/types/index.ts` | DTOs TypeScript desde `pkg/models/models.go` | planned |
| Auth hook | `src/hooks/useAuth.ts` | Guarda/recupera JWT de `localStorage`; maneja login/logout | planned |
| Página Login | `src/pages/Login.tsx` | Telegram Login Widget embebido | planned |
| Página Dashboard | `src/pages/Dashboard.tsx` | Lista devices · crear device · descargar `.conf` | planned |
| Página Pagos | `src/pages/Payments.tsx` | Historial invoices · crear invoice · mostrar QR | planned |
| App router | `src/App.tsx` | Protección de rutas por JWT · navegación | planned |

**Criterio de salida:**
1. Login con Telegram → JWT guardado → redirect a dashboard
2. Dashboard lista dispositivos · crear dispositivo · descargar `.conf`
3. Pagos: crear invoice · ver QR code · historial facturas

---

## Fase 4 — App Android VPN *(P1)*

### Enfoque
Descargar el `.conf` desde el backend → importar en WireGuard nativo para Android.

### Pasos

| Paso | Tarea |
|------|-------|
| 4.1 | Backend: `GET /proxy/devices/{id}/conf` ✅ ya existe |
| 4.2 | Android app: login via WebView Telegram Login → JWT |
| 4.3 | Android app: lista de dispositivos → botón "importar" → intent WireGuard |
| 4.4 | Android app: toggle conectar/desconectar (via WireGuard API si está disponible) |

---

## Fase 5 — wg-exporter Prometheus *(P2)*

| Paso | Tarea |
|------|-------|
| 5.1 | `cmd/exporter/main.go`: sondea `wg show <iface> transfer` cada N segundos |
| 5.2 | Exportar `wg_peer_bytes_rx`, `wg_peer_bytes_tx`, `wg_peer_last_handshake_seconds` |
| 5.3 | Escuchar en `:9100/metrics` |
| 5.4 | Ajustar `docker/wg-exporter.Dockerfile` apuntando a `cmd/exporter/main.go` |

---

## Orden de ejecución recomendado

```
Fase 1-A (split archivos) → Fase 1-B (UUID refactor) →
Fase 2 completar compilación → Fase 3-A (cookie sesión) →
Fase 3-B (App Web) → Fase 1-C (CI/CD) → Fase 4 (Android) → Fase 5 (exporter)
```

---

## Criterios globales de done

| Criterio | Herramienta |
|---|---|
| Go compilación limpia | `go build ./...` (verificable en Docker) |
| Go vet limpio | `go vet ./...` (verificable en Docker) |
| Sin código muerto / TODOs | `grep -rn "TODO\|FIXME\|MVP"` |
| Cumplimiento SOLID + Clean Code | Revisión manual por AGENTS.md §3 |
| Cada archivo .go ≤ 300 líneas | `find . -name "*.go" -exec wc -l {} \;` |
| Build frontend limpio | `npm run build` 0 errors |
| Cobertura de pantallas | 375px / 768px / 1024px / 1440px |
