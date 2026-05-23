package bot

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"strings"
	"time"

	"github.com/usipipo/usipipoproxy/internal/wg"
	"github.com/usipipo/usipipoproxy/pkg/models"
)

// ctxKey para JWT validation via middleware
type ctxKey int

const botUserKey ctxKey = 1

// Store interface reutiliza la de db.
type Store interface {
	GetOrCreateUser(u *models.TelegramUser) (*models.User, error)
	CreateDevice(userID int64, name, pubKey, privKey, ipAddr, psk string) (*models.Device, error)
	ListDevices(userID int64) ([]models.Device, error)
	GetDeviceByID(deviceID int64) (*models.Device, error)
	DeleteDevice(deviceID int64) error
	GetAllAssignedIPs() (map[string]bool, error)
}

// InlineKeyboardButton representa un botón inline de Telegram.
type InlineKeyboardButton struct {
	Text         string `json:"text"`
	URL          string `json:"url,omitempty"`
	CallbackData string `json:"callback_data,omitempty"`
}

// InlineKeyboardMarkup es el teclado inline de Telegram.
type InlineKeyboardMarkup struct {
	InlineKeyboard [][]InlineKeyboardButton `json:"inline_keyboard"`
}

// WebhookHandler procesa mensajes del bot de Telegram.
type WebhookHandler struct {
	store     Store
	wgManager *wg.Manager
	baseURL   string // "usipipo.dpdns.org"
	port      string // puerto WireGuard
	botToken  string
}

func NewWebhookHandler(store Store, wgMgr *wg.Manager, baseURL, port, botToken string) *WebhookHandler {
	return &WebhookHandler{
		store:     store,
		wgManager: wgMgr,
		baseURL:   baseURL,
		port:      port,
		botToken:  botToken,
	}
}

// WebhookPayload — estructura recibida desde el webhook de Telegram.
type WebhookPayload struct {
	UpdateID int64       `json:"update_id"`
	Message  *TgMessage  `json:"message,omitempty"`
	Callback *TgCallback `json:"callback_query,omitempty"`
}

type TgMessage struct {
	MessageID int64                `json:"message_id"`
	From      *models.TelegramUser `json:"from"`
	Chat      TgChat               `json:"chat"`
	Text      string               `json:"text"`
	Date      int64                `json:"date"`
}

type TgCallback struct {
	ID      string     `json:"id"`
	From    TgUser     `json:"from"`
	Message *TgMessage `json:"message,omitempty"`
	Data    string     `json:"data"`
	ChatID  int64      `json:"chat_instance"`
}

type TgUser struct {
	ID       int64  `json:"id"`
	Username string `json:"username,omitempty"`
}

type TgChat struct {
	ID   int64  `json:"id"`
	Type string `json:"type"`
}

// tgFrom extrae el TelegramUser del payload sea mensaje o callback.
func tgFrom(p *WebhookPayload) *models.TelegramUser {
	if p.Message != nil && p.Message.From != nil {
		return p.Message.From
	}
	if p.Callback != nil {
		return &models.TelegramUser{
			ID:        p.Callback.From.ID,
			Username:  p.Callback.From.Username,
			FirstName: p.Callback.From.Username,
		}
	}
	return nil
}

// tgChatID extrae el chat_id sea de mensaje o callback.
func tgChatID(p *WebhookPayload) int64 {
	if p.Message != nil {
		return p.Message.Chat.ID
	}
	if p.Callback != nil {
		return p.Callback.Message.Chat.ID
	}
	return 0
}

// tgText devuelve el texto del mensaje o el callback_data.
func tgText(p *WebhookPayload) string {
	if p.Message != nil {
		return p.Message.Text
	}
	if p.Callback != nil {
		return p.Callback.Data
	}
	return ""
}

// botEndpointURL construye la URL del endpoint del bot de Telegram.
func (h *WebhookHandler) botEndpointURL() string {
	return fmt.Sprintf("https://api.telegram.org/bot%s", h.botToken)
}

