package bot

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"strings"
	"time"

	"github.com/usipipo/usipipoproxy/pkg/models"
)

// JWT validation via middleware
type ctxKey int
const botUserKey ctxKey = 1

// Store interface reutiliza la de db.
type Store interface {
	GetOrCreateUser(u *models.TelegramUser) (*models.User, error)
	CreateDevice(userID int64, name, pubKey, ipAddr, psk string) (*models.Device, error)
	ListDevices(userID int64) ([]models.Device, error)
	GetDeviceByID(deviceID int64) (*models.Device, error)
}

// WebhookHandler procesa mensajes del bot de Telegram.
type WebhookHandler struct {
	store   Store
	baseURL string // "usipipo.dpdns.org"
	port    string // puerto WireGuard
}

func NewWebhookHandler(store Store, baseURL, port string) *WebhookHandler {
	return &WebhookHandler{store: store, baseURL: baseURL, port: port}
}

// WebhookPayload — estructura recibida desde el webhook de Telegram.
type WebhookPayload struct {
	UpdateID int64      `json:"update_id"`
	Message  TgMessage  `json:"message"`
}

type TgMessage struct {
	MessageID   int64             `json:"message_id"`
	From        *models.TelegramUser  `json:"from"`
	Chat        TgChat            `json:"chat"`
	Text        string            `json:"text"`
	Date        int64             `json:"date"`
}

type TgChat struct {
	ID   int64  `json:"id"`
	Type string `json:"type"`
}

// Dispatch procesa un comando y devuelve la respuesta al usuario.
func (h *WebhookHandler) Dispatch(p *WebhookPayload) string {
	if p.Message == nil || p.Message.Text == "" || p.Message.From == nil {
		return ""
	}

	cmd := strings.TrimSpace(p.Message.Text)
	from := p.Message.From

	switch cmd {
	case "/start":
		user, err := h.store.GetOrCreateUser(from)
		if err != nil {
			slog.Error("get or create user", "err", err, "tg_id", from.ID)
			return "Error al crear tu cuenta. Intenta nuevamente."
		}
		return fmt.Sprintf("Bienvenido a uSipipo Proxy, %s!\nUsa /status para ver tus dispositivos, /connect para conectar o /help para ayuda.",
			user.FirstName)

	case "/status", "/devices":
		user, err := h.store.GetOrCreateUser(from)
		if err != nil { break }
		devices, err := h.store.ListDevices(user.ID)
		if err != nil { break }
		if len(devices) == 0 {
			return "No tienes dispositivos. Usa /connect para crear el primero."
		}
		var sb strings.Builder
		sb.WriteString(fmt.Sprintf("Tus dispositivos (%d):\n\n", len(devices)))
		for _, d := range devices {
			rx := float64(d.Rx) / (1024 * 1024 * 1024)
			tx := float64(d.Tx) / (1024 * 1024 * 1024)
			status := "activo"
			if !d.Enabled { status = "revocado" }
			fmt.Fprintf(&sb, "  %s\n   IP: %s | RX: %.2f GB | TX: %.2f GB | %s\n",
				d.Name, d.AssignedIP, rx, tx, status)
		}
		return sb.String()

	case "/connect":
		user, err := h.store.GetOrCreateUser(from)
		if err != nil { break }

		// Crear dispositivo por defecto
		name := fmt.Sprintf("device-%d", time.Now().Unix()%100000)
		pubKey, privKey, err := wg.GenerateKeyPair()
		if err != nil {
			return "Error al generar claves. Intenta /connect más tarde."
		}

		// Asignar IP
		taken, _ := h.store.GetAllAssignedIPs()
		freeIP, err := h.wgManager.NextFreeIP(taken)
		if err != nil {
			return "Sin IPs disponibles. Contacta al administrador."
		}

		device, err := h.store.CreateDevice(user.ID, name, pubKey, freeIP.String(), "")
		if err != nil {
			return "Error al registrar dispositivo. Intenta más tarde."
		}

		_ = privKey // se entrega por /app o end-to-end
		return fmt.Sprintf("Dispositivo creado: %s\nIP: %s\nEndpoint: %s\nEntra a usipipo.dpdns.org/proxy/app para obtener el archivo .conf",
			name, freeIP.String(), baseUrl())

	case "/help":
		return "Comandos:\n" +
			"  /start   — iniciar sesión\n" +
			"  /status  — ver tus dispositivos y consumo\n" +
			"  /connect — crear un nuevo dispositivo VPN\n" +
			"  /help    — esta ayuda"

	default:
		return "Comandos: /start · /status · /connect · /help"
	}
}

func baseUrl() string {
	return "usipipo.dpdns.org"
}

// Handler implementa http.Handler para el webhook.
func (h *WebhookHandler) Handler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var payload WebhookPayload
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		slog.Warn("bot webhook bad body", "err", err)
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}

	reply := h.Dispatch(&payload)
	if reply != "" {
		slog.Info("bot reply queued",
			"chat_id", payload.Message.Chat.ID, "reply_len", len(reply),
			"reply_preview", reply[:min(60, len(reply))])
	}

	writeJSON(w, http.StatusOK, map[string]string{"ok": "true"})
}

func writeJSON(w http.ResponseWriter, code int, v any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(v)
}

func min(a, b int) int { if a < b { return a }; return b }
