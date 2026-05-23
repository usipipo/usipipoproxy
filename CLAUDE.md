# CLAUDE.md — uSipipo Proxy

Este archivo complementa `AGENTS.md` con reglas específicas de interacción con Claude Code.

---

## Instrucciones generales

- **Lenguaje de código**: inglés
- **Lenguaje de interacción**: el agente debe usar el idioma que el usuario use. Si el usuario habla en español, responder en español. Si habla en inglés, responder en inglés.
- **Mensajes de commit**: siempre en inglés (`fix`, `feat`, `chore`, `docs`, `refactor`, `test`, `build`).

---

## Principios SOLID y Clean Code (obligatorios en todo código Go)

Antes de modificar cualquier handler, struct o paquete, revisar que el cambio cumpla:

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
- **Sin comentarios-obvio**: no comentar lo que el código ya expresa claramente. Los comentarios explican el *porqué*, no el *qué*.
- **Zero valores explícitos**: cuando un valor cero de Go tiene significado de negocio, documentarlo con un comentario; no confundir `0`, `""`, `nil` por omisión.
- **Exportar solo lo público**: funciones/métodos que no se usan fuera del paquete van en minúsculas.
- **DRY con interfaces, no copy-paste**: si dos bloques son idénticos, extraer a una función compartida; si difieren solo en el tipo, usar programación genérica.

---

## Archivos fuente confiables

El agente **debe leer** estos archivos antes de modificar cualquier parte del backend:

```
cmd/backend/main.go          — arranque del servidor, rutas, flags
internal/wg/manager.go       — manejo de interfaces WireGuard (prohibido modificar sin análisis previo)
internal/http/handlers/handlers.go — toda la lógica de API + middleware JWT

pkg/models/models.go         — contratos de datos públicos
pkg/config/config.go         — carga de env vars
internal/db/store.go         — CRUD + migraciones SQLite
```

No modificar `docker-compose.yml` sin antes confirmar con el usuario (afecta puertos ciclicados).

---

## ¿Qué se puede/debe hacer?

### Backend Go
- Modificar `handlers.go` para nuevos endpoints, cambios de validación, reformas.
- Modificar `models.go` para agregar/alterar campos públicos (mantén `snake_case` en JSON).
- Modificar `config.go` para variables de entorno nuevas (poner defaults sensatos).
- Corregir bugs conocidos (ver §11 de AGENTS.md).
- **NUNCA** agregar dependencias nuevas en `go.mod` sin aprobación explícita del usuario.
- Variables de entorno de pagos: `TD_API_KEY`, `TD_WEBHOOK_SECRET`, `WEBHOOK_BASE_URL` (definir en `config.go`, defaults sensatos).
- Nunca liberar suscripción en estado `detected`; solo en `confirmed` o `notified`.
- Endpoints de pago nuevos van bajo `/proxy/payments/*` y `/proxy/webhooks/trondealer`.

### Frontend React
- Todo el código frontend (`src/`) está vacío — se puede implementar completamente desde cero.
- Sigue estándares de `frontend-design` skill si está disponible.
- El QR de pago se genera en el frontend a partir de la dirección BSC y monto USDT que entrega el backend.

### Infraestructura
- Actualizar `docker-compose.yml` y `docker/.env.example` cuando se agregue variable nueva (ej: `TD_API_KEY`).
- Modificar Dockerfiles en `docker/` cuando se requiera.

### No tocar sin permiso
- Permisos WireGuard en `docker-compose.yml` — un error rompe la red.
- Datos del VPS (IPs, credenciales, TronDealer api_key) — están hardcodeados; cambios deben ser intencionales.
- `x-api-key` de TronDealer: SOLO en backend, nunca en frontend ni mobile.
- Cambios a tablas de BD pagos/invoices: confirmar con el usuario antes de tocar store.go migraciones.

---

## Flujo de trabajo por defecto al escribir/corregir código

1. **Leer el archivo relevante primero** (no editar a ciegas).
2. Escribir / corregir el cambio.
3. Verificar compilación: `docker run --rm -v "$PWD":/app -w /app golang:1.24-alpine sh -c "apk add git build-base && go build ./cmd/backend"` o `go build ./cmd/backend` localmente.
4. Pasar `go vet ./...` antes de considerar el cambio terminado.
5. Crear commit solo cuando el usuario lo pida explícitamente. Mensaje en inglés, formato git-conventional: `type(scope): descripción`.

---

## Referencias del proyecto

- `CONTEXT.md` — documento amplio con todos los detalles técnicos (§19 incluye todo modelo de pagos TronDealer)
- `AGENTS.md` — reglas y convenciones
- `README.md` — siguiendo el formato de esta misma sección, de clase a Estructuras
- `docker/.env.example` — todas las variables de entorno con valores por defecto; agregar `TD_API_KEY`, `TD_WEBHOOK_SECRET` cuando se implementen pagos
- `scripts/build.sh` — pipeline de compilación dockerizada

---

## Frontend — App Web uSipipo Proxy (Fase 3 — EN PROGRESO)

**Tech stack:** Vite + React 19 + TypeScript + Tailwind CSS v4 + Framer Motion + React Router + Lucide Icons

**Scaffolding:** `npm install` sin conflictos, `npm run build` 0 errores, dev server `localhost:5173`

**Plan de implementación:** `docs/plans/frontend-design-plan.md`
**Tracking:** `docs/tracking/implementation-status.md`

**Design system:**
- Glassmorphism dark mode — fondo `#030712` a `#0f172a` gradientes
- Primary: Electric Blue `#3b82f6`
- Tipografía: Space Grotesk (headings) + DM Sans (body)
- Patrón layout: Bento Grid
- Animaciones: Framer Motion — stagger, parallax, scroll-reveal, word-by-word texto

**Autenticación:** Telegram Login → JWT → Post `/proxy/auth/cookie` → HttpOnly cookie `session`

**API calls:** Todos bajo `/proxy/*`, autenticados via `Authorization: Bearer` o cookie `session`

**Arquitectura frontend:**
```
src/api/client.ts         — fetch wrapper + Bearer auto
src/types/index.ts        — DTOs TypeScript
src/hooks/useAuth.ts      — JWT guard/recupera
src/hooks/usePayment.ts   — TronDealer payment flow
src/components/           — GlassCard, AnimatedButton, ScrollReveal, Sidebar, etc.
src/pages/                — Landing, Login, Dashboard, Devices, Payments
src/styles/globals.css     -- design tokens + glass utilities
```
