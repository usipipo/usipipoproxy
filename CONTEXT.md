# uSipipo Proxy — CONTEXTO DEL PROYECTO

> **§1–§13** ven en los commits anteriores. Este archivo continúa en §14.

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

## 17. BUGS CONOCIDOS

### Bug #1 — `internal/bot/handler.go`: `h.wgManager` nil pointer

`WebhookHandler` tiene campo `wgManager` pero `NewWebhookHandler()` no lo inicializa. El comando `/connect` del bot llamará `h.wgManager.NextFreeIP()` → panic nil pointer.
**Arreglo**: agregar `*wg.Manager` a la estructura y al constructor; inyectar el manager desde `main.go`.

### Bug #2 — `docker/wg-exporter.Dockerfile` apunta a `cmd/exporter/` inexistente

El Dockerfile del exporter asume que el código fuente está en `cmd/exporter/` con su `go.mod` propio. El directorio no fue creado.
**Arreglo**: crear `cmd/exporter/` con todo el código Go del exporter, o eliminar el servicio de `docker-compose.yml` hasta implementarlo.

### Bug #3 — `internal/db/store.go`: `ensureDir()` es no-op

```go
func ensureDir(p string) error {
    if _, err := sql.Open("sqlite3", ":memory:"); err != nil { return err }
    return nil // <-- nunca crea el directorio
}
```
No crea directorios reales. Si `DB_PATH` apunta a `./data/usipipo.db` y `/app/data` no existe, falla.
**Arreglo**: usar `os.MkdirAll(p, 0755)`.

### Bug #4 — Código frontend completamente vacío

`main.tsx`, `App.tsx`, `vite.config.ts`, `tsconfig.json`, `package.json` — todos cero bytes. La app frontend debe escribirse desde cero.

## 18. CHECKLIST DE DESPLIEGUE

1. Backend compila sin errores (`go build`, `go vet ./...`)
2. Imágenes Docker construidas y etiquetadas
3. Imágenes empujadas a GHCR (`ghcr.io/usipipo/backend:TAG`, `ghcr.io/usipipo/frontend:TAG`)
4. VPS AlphaVPS: `docker compose up -d` (backend) o binario nativo + Caddyfile
5. Caddyfile actualizado con `reverse_proxy /proxy/* localhost:9001`
6. Sintaxis Caddy verificada: `caddy validate --config /etc/caddy/Caddyfile`
7. Caddy recargado: `systemctl reload caddy`
8. Seed ejecutado: `./backend --seed`
9. Frontend compilado y servido por Caddy
10. Webhook Telegram configurado (long polling o `setWebhook` a `https://usipipo.dpdns.org/bot/telegram`)
11. Prueba e2e: auth → JWT → crear dispositivo → WireGuard peer activo → `.conf` descargado → cliente conectado
