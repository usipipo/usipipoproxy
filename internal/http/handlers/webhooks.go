package handlers

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"io"
	"log/slog"
	"net/http"
	"time"

	"github.com/usipipo/usipipoproxy/pkg/models"
)

// TronDealerWebhookHandler procesa el webhook de TronDealer.
type TronDealerWebhookHandler struct {
	store      PaymentStore
	secret     string
	eventQueue PaymentQueue
}

func NewTronDealerWebhookHandler(store PaymentStore, secret string, queue PaymentQueue) *TronDealerWebhookHandler {
	if queue == nil {
		queue = make(chan PaymentEvent, 256)
	}
	return &TronDealerWebhookHandler{store: store, secret: secret, eventQueue: queue}
}

// Handler es el endpoint HTTP del webhook.
// 1. Valida firma HMAC sobre body raw.
// 2. Deserializa webhook.
// 3. Persiste evento en BD.
// 4. Encola para procesamiento asincrono.
// 5. Responde 200 inmediatamente.
func (h *TronDealerWebhookHandler) Handler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeMethodNotAllowed(w)
		return
	}

	// Leer body crudo antes de cualquier parseo
	rawBody, err := readHTTPBody(r)
	if err != nil {
		slog.Warn("webhook read body", "err", err)
		writeError(w, http.StatusBadRequest, "bad body")
		return
	}

	// Validar firma HMAC
	sig := r.Header.Get("X-Signature-256")
	if !validateTDSignature(rawBody, sig, h.secret) {
		slog.Warn("webhook invalid signature")
		writeError(w, http.StatusUnauthorized, "invalid signature")
		return
	}

	// Deserializar webhook
	var evt models.TronDealerWebhook
	if err := json.Unmarshal(rawBody, &evt); err != nil {
		slog.Warn("webhook unmarshal", "err", err)
		writeError(w, http.StatusBadRequest, "bad json")
		return
	}

	// Buscar invoice por direccion BSC
	invoice, err := h.store.GetInvoiceByAddress(evt.ToAddress)
	if err != nil {
		// No es un error fatal — puede ser una invoice fuera de nuestro dominio
		slog.Warn("webhook address not found in invoices", "addr", evt.ToAddress)
	}
	if invoice != nil {
		// Persistir raw body para auditoria
		_ = h.store.CreateWebhookEvent(&models.WebhookEvent{
			InvoiceID:  invoice.ID,
			EventType:  evt.Event,
			RawBody:    string(rawBody),
			ReceivedAt: time.Now().UTC(),
		})

		// Encolar evento para worker asincrono
		eventType := evt.Event
		select {
		case h.eventQueue <- PaymentEvent{
			InvoiceID: invoice.ID,
			Type:      eventType,
			TXHash:    evt.TXHash,
			Label:     evt.Label,
		}:
		default:
			slog.Warn("webhook event queue full, dropping", "invoice", invoice.ID)
		}
	}

	slog.Info("webhook received",
		"event", evt.Event, "label", evt.Label, "addr", evt.ToAddress,
		"amount", evt.Amount, "tx", evt.TXHash)
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte("ok"))
}

// readHTTPBody lee el cuerpo de la request completa en bytes.
func readHTTPBody(r *http.Request) ([]byte, error) {
	defer r.Body.Close()
	return io.ReadAll(r.Body)
}

// validateTDSignature verifica X-Signature-256 = HMAC-SHA256(secret, rawBody).
func validateTDSignature(rawBody []byte, signature, secret string) bool {
	if secret == "" || signature == "" {
		return false
	}
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write(rawBody)
	expected := hex.EncodeToString(mac.Sum(nil))
	return hmac.Equal([]byte(signature), []byte(expected))
}

// StartPaymentWorker arranca la goroutine que consume events de pago.
func StartPaymentWorker(h *PaymentHandlers, queue PaymentQueue) {
	go func() {
		for evt := range queue {
			h.processPaymentEvent(evt)
		}
	}()
}

func (h *PaymentHandlers) processPaymentEvent(evt PaymentEvent) {
	defer func() {
		if r := recover(); r != nil {
			slog.Error("payment event panic", "invoice", evt.InvoiceID, "panic", r)
		}
	}()

	switch evt.Type {
	case models.TDEventNotified:
		h.processNotified(evt)
	case models.TDEventSwept:
		h.processSwept(evt)
	case models.TDEventExpired:
		h.processExpired(evt)
	default:
		slog.Warn("unknown payment event", "type", evt.Type, "invoice", evt.InvoiceID)
	}
}

func (h *PaymentHandlers) processNotified(evt PaymentEvent) {
	inv, err := h.store.GetInvoiceByID(evt.InvoiceID)
	if err != nil {
		slog.Error("notified: invoice not found", "id", evt.InvoiceID, "err", err)
		return
	}
	if inv.Status != models.InvoiceStatusPending {
		slog.Info("notified: invoice already processed", "id", evt.InvoiceID, "status", inv.Status)
		return
	}

	now := time.Now().UTC()

	user, err := h.store.GetUserByID(inv.UserID)
	if err != nil {
		slog.Error("notified: user not found", "uid", inv.UserID, "err", err)
		return
	}

	// Calcular nueva fecha de expiracion de suscripcion
	newEndsAt := now.AddDate(0, 0, inv.Days)
	if user.SubscriptionEndsAt != nil && user.SubscriptionEndsAt.After(now) {
		newEndsAt = user.SubscriptionEndsAt.AddDate(0, 0, inv.Days)
	}

	if err := h.store.UpdateUserSubscriptionEndsAt(inv.UserID, newEndsAt); err != nil {
		slog.Error("notified: update subscription", "uid", inv.UserID, "err", err)
		return
	}

	if err := h.store.UpdateInvoiceConfirmation(inv.ID, now); err != nil {
		slog.Error("notified: update invoice", "id", inv.ID, "err", err)
		return
	}

	slog.Info("subscription extended",
		"uid", inv.UserID, "invoice", inv.ID, "days", inv.Days, "ends_at", newEndsAt.Format(time.RFC3339))
}

func (h *PaymentHandlers) processSwept(evt PaymentEvent) {
	slog.Info("sweep received",
		"invoice", evt.InvoiceID, "tx", evt.TXHash, "label", evt.Label)
}

func (h *PaymentHandlers) processExpired(evt PaymentEvent) {
	inv, err := h.store.GetInvoiceByID(evt.InvoiceID)
	if err != nil {
		slog.Warn("expired: invoice not found", "id", evt.InvoiceID)
		return
	}
	if inv.Status == models.InvoiceStatusPending {
		if err := h.store.UpdateInvoiceStatus(inv.ID, models.InvoiceStatusExpired); err != nil {
			slog.Error("expired: update", "id", inv.ID, "err", err)
		}
		slog.Info("invoice expired", "id", inv.ID, "label", inv.TDWalletLabel)
	}
}
