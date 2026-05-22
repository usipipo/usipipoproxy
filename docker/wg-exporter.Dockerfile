# ── uSipipo Proxy – WireGuard Stats Exporter ────────────────────────────────
FROM golang:1.24-alpine AS builder
RUN apk add --no-cache git build-base
WORKDIR /src
COPY cmd/exporter/go.mod cmd/exporter/go.sum ./
RUN go mod download
COPY cmd/exporter .
RUN CGO_ENABLED=1 GOOS=linux GOARCH=amd64 go build -o /out/exporter ./...

FROM alpine:3.21
RUN apk add --no-cache ca-certificates curl tini
COPY --from=builder /out/exporter /usr/local/bin/wg-exporter
EXPOSE 9100
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["wg-exporter"]
