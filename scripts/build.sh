#!/bin/bash
# ─── uSipipo Proxy – Build desde Docker ──────────────────────────────────────
# Uso: ./scripts/build.sh [--push]
# Compila el backend Go usando golang:latest, sin Go instalado localmente.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
IMAGE="golang:1.24-alpine"
TAG="${TAG:-dev}"
DOCKERFILE="$REPO_ROOT/docker/backend.Dockerfile"

echo "══ uSipipo backend build — tag=$TAG ═══════════════════════════════════"

# ── 1. go mod download + go vet ─────────────────────────────────────────────
docker run --rm \
  -v "$REPO_ROOT":/app \
  -w /app \
  "$IMAGE" \
  sh -c "
    apk add --no-cache git build-base && \
    echo '→ go mod download' && \
    go mod download && \
    echo '→ go vet' && \
    go vet ./...
  "

echo "✓ go mod download + go vet OK"

# ── 2. go build ─────────────────────────────────────────────────────────────
docker run --rm \
  -v "$REPO_ROOT":/app \
  -w /app \
  -e CGO_ENABLED=1 \
  -e GOOS=linux \
  -e GOARCH=amd64 \
  -e LD_FLAGS='-s -w -X main.version='$TAG \
  "$IMAGE" \
  sh -c "
    apk add --no-cache git build-base && \
    echo '→ compilando backend...' && \
    go build -ldflags \"-s -w -X main.version=$TAG\" \
      -o /app/bin/backend ./cmd/backend && \
    echo '→ build OK' && \
    ls -lh /app/bin/backend
  "

echo "✓ binario en $REPO_ROOT/bin/backend"

# ── 3. (opcional) compilar frontend ──────────────────────────────────────────
if command -v npm &>/dev/null; then
  echo "→ compilando frontend..."
  cd "$REPO_ROOT/frontend"
  npm ci 2>/dev/null || npm install
  npx vite build
  echo "✓ frontend build OK"
else
  echo "⚠ npm no encontrado — salta frontend build"
fi

echo "══ build completo ═══════════════════════════════════════════════════════"
