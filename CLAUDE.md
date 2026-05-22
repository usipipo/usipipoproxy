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
internal/wg/manager.go       — manejo de interfaces WireGuard prohibitivo modificar en caliente
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
- Corregir bugs conocidos (ver §10 de AGENTS.md).
- **NUNCA** agregar dependencias nuevas en `go.mod` sin aprobación explícita del usuario.

### Frontend React
- Todo el código frontend (`src/`) está vacío — se puede implementar completamente desde cero.
- Sigue estándares de `frontend-design` skill si está disponible.

### Infraestructura
- Actualizar `docker-compose.yml` cuando se agregue servicio nuevo (ej: `wg-exporter` funcional).
- Modificar Dockerfiles en `docker/` cuando se requiera.

### No tocar sin permiso
- Permisos WireGuard en `docker-compose.yml` — un error rompe la red.
- Datos del VPS (IPs, credenciales) — están hardcodeados; cambios deben ser intencionales.

---

## Flujo de trabajo por defecto al escribir/corregir código

1. **Leer el archivo relevante primero** (no editar a ciegas).
2. Escribir / corregir el cambio.
3. Verificar compilación: `docker run --rm -v "$PWD":/app -w /app golang:1.24-alpine sh -c "apk add git build-base && go build ./cmd/backend"` o `go build ./cmd/backend` localmente.
4. Pasar `go vet ./...` antes de considerar el cambio terminado.
5. Crear commit solo cuando el usuario lo pida explícitamente. Mensaje en inglés, formato git-conventional: `type(scope): descripción`.

---

## Referencias del proyecto

- `CONTEXT.md` — documento amplio con todos los detalles técnicos
- `AGENTS.md` — reglas y convenciones
- `README.md` — siguiendo el formato de esta misma sección, de clase a Estructuras
- `docker/.env.example` — todas las variables de entorno con valores por defecto
- `scripts/build.sh` — pipeline de compilación dockerizada