// SendMessage envía un mensaje de texto a un chat de Telegram.
// Si keyboard es nil se envía sin teclado inline.
func (h *WebhookHandler) SendMessage(chatID int64, text string, keyboard *InlineKeyboardMarkup) error {
	url := h.botEndpointURL() + "/sendMessage"

	payload := map[string]any{
		"chat_id":    chatID,
		"text":       text,
		"parse_mode": "MarkdownV2",
	}
	if keyboard != nil {
		payload["reply_markup"] = keyboard
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal sendMessage: %w", err)
	}

	req, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("new request sendMessage: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return fmt.Errorf("http sendMessage: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 400 {
		return fmt.Errorf("sendMessage HTTP %d", resp.StatusCode)
	}
	return nil
}

// answerCallback responde a un callback de Telegram (cierra el estado de "cargando" del botón).
func (h *WebhookHandler) answerCallback(callbackID string) error {
	url := h.botEndpointURL() + "/answerCallbackQuery"
	body, err := json.Marshal(map[string]any{"callback_query_id": callbackID})
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}
	resp.Body.Close()
	return nil
}

// ─── Respuestas de comandos ─────────────────────────────────────────────────────

// cmdStart maneja /start.
func (h *WebhookHandler) cmdStart(from *models.TelegramUser) (string, *InlineKeyboardMarkup) {
	text := fmt.Sprintf("Bienvenido a uSipipo Proxy, %s!\nUsa los botones o escribe /status para ver tus dispositivos.",
		from.FirstName)
	return text,
		&InlineKeyboardMarkup{
			InlineKeyboard: [][]InlineKeyboardButton{
				{
					{Text: "🚀 Conectar VPN", CallbackData: "/connect"},
					{Text: "📋 Mis dispositivos", CallbackData: "/status"},
				},
			},
		}
}

// cmdStatus maneja /status y /devices.
func (h *WebhookHandler) cmdStatus(from *models.TelegramUser) (string, *InlineKeyboardMarkup) {
	user, err := h.store.GetOrCreateUser(from)
	if err != nil {
		return "Error al leer dispositivos. Intenta mas tarde.", nil
	}
	devices, err := h.store.ListDevices(user.ID)
	if err != nil {
		return "Error al leer dispositivos. Intenta mas tarde.", nil
	}
	if len(devices) == 0 {
		text := "No tienes dispositivos.\nUsa /connect o el boton de abajo para crear el primero."
		return text,
			&InlineKeyboardMarkup{
				InlineKeyboard: [][]InlineKeyboardButton{
					{
						{Text: "🚀 Conectar VPN", CallbackData: "/connect"},
					},
				},
			}
	}

	sb := strings.Builder{}
	fmt.Fprintf(&sb, "Tus dispositivos (%d):\n\n", len(devices))
	var rows [][]InlineKeyboardButton
	for _, d := range devices {
		rx := float64(d.BytesRx) / (1024 * 1024 * 1024)
		tx := float64(d.BytesTx) / (1024 * 1024 * 1024)
		status := "activo"
		if !d.Enabled {
			status = "revocado"
		}
		fmt.Fprintf(&sb, "  %s\n  IP: %s | RX: %.2f GB | TX: %.2f GB | %s\n",
			d.Name, d.AssignedIP, rx, tx, status)
		confURL := fmt.Sprintf("%s/proxy/devices/%d/conf", h.baseURL, d.ID)
		rows = append(rows, []InlineKeyboardButton{
			{Text: "🔑 Ver .conf", URL: confURL},
		})
	}
	return sb.String(), &InlineKeyboardMarkup{InlineKeyboard: rows}
}

// cmdConnect crea un nuevo dispositivo VPN.
func (h *WebhookHandler) cmdConnect(from *models.TelegramUser) (string, *InlineKeyboardMarkup) {
	user, err := h.store.GetOrCreateUser(from)
	if err != nil {
		return "Error al conectar. Intenta /start mas tarde.", nil
	}

	name := fmt.Sprintf("device-%d", time.Now().Unix()%100000)
	pubKey, privKey, err := wg.GenerateKeyPair()
	if err != nil {
		return "Error al generar claves. Intenta /connect mas tarde.", nil
	}

	taken, err := h.store.GetAllAssignedIPs()
	if err != nil {
		return "Error al leer IPs. Intenta mas tarde.", nil
	}
	freeIP, err := h.wgManager.NextFreeIP(taken)
	if err != nil {
		return "Sin IPs disponibles. Contacta al administrador.", nil
	}

	device, err := h.store.CreateDevice(user.ID, name, pubKey, privKey, freeIP.String(), "")
	if err != nil {
		return "Error al registrar dispositivo. Intenta mas tarde.", nil
	}

	confURL := fmt.Sprintf("%s/proxy/devices/%d/conf", h.baseURL, device.ID)
	text := fmt.Sprintf("Dispositivo creado: %s\nIP: %s\nEndpoint: %s\nDescarga tu archivo .conf abajo 👇",
		name, freeIP.String(), h.port)
	return text,
		&InlineKeyboardMarkup{
			InlineKeyboard: [][]InlineKeyboardButton{
				{
					{Text: "📄 Descargar .conf", URL: confURL},
				},
			},
		}
}

