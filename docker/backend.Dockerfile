# ── uSipipo Proxy – Backend Go ──────────────────────────────────────────────
# Multi-stage Dockerfile, imagen final ~15 MB

ARG GO_VERSION=1.24
ARG ALPINE_VERSION=3.21
ARG TARGETPLATFORM

# ── Builder ──────────────────────────────────────────────────────────────────
FROM golang:${GO_VERSION}-alpine${ALPINE_VERSION} AS builder
RUN apk add --no-cache git ca-certificates build-base

WORKDIR /app

# Cache de dependencias
COPY go.mod go.sum ./
RUN go mod download

# Compilar
COPY . .
RUN CGO_ENABLED=1 GOOS=linux GOARCH=$(echo $TARGETPLATFORM | sed 's/linux\///') go build \
    -ldflags "-s -w -X main.version=${TAG:-dev}" \
    -o /out/backend ./cmd/backend
# ── Runner ──────────────────────────────────────────────────────────────────
FROM alpine:${ALPINE_VERSION}
RUN apk add --no-cache ca-certificates curl tini

WORKDIR /app

# Binarios + runtime + skins
COPY --from=builder /out/backend /usr/local/bin/backend
COPY --from=builder /app/migrations ./migrations
COPY --from=builder /app/pkg ./pkg
COPY --from=builder /app/internal ./internal

# Writable
VOLUME ["/app/data"]

ENV DB_PATH=/app/data/usipipo.db \
    API_PORT=8001

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=5 \
    CMD ["wget", "--spider", "-q", "http://localhost:${API_PORT}/health"]

USER nobody:nobody
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["backend"]
