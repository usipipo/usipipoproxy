package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/usipipo/usipipoproxy/internal/http/middleware"
	"github.com/usipipo/usipipoproxy/pkg/models"
)

var writeError = func(w http.ResponseWriter, code int, msg string) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.WriteHeader(code)
	_, _ = fmt.Fprintf(w, `{"error":"%s"}`, msg)
}

var writeJSON = func(w http.ResponseWriter, code int, v any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(v)
}

var writeMethodNotAllowed = func(w http.ResponseWriter) {
	http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
}

// userFromCtx extrae el usuario del contexto (inyectado por middleware.AuthMiddleware).
func userFromCtx(r *http.Request) (*models.User, bool) {
	return middleware.UserFromCtx(r.Context())
}

// userIDFromCtx extrae el ID numerico del usuario autenticado.
func userIDFromCtx(r *http.Request) (int64, bool) {
	u, ok := userFromCtx(r)
	if !ok || u == nil {
		return 0, false
	}
	return u.ID, true
}

// deviceResponseFrom convierte una entidad Device (BD) a DeviceResponse (DTO API).
// Es el unico punto de construccion de DeviceResponse.
func deviceResponseFrom(d *models.Device) models.DeviceResponse {
	return models.DeviceResponse{
		ID: d.ID, UserID: d.UserID, Name: d.Name,
		PublicKey: d.PublicKey, AssignedIP: d.AssignedIP, PSK: d.PSK,
		Enabled: d.Enabled,
		BytesRx: d.BytesRx, BytesTx: d.BytesTx,
		CreatedAt: d.CreatedAt, LastSeenAt: d.LastSeenAt,
	}
}

// PaymentEvent representa un evento de webhook encolado para procesamiento asincrono.
type PaymentEvent struct {
	InvoiceID string
	Type      string
	TXHash    string
	Label     string
}

// PaymentQueue es el canal de eventos para procesamiento asincrono de webhooks.
type PaymentQueue chan PaymentEvent
