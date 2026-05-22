package models

import "time"

// Device es un dispositivo WireGuard (cliente VPN), vinculado a un usuario.
type Device struct {
	ID          int64     `json:"id"`
	UserID      int64     `json:"user_id"`
	Name        string    `json:"name"`
	PublicKey   string    `json:"public_key"`
	AssignedIP  string    `json:"assigned_ip"`
	PSK         string    `json:"psk,omitempty"`
	Enabled     bool      `json:"enabled"`
	Conf        ClientConfig `json:"conf,omitempty"` // configuración de cliente WG
	BytesRx     uint64    `json:"bytes_rx,omitempty"`
	BytesTx     uint64    `json:"bytes_tx,omitempty"`
	CreatedAt   time.Time `json:"created_at"`
	LastSeenAt  *time.Time `json:"last_seen_at,omitempty"`
}

// ClientConfig es el archivo de configuración WireGuard listo para el cliente.
type ClientConfig struct {
	PrivateKey string
	Address    string
	DNS        string
	PublicKey  string
	Endpoint   string
	AllowedIPs string
	PSK        string
}

// User es una cuenta de usuario autorizado por telegram_id.
type User struct {
	ID         int64     `json:"id"`
	TelegramID int64     `json:"telegram_id"`
	Username   string    `json:"username,omitempty"`
	FirstName  string    `json:"first_name,omitempty"`
	Role       string    `json:"role"`
	CreatedAt  time.Time `json:"created_at"`
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
