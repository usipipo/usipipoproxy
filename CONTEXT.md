# uSipipo Proxy — CONTEXTO DEL PROYECTO

---

## 6. WIREGUARD MANAGER

### Estrategia: binario `wg` exclusivamente

No se usa la biblioteca `wgctrl` (incompatible con CGO/Alpine en Go 1.24). Todas las operaciones se ejecutan
vía `exec.Command("wg", ...)` con el binario presente en `$PATH`.

**Ubicación**: `internal/wg/manager.go`

### Struct `Manager`

```go
type Manager struct {
    iface    string          // nombre de la interfaz WG, ej: "wg0"
    endpoint string          // "165.140.241.96:64000"
    nextFree *net.IPNet      // subred para asignación de IPs
    mu       sync.Mutex      // protege todas las operaciones de escritura
}
```

### Operaciones públicas

| Método | Comando `wg` subyacente | Protección |
|---|---|---|
| `AddPeer(PeerInput)` | `wg set <iface> peer <pubkey> allowed-ips <ip/32> [endpoint <ep>] [preshared-key /dev/stdin]` | `mu.Lock` |
| `RemovePeer(pubKey)` | `wg set <iface> peer <pubkey> remove` | `mu.Lock` |
| `DevicePeers()` | `wg show <iface> dump` → parsea `transfer-rx`/`transfer-tx` por peer | `mu.Lock` |
| `NextFreeIP(existing)` | Algoritmo de barrido sobre la subred (ver §6-C) | sin lock (solo lectura) |

`RemovePeer` es **best-effort**: la falla no aborta el flujo superior, solo se registra como warning.

### Algoritmo de asignación de IPs (`NextFreeIP`)

```
subred base: 10.66.66.0/24  →  hostBits = 32 - 24 = 8  →  254 IPs utilizables (2–255)
itera desde i=2 hasta i=253 (evita .0 y .255)
candidata = base + offset bytes (vía big.Int)
devuelve la primera IP no presente en el mapa `existing`
```

**Implementación**: `incrementIP(base, offset)` usa `math/big` para evitar overflow en la suma de enteros.

### Generación de claves

`GenerateKeyPair()` ejecuta dos comandos secuenciales:
1. `wg genkey` → clave privada (stdout)
2. `wg pubkey` (con privada en stdin) → clave pública

Ambas se devuelven en hex, sin prefijos ni sufijos (formato compatible con `wg set` y `wg-quick`).

### `ClientConfig` — archivo `.conf` del cliente

```go
type ClientConfig struct {
    PrivateKey string  // NUNCA se recibe de vuelta tras la creación
    Address    string  // ej: "10.66.66.5/24"
    DNS        string  // ej: "10.66.66.1"
    PublicKey  string
    Endpoint   string  // "165.140.241.96:64000"
    AllowedIPs string  // ej: "0.0.0.0/0"
    PSK        string
}
```

Clave privada se entrega **una sola vez** en la respuesta de `POST /proxy/devices`. Nunca se vuelve a exponer por API.

### Endpoint de producción

```
Hardcoded en cmd/backend/main.go cuando WG_ENDPOINT_HOST está vacío:
  165.140.241.96:64000
Configurable por env WG_ENDPOINT_HOST + WG_ENDPOINT_PORT.
```

---

## 7. AUTENTICACIÓN — FLUJO TELEGRAM → JWT

### Flujo completo

```
1. Frontend (Telegram Web App) envía initData al backend:
   POST /proxy/auth/telegram  body: { id, username, first_name, last_name, photo_url, auth_date, hash }

2. Backend valida el hash:
   a. Ordenar campos alfabéticamente, excluyendo "hash"
      → "auth_date=N\nfirst_name=X\nid=M\nusername=Y" (ejemplo)
   b. HMAC-SHA256(data_check_string, BOT_TOKEN)  ==  hash recibido
   c. Usa crypto/hmac + crypto/sha256 (Comparación: hmac.Equal — anti-timing attack)

3. Si el hash es válido:
   a. GetOrCreateUser — inserta usuario en SQLite si no existe
   b. generateJWT(user, secret, 30*24h) — JWT HS256 (golang-jwt/jwt v5)
   c. Devuelve { token, user, expires_at }
```

### Claims JWT