// cmdHelp muestra la ayuda.
func (h *WebhookHandler) cmdHelp() (string, *InlineKeyboardMarkup) {
	text := "Comandos disponibles:\n" +
		"  /start - iniciar sesion\n" +
		"  /status - ver tus dispositivos y consumo\n" +
		"  /connect - crear un nuevo dispositivo VPN\n" +
		"  /help - esta ayuda"
	return text,
		&InlineKeyboardMarkup{
			InlineKeyboard: [][]InlineKeyboardButton{
				{
					{Text: "🚀 Conectar", CallbackData: "/connect"},
					{Text: "📋 Estado", CallbackData: "/status"},
				},
				{
					{Text: "❓ Ayuda", CallbackData: "/help"},
				},
			},
		}
}

// cmdUnknown para comandos no reconocidos.
func (h *WebhookHandler) cmdUnknown() (string, *InlineKeyboardMarkup) {
	return "Comandos: /start · /status · /connect · /help",
		&InlineKeyboardMarkup{
			InlineKeyboard: [][]InlineKeyboardButton{
				{
					{Text: "🚀 Conectar", CallbackData: "/connect"},
					{Text: "📋 Estado", CallbackData: "/status"},
				},
			},
		}
}

// Dispatch rutea el comando por texto y devuelve (texto, teclado inline).
func (h *WebhookHandler) Dispatch(p *WebhookPayload) (string, *InlineKeyboardMarkup) {
	cmd := strings.TrimSpace(tgText(p))
	from := tgFrom(p)

	if cmd == "" || from == nil {
		return "", nil
	}

	switch cmd {
	case "/start":
		return h.cmdStart(from)

	case "/status", "/devices":
		return h.cmdStatus(from)

	case "/connect":
		return h.cmdConnect(from)

	case "/help":
		return h.cmdHelp()

	default:
		return h.cmdUnknown()
	}
}

// Handler implementa http.Handler para el webhook.
func (h *WebhookHandler) Handler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeMethodNotAllowed(w)
		return
	}

	var payload WebhookPayload
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		slog.Warn("bot webhook bad body", "err", err)
		writeError(w, http.StatusBadRequest, "bad request")
		return
	}

	chatID := tgChatID(&payload)

	// Extraer el mensaje fuente: si es callback usar el mensaje embebido, si es mensaje directo usar el payload.
	src := &WebhookPayload{Message: payload.Message}
	if payload.Callback != nil && payload.Callback.Message != nil {
		src.Message = payload.Callback.Message
	}

	text, keyboard := h.Dispatch(src)

	// Si es callback, confirmarlo a Telegram.
	if payload.Callback != nil {
		if err := h.answerCallback(payload.Callback.ID); err != nil {
			slog.Warn("answer callback", "err", err, "id", payload.Callback.ID)
		}
	}

	// Enviar la respuesta por SendMessage (o loguear si no hay chat_id).
	if text != "" && chatID != 0 {
		if err := h.SendMessage(chatID, text, keyboard); err != nil {
			slog.Error("sendMessage reply", "err", err, "chat_id", chatID)
		}
	} else if text != "" {
		slog.Warn("bot reply sin chat_id", "update", payload.UpdateID)
	}

	writeJSON(w, http.StatusOK, map[string]string{"ok": "true"})
}

// ─── HTTP helpers ───────────────────────────────────────────────────────────────

func writeJSON(w http.ResponseWriter, code int, v any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(v)
}

func writeMethodNotAllowed(w http.ResponseWriter) {
	http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
}

func writeError(w http.ResponseWriter, code int, msg string) {
	writeJSON(w, code, map[string]string{"error": msg})
}
