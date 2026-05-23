package models

import (
	"time"

	"github.com/usipipo/usipipoproxy/internal/wg"
)

// Device es un dispositivo WireGuard (cliente VPN), vinculado a un usuario.
// Es una entidad de BD pura: no contiene configuración de cliente ni claves privadas.
type Device struct {
	ID         int64      `json:"id"`
	UserID     int64      `json:"user_id"`
	Name       string     `json:"name"`
	PublicKey  string     `json:"public_key"`
	PrivateKey string     `json:"-"`
	AssignedIP string     `json:"assigned_ip"`
	PSK        string     `json:"psk,omitempty"`
	Enabled    bool       `json:"enabled"`
	BytesRx    uint64     `json:"bytes_rx,omitempty"`
	BytesTx    uint64     `json:"bytes_tx,omitempty"`
	CreatedAt  time.Time  `json:"created_at"`
	LastSeenAt *time.Time `json:"last_seen_at,omitempty"`
}

// ---------------------------------------------------------------------------
// DTOs de API — Device responses (sin campos privados de BD ni de WG)
// ---------------------------------------------------------------------------

// DeviceResponse es lo que expone GET /proxy/devices (sin configuración de cliente).
type DeviceResponse struct {
	ID         int64      `json:"id"`
	UserID     int64      `json:"user_id"`
	Name       string     `json:"name"`
	PublicKey  string     `json:"public_key"`
	AssignedIP string     `json:"assigned_ip"`
	PSK        string     `json:"psk,omitempty"`
	Enabled    bool       `json:"enabled"`
	BytesRx    uint64     `json:"bytes_rx,omitempty"`
	BytesTx    uint64     `json:"bytes_tx,omitempty"`
	CreatedAt  time.Time  `json:"created_at"`
	LastSeenAt *time.Time `json:"last_seen_at,omitempty"`
}

// CreateDeviceResponse es la respuesta de POST /proxy/devices (incluye ClientConfig con clave privada).
type CreateDeviceResponse struct {
	Device DeviceResponse  `json:"device"`
	Conf   wg.ClientConfig `json:"conf"`
}

// User es una cuenta de usuario autorizado por telegram_id.
type User struct {
	ID                 int64      `json:"id"`
	TelegramID         int64      `json:"telegram_id"`
	Username           string     `json:"username,omitempty"`
	FirstName          string     `json:"first_name,omitempty"`
	Role               string     `json:"role"`
	CreatedAt          time.Time  `json:"created_at"`
	SubscriptionEndsAt *time.Time `json:"subscription_ends_at,omitempty"`
	EarlyAdopter       bool       `json:"early_adopter"`
}

// TrafficSample es una muestra de tráfico capturada del exporter.
type TrafficSample struct {
	DeviceID  int64     `json:"device_id"`
	BytesRx   uint64    `json:"bytes_rx"`
	BytesTx   uint64    `json:"bytes_tx"`
	Timestamp time.Time `json:"timestamp"`
}

// TrafficSummary es el agregado de consumo por dispositivo y periodo.
type TrafficSummary struct {
	DeviceID  int64   `json:"device_id"`
	Period    string  `json:"period"` // daily | weekly | monthly
	TotalRxGB float64 `json:"total_rx_gb"`
	TotalTxGB float64 `json:"total_tx_gb"`
	TotalGB   float64 `json:"total_gb"`
}

// TelegramUser es el DTO recibido desde el webhook/login de Telegram.
type TelegramUser struct {
	ID        int64  `json:"id"`
	Username  string `json:"username,omitempty"`
	FirstName string `json:"first_name"`
	LastName  string `json:"last_name,omitempty"`
}

// AuthResponse es la respuesta del endpoint de login.
type AuthResponse struct {
	Token     string `json:"token"`
	User      User   `json:"user"`
	ExpiresAt int64  `json:"expires_at"`
}

// ---------------------------------------------------------------------------
// Payment / TronDealer types
// ---------------------------------------------------------------------------

// InvoiceStatus values for the invoices table.
const (
	InvoiceStatusPending   = "pending"
	InvoiceStatusConfirmed = "confirmed"
	InvoiceStatusExpired   = "expired"
	InvoiceStatusFailed    = "failed"
	InvoiceStatusPartial   = "partial"
)

// TronDealerEvent values emitted by the TronDealer webhook.
const (
	TDEventNotified = "payment.notified"
	TDEventSwept    = "payment.swept"
	TDEventExpired  = "wallet.expired"
)

// Invoice representa una Invoice generada para el pago con TronDealer.
type Invoice struct {
	ID             string     `json:"id"`
	UserID         int64      `json:"user_id"`
	TDWalletLabel  string     `json:"td_wallet_label"`
	TDWalletAddr   string     `json:"td_wallet_addr"`
	AmountUSDT     float64    `json:"amount_usdt"`
	Days           int        `json:"days"`
	Status         string     `json:"status"`
	TDOrderID      *string    `json:"td_order_id,omitempty"`
	ExpiresAt      time.Time  `json:"expires_at"`
	ConfirmedAt    *time.Time `json:"confirmed_at,omitempty"`
	SweptAt        *time.Time `json:"swept_at,omitempty"`
	RawWebhookBody string     `json:"-"`
	CreatedAt      time.Time  `json:"created_at"`
}

// TronDealerWebhook es el DTO recibido desde el webhook de TronDealer.
type TronDealerWebhook struct {
	Event         string     `json:"event"`
	Label         string     `json:"label"`
	ToAddress     string     `json:"to_address"`
	Amount        float64    `json:"amount"`
	Asset         string     `json:"asset"`
	Network       string     `json:"network"`
	TXHash        string     `json:"tx_hash"`
	Confirmations int        `json:"confirmations"`
	ReceivedAt    *time.Time `json:"received_at,omitempty"`
}

// CreateInvoiceRequest es enviado por el frontend al pedir una invoice.
type CreateInvoiceRequest struct {
	Days int `json:"days"`
}

// CreateInvoiceResponse es la respuesta al crear una invoice.
type CreateInvoiceResponse struct {
	InvoiceUUID string    `json:"invoice_uuid"`
	Address     string    `json:"address"`
	AmountUSDT  float64   `json:"amount_usdt"`
	QRData      string    `json:"qr_data"`
	ExpiresAt   time.Time `json:"expires_at"`
	Days        int       `json:"days"`
}

// WebhookEvent registra cada evento de webhook recibido para auditoría.
type WebhookEvent struct {
	ID         int64     `json:"id"`
	InvoiceID  string    `json:"invoice_id"`
	EventType  string    `json:"event_type"`
	TDTxHash   *string   `json:"td_tx_hash,omitempty"`
	RawBody    string    `json:"raw_body"`
	Processed  bool      `json:"processed"`
	ReceivedAt time.Time `json:"received_at"`
}