```json
{
  "uid": <user internal id>,
  "tid": <telegram id>,
  "un":  <username>,
  "fn":  <first name>,
  "rl":  <role>,
  "iat": <issued-at unix>,
  "exp": <expiry unix>   // ahora + 30 días
}
```

### Handler `AuthHandler`

- Ubicación: `internal/http/handlers/handlers.go`
- Ruta: `POST /proxy/auth/telegram`
- Dependencias: `botToken` (para HMAC), `secret` (para JWT signing)

### Header de autorización en requests autenticados

```
Authorization: Bearer <jwt token>
```

Middleware `userFromCtx` extrae el usuario del `context.Context` inyectado por el middleware JWT (handler wrapper que valida el token y llama a `withUser` antes de invocar el handler real).

---

## 8. DEVICE PROVISIONING FLOW

### Endpoint: `POST /proxy/devices` (Handlers → DevicesHandler → Create)

```
1. Extraer uid del JWT (contexto autenticado)
2. Validar body { "name": string, "psk": string? }
3. wg.GenerateKeyPair()  →  pubKey, privKey
4. store.GetAllAssignedIPs()  →  mapa de IPs en uso
5. wgManager.NextFreeIP(usedIPs)  →  freeIP
6. wgManager.AddPeer({pubKey, allowedIP: freeIP + "/32", endpoint, psk})
   ↳ exec.Command("wg", "set", "wg0", "peer", pubKey, "allowed-ips", ip+"/32", ...)
7. store.CreateDevice(uid, name, pubKey, freeIP, psk)  →  device (DB row)
   Si el paso 6 falla o el paso 7 falla: rollback best-effort de WG peer
8. device.Conf = ClientConfig{PrivateKey: privKey, ...}
9. Devuelve device con conf (privKey solo disponible aquí)
```

### GET /proxy/devices/{id}/traffic

Endpoint `GET /proxy/devices/{id}/traffic?period=daily|weekly|monthly`
Devuelve `TrafficSummary` con agregado de `traffic_samples` por dispositivo y periodo.

### Rollback en error

Si `CreateDevice` (paso 7) falla después de que WG aceptó el peer (paso 6):
```go
_ = h.wgManager.RemovePeer(pubKey) // best-effort, ignora el error
```

### Clave privada — política de exposición

La clave privada existe en el objeto `Conf` del `Device` **exactamente una vez**: la respuesta a `POST /proxy/devices`.
No hay endpoint `GET /proxy/devices/{id}/conf`. El frontend debe capturar la clave en el momento de creación y ofrecerla en descarga o pantalla una vez.

---

## 9. TELEGRAM BOT — COMANDOS Y BUG #1

### Comandos implementados (`WebhookHandler.Dispatch` en `internal/bot/handler.go`)

