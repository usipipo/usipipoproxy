# CLAUDE.md — uSipipo Proxy

Este archivo complementa `AGENTS.md` con reglas específicas de interacción con Claude Code.

---

## Instrucciones generales

- **Lenguaje de código**: inglés
- **Lenguaje de interacción**: el agente debe usar el idioma que el usuario use. Si el usuario habla en español, responder en español. Si habla en inglés, responder en inglés.
- **Mensajes de commit**: siempre en inglés (`fix`, `feat`, `chore`, `docs`, `refactor`, `test`, `build`).

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
