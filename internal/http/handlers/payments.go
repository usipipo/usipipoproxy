package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log/slog"
	"math"
	"net/http"
	"strings"
	"time"

	"github.com/usipipo/usipipoproxy/pkg/models"
)

// PaymentStore extiende DeviceStore con todo lo necesario para pagos.
type PaymentStore interface {
	DeviceStore
	CreateInvoice(inv *models.Invoice) error
	GetInvoiceByID(id string) (*models.Invoice, error)
	GetInvoiceByAddress(addr string) (*models.Invoice, error)
	GetInvoiceByLabel(label string) (*models.Invoice, error)
	UpdateInvoiceStatus(id, status string) error
	UpdateInvoiceConfirmation(id string, confirmedAt time.Time) error
	UpdateUserSubscriptionEndsAt(userID int64, endsAt time.Time) error
	GetUserByID(uid int64) (*models.User, error)
	CreateWebhookEvent(evt *models.WebhookEvent) error
	ListInvoices(userID int64) ([]models.Invoice, error)
}

const paymentRateUSDTPerDay = 0.06633 // $1.99 / 30 dias
const invoiceExpiryMinutes = 30

// PaymentHandlers maneja los endpoints de pagos TronDealer.
type PaymentHandlers struct {
	store      PaymentStore
	tdAPIKey   string
	tdSecret   string
	tdBaseURL  string
	eventQueue PaymentQueue
}

func NewPaymentHandlers(store PaymentStore, tdAPIKey, tdSecret, tdBaseURL string, queue PaymentQueue) *PaymentHandlers {
	if queue == nil {
		queue = make(chan PaymentEvent, 256)
	}
	return &PaymentHandlers{
		store:      store,
		tdAPIKey:   tdAPIKey,
		tdSecret:   tdSecret,
		tdBaseURL:  tdBaseURL,
		eventQueue: queue,
	}
}

// calculateDays calcula dias de suscripcion a partir de un monto USDT.
// Si el usuario es early adopter, aplica 20% del precio (descuento 80%).
func (h *PaymentHandlers) calculateDays(user *models.User, amountUSDT float64) int {
	effectiveRate := paymentRateUSDTPerDay
	if user.EarlyAdopter {
		effectiveRate = paymentRateUSDTPerDay * 0.20
	}
	days := int(math.Floor(amountUSDT / effectiveRate))
	if days < 1 {
		days = 1
	}
	return days
}

// Router despacha los endpoints de pagos.
func (h *PaymentHandlers) Router(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodPost:
		if strings.HasSuffix(r.URL.Path, "/invoice") {
			h.CreateInvoice(w, r)
			return
		}
		writeMethodNotAllowed(w)
	case http.MethodGet:
		if strings.HasSuffix(r.URL.Path, "/invoices") || r.URL.Path == "/proxy/payments/invoices" {
			h.ListInvoices(w, r)
			return
		}
		writeMethodNotAllowed(w)
	default:
		writeMethodNotAllowed(w)
	}
}

// POST /proxy/payments/invoice — crea una invoice TronDealer.
func (h *PaymentHandlers) CreateInvoice(w http.ResponseWriter, r *http.Request) {
	uid, ok := userIDFromCtx(r)
	if !ok {
		writeError(w, http.StatusUnauthorized, "unauthenticated")
		return
	}
	if h.tdAPIKey == "" {
		writeError(w, http.StatusInternalServerError, "TronDealer API key not configured")
		return
	}

	var req models.CreateInvoiceRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid body")
		return
	}
	if req.Days < 1 || req.Days > 365 {
		writeError(w, http.StatusBadRequest, "days must be between 1 and 365")
		return
	}

	user, err := h.store.GetUserByID(uid)
	if err != nil {
		slog.Error("get user for invoice", "uid", uid, "err", err)
		writeError(w, http.StatusInternalServerError, "user lookup failed")
		return
	}

	// Calcular monto en USDT
	amount := float64(req.Days) * paymentRateUSDTPerDay
	if user.EarlyAdopter {
		amount *= 0.20
	}

	// Generar UUID v4 como invoice_id
	invoiceUUID := genUUIDv4()
	label := "order-" + invoiceUUID

	// Llamar a TronDealer /wallets/assign
	tdResp, err := h.callTronDealerAssignWallet(label)
	if err != nil {
		slog.Error("trondealer assign wallet", "label", label, "err", err)
		writeError(w, http.StatusBadGateway, "payment gateway error")
		return
	}

	addr := tdResp.Address
	if addr == "" {
		writeError(w, http.StatusInternalServerError, "empty address from TronDealer")
		return
	}

	expiresAt := time.Now().UTC().Add(invoiceExpiryMinutes * time.Minute)

	inv := &models.Invoice{
		ID:            invoiceUUID,
		UserID:        uid,
		TDWalletLabel: label,
		TDWalletAddr:  addr,
		AmountUSDT:    amount,
		Days:          req.Days,
		Status:        models.InvoiceStatusPending,
		ExpiresAt:     expiresAt,
		CreatedAt:     time.Now().UTC(),
	}

	if err := h.store.CreateInvoice(inv); err != nil {
		slog.Error("create invoice in db", "uuid", invoiceUUID, "err", err)
		writeError(w, http.StatusInternalServerError, "failed to create invoice")
		return
	}

	// Generar QR data URI (formato BIP-21 para BSC)
	qrData := fmt.Sprintf("bip21:%s?amount=%.6f", addr, amount)

	slog.Info("invoice created",
		"uuid", invoiceUUID, "uid", uid, "amount", amount, "days", req.Days, "addr", addr)

	writeJSON(w, http.StatusCreated, models.CreateInvoiceResponse{
		InvoiceUUID: invoiceUUID,
		Address:     addr,
		AmountUSDT:  amount,
		QRData:      qrData,
		ExpiresAt:   expiresAt,
		Days:        req.Days,
	})
}

// GET /proxy/payments/invoices — historial del usuario autenticado.
func (h *PaymentHandlers) ListInvoices(w http.ResponseWriter, r *http.Request) {
	uid, ok := userIDFromCtx(r)
	if !ok {
		writeError(w, http.StatusUnauthorized, "unauthenticated")
		return
	}
	invoices, err := h.store.ListInvoices(uid)
	if err != nil {
		slog.Error("list invoices", "uid", uid, "err", err)
		writeError(w, http.StatusInternalServerError, "failed to list invoices")
		return
	}
	if invoices == nil {
		invoices = []models.Invoice{}
	}
	writeJSON(w, http.StatusOK, invoices)
}

// tronDealerAssignWalletResp es la respuesta de /wallets/assign.
type tronDealerAssignWalletResp struct {
	Address string `json:"address"`
}

// callTronDealerAssignWallet POST a /api/v2/wallets/assign.
func (h *PaymentHandlers) callTronDealerAssignWallet(label string) (*tronDealerAssignWalletResp, error) {
	url := h.tdBaseURL + "/api/v2/wallets/assign"
	body, _ := json.Marshal(map[string]string{"label": label})

	req, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("new request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-api-key", h.tdAPIKey)

	client := &http.Client{Timeout: 15 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("http do: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("td status %d", resp.StatusCode)
	}

	var tdResp tronDealerAssignWalletResp
	if err := json.NewDecoder(resp.Body).Decode(&tdResp); err != nil {
		return nil, fmt.Errorf("decode td response: %w", err)
	}
	return &tdResp, nil
}