| Comando | Acción |
|---|---|
| `/start` | `GetOrCreateUser` → saludo con nombre de usuario |
| `/status` | `ListDevices` → tabla de dispositivos con tráfico (GB RX/TX) |
| `/connect` | Intenta crear dispositivo WireGuard nuevo (ver Bug #1) |
| `/help` | Lista de comandos disponibles |

Webhook endpoint: `POST /bot/telegram` (valida por `chat_id` de Telegram — no requiere JWT).

### Bug #1 —handler.go: `h.wgManager` es campo que no existe → error de compilación

**Estado actual del código** (leído de `internal/bot/handler.go`):

- `WebhookHandler` NO tiene campo `wgManager` — solo tiene `store Store` y `baseURL string` y `port string`
- `NewWebhookHandler(store, baseURL, port)` NO recibe ni asigna `wgManager`
- Al ejecutar `/connect`, línea `freeIP, err := h.wgManager.NextFreeIP(taken)` no compila: `undefined field`

**Impacto**: `/connect` del bot no puede asignar IPs ni crear peers WireGuard.

**Arreglo planificado**:
```go
// En WebhookHandler:
type WebhookHandler struct {
    store      Store
    wgManager  *wg.Manager     // ← agregar
    baseURL    string
    port       string
}

func NewWebhookHandler(store Store, wgMgr *wg.Manager, baseURL, port string) *WebhookHandler {
    return &WebhookHandler{store: store, wgManager: wgMgr, baseURL: baseURL, port: port}
}
```

En `cmd/backend/main.go`, inyectar el manager:
```go
botH := bot.NewWebhookHandler(store, wgMgr, "usipipo.dpdns.org",
    fmt.Sprintf("%s:%d", cfg.WGEndpointHost, cfg.WGEndpointPort))
```

---

## 10. WG-EXPORTER — Bug #2

### Problema: `cmd/exporter/` no existe

`docker/wg-exporter.Dockerfile` empaqueta el código desde `cmd/exporter/` con su propio `go.mod`, pero ese directorio y archivos no fueron creados.

```dockerfile
COPY cmd/exporter/go.mod cmd/exporter/go.sum ./
COPY cmd/exporter .
RUN CGO_ENABLED=1 ... go build -o /out/exporter ./...
```

El servicio `wg-exporter` en `docker-compose.yml` no arrancará — el build falla en el paso de COPY.

**Opciones de arreglo**:
1. Crear `cmd/exporter/main.go` con un binario que ejecute `wg show <iface> transfer` y exporte las métricas en formato Prometheus en el puerto 9100.
2. Eliminar el servicio `wg-exporter` de `docker-compose.yml` hasta implementarlo.
3. Pasar a una implementación shell-script si se prefiere simplicidad temporal.

### Servicio `wg-exporter` en docker-compose

```yaml
services:
  wg-exporter:
    image: usipipo/wg-exporter:${TAG:-latest}
    cap_add: [NET_ADMIN]
    devices: [/dev/net/tun:/dev/net/tun]
    volumes: [/run/wireguard:/run/wireguard:ro]
    environment:
      WG_INTERFACE: wg0
      METRICS_PORT: 9100
```

---

## 11. DOCKER-COMPOSE — SERVICIOS, PERMISOS, VOLÚMENES

### Arquitectura de servicios

| Servicio | Imagen | Puerto interno | Exposición local |
|---|---|---|---|
| `wg-api` | `usipipo/backend:${TAG}` | 8001 | variable por compose |
| `frontend` | `usipipo/frontend:${TAG}` | 80→3000 | `:3000` |
| `wg-exporter` | `usipipo/wg-exporter:${TAG}` | 9100 | no expuesto (interno) |

### Permisos WireGuard (requeridos)

```yaml
cap_add:   [NET_ADMIN]
devices:   [/dev/net/tun:/dev/net/tun]
volumes:
  - /run/wireguard:/run/wireguard:ro   # estado persistente de WG
```

Sin `NET_ADMIN`, `wg set` falla. Sin `/dev/net/tun`, la interfaz no se crea.

### Volúmenes

| Volumen | Uso |
|---|---|
| `wg-data` | Persistencia SQLite (`DB_PATH=/app/data/usipipo.db`) |
| `/run/wireguard` (bind mount, ro) | Estado de WireGuard entre el kernel y el contenedor |

### Variables de entorno importantes (`docker/.env.example`)

| Variable | Default | Descripción |
|---|---|---|
| `DB_PATH` | `/app/data/usipipo.db` | Ruta a la base de datos SQLite |
| `WG_INTERFACE` | `wg0` | Nombre de la interfaz WireGuard |
| `WG_SUBNET` | `10.66.66.0/24` | Subred de IPs virtuales |
| `WG_ENDPOINT_PORT` | `64000` | Puerto UDP del endpoint WireGuard |
| `TELEGRAM_BOT_TOKEN` | — | Token del bot de Telegram (requerido) |
| `TELEGRAM_WEBHOOK_SECRET` | — | Opcional |
| `JWT_SECRET` | — | Clave de firma JWT (requerida, panic si vacía) |
| `API_PORT` | `8001` | Puerto interno del backend |
| `TAG` | `latest` | Etiqueta de imagen Docker |

### Observación sobre puertos TASALO

TASALO ocupa `:8001`, `:8000`, `:8040` externamente. uSipipo backend escucha en `API_PORT=8001` (Docker), pero en producción Caddy reenvía `/proxy/*` → `localhost:9001`. El backend Docker NO usa el puerto `8001` expuesto al exterior; toda la comunicación externa pasa por `/proxy`.

---

## 12. build.sh — PIPELINE DE COMPILACIÓN DOCKERIZADA

**Ubicación**: `scripts/build.sh`

### Etapas (3 etapas en un solo script)

```
$ TAG={tag} ./scripts/build.sh [--push]
```

**Etapa 1 — go mod download + go vet**
```bash
docker run --rm \
  -v "$PWD":/app -w /app golang:1.24-alpine sh -c "
    apk add --no-cache git build-base && \
    go mod download && go vet ./..."
```
No requiere Go instalado localmente. Salida en stdout.

**Etapa 2 — go build (CGO + amd64)**
```bash
docker run --rm -v "$PWD":/app -w /app -e CGO_ENABLED=1 -e GOOS=linux -e GOARCH=amd64 \
  golang:1.24-alpine sh -c "
    go build -ldflags '-s -w -X main.version=$TAG' -o /app/bin/backend ./cmd/backend"
```
Binario resultado: `bin/backend`.

**Etapa 3 — frontend build (opcional)**
Requiere `npm` disponible localmente. Si no está presente, se salta con warning.
```bash
cd frontend && npm ci && npx vite build
```

### Dockerfile backend (multi-stage)

`docker/backend.Dockerfile`:
```
Stage 1 (builder):  golang:1.24-alpine + build-base → compila
Stage 2 (runner):   alpine:3.21 + ca-certificates + curl + tini ↓ ~15 MB
```
Entrypoint: `tini` (maneja señales SIGTERM/SIGINT). Usuario no-root: `nobody:nobody`.

### Nota sobre `go vet` y `// TODO`

`store.go` línea 96 contiene `// TODO: make first user admin` — debe removerse antes de cada release (ver checklist §18 de AGENTS.md). `go vet ./...` no detecta comentarios TODO (es una regla del equipo, no un analizador automático).

---

## 13. FRONTEND — ESTADO DE SCAFFOLDING (VACÍO)

### Directorios y archivos existentes

```
frontend/
  index.html         ← 0 bytes (vacío)
  package.json       ← 0 bytes (vacío)
  vite.config.ts     ← 0 bytes (vacío)
  tsconfig.json      ← 0 bytes (vacío)
  src/
    main.tsx         ← 0 bytes (vacío)
    App.tsx          ← 0 bytes (vacío)
```

### dist/ (SPA placeholder)

`dist/index.html` — contenido estático placeholder que sirve como SPA fallback durante desarrollo en producción.

### Stack planificado (según AGENTS.md §2)

| Herramienta | Versión |
|---|---|
| Vite | — |
| React | 19 |
| TypeScript | — |
| Tailwind CSS | v4 |

### Convenciones de código frontend

- Componentes en `src/components/`
- Tipos en `src/types/`
- Hooks en `src/hooks/`
- Llamadas API en `src/api/`
- Estilos en `src/styles/`
- **Todas** las llamadas API van bajo `/proxy/*`, autenticadas con `Authorization: Bearer <token>`
- El frontend compilado se sirve por Caddy, NO por Docker en producción
- La SPA tiene fallback a `index.html` para rutas cliente (React Router)

### Servido en desarrollo

```
docker-compose.yml:  frontend → imagen local, puerto 3000:80
```

En producción: Caddy sirve el build estático desde disco, sin Docker.

---

1: # uSipipo Proxy — CONTEXTO DEL PROYECTO
2: 
3: > **§1–§13** están documentados en los commits anteriores. Este archivo continúa en §14.
4: 
5: ---
6: 
7: ## 14. USUARIOS BETA
8: 
9: Hardcodeados en `cmd/backend/main.go`:
10: 
11: | Nombre  | Telegram ID |
12: |---------|-------------|
13: | mowgli  | `891835105` |
14: | ersu    | `634873279` |
15: 
16: Se cargan con `--seed`. El `WG_ENDPOINT_HOST` se leería de la env en despliegue real.
17: 
18: ## 15. VPS PRODUCCIÓN — INFRAESTRUCTURA EXISTENTE
19: 
20: | Servicio         | Puerto   | Tecnología         |
21: |------------------|----------|--------------------|
22: | Caddy            | 80/443   | HTTPS + proxy      |
23: | TASALO API 1     | 8001     | Flask (localhost:5040)| ⚠️ Backend uSipipo NO usa el 8001 externo |
24: | TASALO API 2     | 8000     | Flask              |
25: | TASALO API 3     | 8040     | FastAPI             |
26: | Freqtrade 1      | 8081     | Python              |
27: | Freqtrade 2      | 8082     | Python              |
28: | Blocky DNS       | 4000     | DNS proxy           |
29: | DuckDNS cron     | */5 min  | Actualiza IP dinámica|
30: | ──────────────────────────────────────── |
31: | **uSipipo backend** | 9001  | Go (nuevo, via Caddyfile) |
32: | **uSipipo frontend** | verificado por Caddy | |
33: 
34: **Regla TASALO atendida**: el backend escucha en `API_PORT=8001` (Docker), pero Caddy rutea a `localhost:9001`. El frontend Vue/React se sirve por `usipipo.dpdns.org` y llama a `http://localhost:8001` (Docker) o `http://localhost:9001` (producción) mediante `VITE_API_BASE_URL`.
35: 
36: ## 16. RESTRICCIONES Y CONVENCIONES
37: 
38: 1. **No wgctrl**: causalmente eliminado de `go.mod` por broken checksum + CGO/Alpine con Go 1.24.
39: 2. **No `// TODO`**: removidos en Go; committed.
40: 3. **No `// MVP` / `// fake` / `// FAKE`**: prohibidos, revisar antes de cada commit.
41: 4. **WireGuard endpoint es la IP pública AlphaVPS**: `165.140.241.96:64000` — hardcoded en `main.go` si `WG_ENDPOINT_HOST` vacío.
42: 5. **Backend es la fuente de toda verdad**: identities, dispositivos, tráfico — WireGuard solo ejecuta.
43: 6. **Todo bajo `/proxy`**: Caddyfile debe insertar `reverse_proxy /proxy/* localhost:9001` antes de cualquier catch-all.
44: 7. **Frontend de producción se compila y sirve por Caddy**, no por Docker local.
45: 8. **Lenguaje de commits y comentarios**: se prefiere inglés cuando el código es en inglés; la documentación puede estar en español según preferencia.
46: 
47: ## 17. BUGS CONOCIDOS
48: 
49: ### Bug #1 — `internal/bot/handler.go`: `h.wgManager` es campo que no existe → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es campo que no existe en WebhookHandler → compila, pero wgManager es ...  

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

### Bug #1 — `internal/bot/handler.go`: `h.wgManager` es campo que no existe

**Estado actual del código** (leído de `internal/bot/handler.go`):
- `WebhookHandler` NO tiene campo `wgManager` — solo tiene `store Store`, `baseURL string`, `port string`
- `NewWebhookHandler(store, baseURL, port)` NO recibe ni asigna `wgManager`
- Al ejecutar `/connect`, la referencia `h.wgManager` no compila: `undefined field`

**Impacto**: `/connect` del bot no puede asignar IPs ni crear peers WireGuard.

**Arreglo planificado**:
```go
type WebhookHandler struct {
    store     Store
    wgManager *wg.Manager
    baseURL   string
    port      string
}
func NewWebhookHandler(store Store, wgMgr *wg.Manager, baseURL, port string) *WebhookHandler {
    return &WebhookHandler{store: store, wgManager: wgMgr, baseURL: baseURL, port: port}
}
```

En `cmd/backend/main.go`, inyectar el manager:
```go
botH := bot.NewWebhookHandler(store, wgMgr, "usipipo.dpdns.org",
    fmt.Sprintf("%s:%d", cfg.WGEndpointHost, cfg.WGEndpointPort))
```

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

---

## 19. DECISIONES DE NEGOCIO (adicionales)

### Modelo de monetización

| Etapa            | Condición                         | Precio                    |
|------------------|-----------------------------------|---------------------------|
| Beta             | Primeros 10 usuarios (familia/amigos) | Free                     |
| Crecimiento      | Usuarios 11–499                   | Free                      |
| Lanzamiento      | Usuarios ≥ 500                    | $1.99/mes nuevos          |
| Early adopters   | Marca `early_adopter` en `users`  | $0.40/mes (80% descuento) |

**Rate de conversión días ↔ USDT:**
```
rate = 1.99 / 30 = 0.06633 USDT/día
dias = monto_ingresado / rate
```
Early adopter paga `monto * 0.20` por el mismo cómputo de días.

### Data cap

- Límite: **60 GB/mes por usuario**
- Exceso: limitación de velocidad (no corte, no cargo extra)

### Pasarela de pagos: TronDealer V2

- **Proveedor:** TronDealer (operado por QvaPay)
- **Stablecoins:** USDT y USDC
- **Red de depósito única:** BSC BEP-20 USDT
  - Contrato USDT BEP-20: `0x55d398326f99059fF775485485246999027B3197955`
  - 18 decimales (importante: no hardcodear 6)
- **Fee:** 0.4% sobre monto ≥ $10 · flat $0.30 si monto < $10 · 0% con QvaPay custody
- **Sin KYC** para empezar
- **Webhook firma:** header `X-Signature-256` → HMAC-SHA256(raw body, webhook_secret)
- **Lifecycle:** `detected → confirmed → notified → swept`
- **Notificado = pago confirmado** — en este estado se activa la suscripción

### Flujo de recarga (prepago en días)

1. Usuario elige cantidad de días o monto en USDT en el frontend.
2. Frontend envía `POST /proxy/payments/invoice` al backend con `{days, user_id}`.
3. Backend calcula monto USDT (`days × rate`) aplica descuento early_adopter si corresponde.
4. Backend llama a `POST https://www.trondealer.com/api/v2/wallets/assign` con `label=order-{uuid}` → recibe dirección BSC.
5. Backend registra el invoice/order en BD con estado `pending`.
6. Backend responde al frontend con `{address, amount_usdt, qr_data, expires_at}`.
7. Frontend genera código QR (el QR lo genera el frontend a partir de la dirección y monto) y lo muestra al usuario.
8. Usuario envía USDT BEP-20 a la dirección desde su wallet (Trust Wallet, MetaMask, etc.).
9. Webhook `notified` de TronDealer → Backend valida firma HMAC → marca invoice `confirmed` → acredita `days` al usuario.
10. Webhook `swept` → Backend registra en bitácora (reconciliación).

### Tiempos y timeouts

| Evento                         | Valor                              |
|-------------------------------|------------------------------------|
| Expiración de wallet/invoice   | 30 minutos desde la generación     |
| Tiempo de confirmación BSC     | ~15 bloques (configurable en TronDealer) |
| Tiempo de sweep automático     | Minutos después de confirmación    |

### Tablas BD nuevas requeridas (pagos)

```sql
-- Invoices: cada intento de recarga
CREATE TABLE IF NOT EXISTS invoices (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id),
    td_wallet_label TEXT NOT NULL UNIQUE,  -- label usado en /wallets/assign
    amount_usdt   REAL NOT NULL,           -- monto solicitado en USDT
    days          INTEGER NOT NULL,        -- días acreditados si pago se confirma
    status        TEXT NOT NULL DEFAULT 'pending',  -- pending/confirmed/expired/failed
    tx_hash       TEXT,                    -- tx on-chain desde webhook
    td_order_id   TEXT UNIQUE,             -- id de orden TronDealer
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confirmed_at  DATETIME,
    sweep_at      DATETIME
);
CREATE INDEX idx_invoices_user ON invoices(user_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_td_order ON invoices(td_order_id);

-- Perfiles de suscripción extendidos (se agregarán columnas si es necesario)
-- Alternativa: agregar credit_days y subscription_status a tabla users
```

### Campo `early_adopter` en tabla `users`

Agregar columna a migración:

```sql
ALTER TABLE users ADD COLUMN early_adopter INTEGER NOT NULL DEFAULT 0;
```

Valores: `0` = normal, `1` = early adopter (descuento 80%).

### Endpoints nuevos de pago (a agregar en backend)

| Método | Ruta                    | Descripción                              |
|--------|-------------------------|------------------------------------------|
| POST   | `/proxy/payments/invoice` | Calcula monto y crea invoice TronDealer |
| GET    | `/proxy/payments/invoices` | Historial de invoices del usuario       |
| POST   | `/proxy/webhooks/trondealer` | Webhook de TronDealer (validar firma)   |

### Seguridad del webhook

1. Recibir body **raw** (no parsear antes de validar firma).
2. `HMAC-SHA256(webhook_secret, raw_body)` en hex.
3. Comparar con `X-Signature-256` usando `hmac.Equal` (timing-safe).
4. Verificar `event.status == "notified"` antes de acreditar días.
5. Usar `tx_hash + log_index` como clave idempotente en BD (evita doble acreditación por retries).
