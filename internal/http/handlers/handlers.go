package handlers

import (
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/usipipo/usipipoproxy/internal/wg"
	"github.com/usipipo/usipipoproxy/pkg/models"
)

// —————————————————————————————————————————————————————————————————
//  UTILS
// —————————————————————————————————————————————————————————————————

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

// context key para el usuario autenticado
type ctxKey int
const userCtxKey ctxKey = 0

func withUser(r *http.Request, u *models.User) *http.Request {
	return r.WithContext(context.WithValue(r.Context(), userCtxKey, u))
}

func userFromCtx(r *http.Request) (*models.User, bool) {
	u, ok := r.Context().Value(userCtxKey).(*models.User)
	return u, ok
}

// userIDFromCtx extrae el ID numérico del usuario autenticado.
func userIDFromCtx(r *http.Request) (int64, bool) {
	u, ok := userFromCtx(r)
	if !ok || u == nil { return 0, false }
	return u.ID, true
}

// —————————————————————————————————────────────────————————————————
//  AUTH
// —————————————————————————————————————————————————————————————————

type AuthHandler struct {
	store    AuthStore
	botToken string
	secret   string
}

type AuthStore interface {
	GetOrCreateUser(u *models.TelegramUser) (*models.User, error)
}

func NewAuthHandler(store AuthStore, botToken, jwtSecret string) *AuthHandler {
	return &AuthHandler{store: store, botToken: botToken, secret: jwtSecret}
}

type LoginRequest struct {
	ID        int64  `json:"id"`
	Username  string `json:"username,omitempty"`
	FirstName string `json:"first_name"`
	LastName  string `json:"last_name,omitempty"`
	PhotoURL  string `json:"photo_url,omitempty"`
	AuthDate  int64  `json:"auth_date"`
	Hash      string `json:"hash"`
}

type LoginResponse struct {
	Token     string      `json:"token"`
	User      models.User `json:"user"`
	ExpiresAt int64       `json:"expires_at"`
}

// generateJWT crea y firma un token JWT HS256.
func generateJWT(u *models.User, secret string, ttl time.Duration) (string, error) {
	now := time.Now().UTC()
	claims := jwt.MapClaims{
		"uid": u.ID, "tid": u.TelegramID, "un": u.Username,
		"fn": u.FirstName, "rl": u.Role,
		"iat": now.Unix(), "exp": now.Add(ttl).Unix(),
	}
	tok := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return tok.SignedString([]byte(secret))
}

// POST /proxy/auth/telegram — valida hash Telegram y devuelve JWT.
func (h *AuthHandler) Handler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost { writeMethodNotAllowed(w); return }

	var req LoginRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid body"); return
	}
	if req.ID == 0 || req.Hash == "" {
		writeError(w, http.StatusBadRequest, "id and hash required"); return
	}

	if err := validateTelegramHashManual(req, h.botToken); err != nil {
		slog.Warn("invalid telegram hash", "tg_id", req.ID, "err", err)
		writeError(w, http.StatusUnauthorized, "invalid telegram auth"); return
	}

	user, err := h.store.GetOrCreateUser(&models.TelegramUser{
		ID: req.ID, Username: req.Username, FirstName: req.FirstName,
	})
	if err != nil {
		slog.Error("get or create user", "err", err, "tg_id", req.ID)
		writeError(w, http.StatusInternalServerError, "user lookup failed"); return
	}

	tok, err := generateJWT(user, h.secret, 30*24*time.Hour)
	if err != nil {
		slog.Error("jwt generation", "err", err, "tg_id", req.ID)
		writeError(w, http.StatusInternalServerError, "token generation failed"); return
	}

	writeJSON(w, http.StatusOK, LoginResponse{
		Token: tok, User: *user, ExpiresAt: time.Now().Add(30*24*time.Hour).Unix(),
	})
}

// validateTelegramHashManual implementa el algoritmo oficial de Telegram:
// 1. Campos ordenados alfabéticamente, excluyendo "hash"
// 2. Unidos con \n: "auth_date=N\nfirst_name=X\nid=M\n..."
// 3. HMAC-SHA256(data_check_string, BOT_TOKEN) == hash recibido
func validateTelegramHashManual(req LoginRequest, botToken string) error {
	if botToken == "" { return fmt.Errorf("bot token is empty") }
	pairs := []string{
		"auth_date=" + strconv.FormatInt(req.AuthDate, 10),
		"first_name=" + req.FirstName,
		"id=" + strconv.FormatInt(req.ID, 10),
	}
	if req.Username != "" { pairs = append(pairs, "username="+req.Username) }
	if req.LastName != ""  { pairs = append(pairs, "last_name="+req.LastName) }
	if req.PhotoURL != ""  { pairs = append(pairs, "photo_url="+req.PhotoURL) }
	checkString := strings.Join(pairs, "\n")
	mac := hmac.New(sha256.New, []byte(botToken))
	mac.Write([]byte(checkString))
	expected := hex.EncodeToString(mac.Sum(nil))
	if !hmac.Equal([]byte(expected), []byte(req.Hash)) {
		return fmt.Errorf("hash mismatch")
	}
	return nil
}

// —————————————————————————————————————————————————————————————————
//  DEVICES
// —————————————————————————————————————————————————————————————————

// Store2 extiende AuthStore con todo lo que necesitan los handlers.
type Store2 interface {
	AuthStore
	ListDevices(userID int64) ([]models.Device, error)
	GetDeviceByID(deviceID int64) (*models.Device, error)
	DeleteDevice(deviceID int64) error
	GetTrafficSummary(deviceID int64, period string) (*models.TrafficSummary, error)
	GetAllAssignedIPs() (map[string]bool, error)
	CreateDevice(userID int64, name, pubKey, ip, psk string) (*models.Device, error)
	GetDeviceByPublicKey(pubKey string) (*models.Device, error)
}

type DevicesHandler struct {
	store     Store2
	wgManager *wg.Manager
	endpoint  string
}

func NewDevicesHandler(store Store2, wgMgr *wg.Manager, endpoint string) *DevicesHandler {
	return &DevicesHandler{store: store, wgManager: wgMgr, endpoint: endpoint}
}

// Router despacha por método HTTP bajo el prefijo /proxy/devices.
func (h *DevicesHandler) Router(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		if strings.HasSuffix(r.URL.Path, "/traffic") { h.Traffic(w, r); return }
		h.List(w, r)
	case http.MethodPost:
		h.Create(w, r)
	case http.MethodDelete:
		id := strings.TrimPrefix(r.URL.Path, "/proxy/devices/")
		h.Delete(w, r, id)
	default:
		writeMethodNotAllowed(w)
	}
}

// GET /proxy/devices — lista de dispositivos del usuario autenticado.
func (h *DevicesHandler) List(w http.ResponseWriter, r *http.Request) {
	uid, ok := userIDFromCtx(r)
	if !ok { writeError(w, http.StatusUnauthorized, "unauthenticated"); return }

	devices, err := h.store.ListDevices(uid)
	if err != nil {
		slog.Error("list devices", "uid", uid, "error", err)
		writeError(w, http.StatusInternalServerError, "failed to list devices"); return
	}
	if devices == nil { devices = []models.Device{} }

	// Enriquecer con tráfico en vivo desde WireGuard
	if h.wgManager != nil {
		if peers, err := h.wgManager.DevicePeers(); err == nil {
			pm := make(map[string]wg.PeerInfo, len(peers))
			for _, p := range peers { pm[p.PublicKey] = p }
			for i := range devices {
				if p, ok := pm[devices[i].PublicKey]; ok {
					devices[i].Rx = p.Rx
					devices[i].Tx = p.Tx
				}
			}
		}
	}
	writeJSON(w, http.StatusOK, devices)
}

// POST /proxy/devices — crea un dispositivo WireGuard completo.
func (h *DevicesHandler) Create(w http.ResponseWriter, r *http.Request) {
	uid, ok := userIDFromCtx(r)
	if !ok { writeError(w, http.StatusUnauthorized, "unauthenticated"); return }

	var req struct {
		Name string `json:"name"`
		PSK  string `json:"psk,omitempty"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid body"); return
	}
	req.Name = strings.TrimSpace(req.Name)
	if req.Name == "" {
		writeError(w, http.StatusBadRequest, "name required"); return
	}

	// Generar par de claves WireGuard
	pubKey, privKey, err := wg.GenerateKeyPair()
	if err != nil {
		slog.Error("keygen", "err", err)
		writeError(w, http.StatusInternalServerError, "key generation failed"); return
	}

	// Asignar IP virtual libre
	taken, _ := h.store.GetAllAssignedIPs()
	freeIP, err := h.wgManager.NextFreeIP(taken)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "no free IP in subnet"); return
	}
	targetIP := freeIP.String()

	// Añadir peer en WireGuard
	if err := h.wgManager.AddPeer(wg.PeerInput{
		PublicKey: pubKey,
		AllowedIP: targetIP + "/32",
		Endpoint:  h.endpoint,
		PSK:       req.PSK,
	}); err != nil {
		slog.Error("wg add peer", "ip", targetIP, "err", err)
		writeError(w, http.StatusInternalServerError, "failed to add wireguard peer"); return
	}

	// Guardar en BD
	device, err := h.store.CreateDevice(uid, req.Name, pubKey, targetIP, req.PSK)
	if err != nil {
		slog.Error("db create device", "err", err)
		_ = h.wgManager.RemovePeer(pubKey) // rollback best-effort
		writeError(w, http.StatusInternalServerError, "failed to save device"); return
	}

	// Configuración de cliente (privada — solo se devuelve una vez en la creación)
	device.Conf = wg.ClientConfig{
		PrivateKey: privKey,
		Address:    targetIP + "/24",
		DNS:        "10.66.66.1",
		PublicKey:  pubKey,
		Endpoint:   h.endpoint,
		AllowedIPs: "0.0.0.0/0",
		PSK:        req.PSK,
	}

	slog.Info("device provisioned",
		"uid", uid, "device_id", device.ID, "name", req.Name, "ip", targetIP)
	writeJSON(w, http.StatusCreated, device)
}

// DELETE /proxy/devices/{id} — revoca un dispositivo.
func (h *DevicesHandler) Delete(w http.ResponseWriter, r *http.Request, idStr string) {
	deviceID, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil || deviceID == 0 {
		writeError(w, http.StatusBadRequest, "invalid device id"); return
	}

	d, err := h.store.GetDeviceByID(deviceID)
	if err != nil {
		writeError(w, http.StatusNotFound, "device not found"); return
	}
	uid, ok := userIDFromCtx(r)
	if !ok || uid != d.UserID {
		writeError(w, http.StatusForbidden, "not authorized"); return
	}

	// Eliminar peer de WireGuard (best-effort: continúa aunque falle)
	if h.wgManager != nil {
		if err := h.wgManager.RemovePeer(d.PublicKey); err != nil {
			slog.Warn("wg remove peer", "device_id", deviceID, "err", err)
		}
	}

	// Marcar inactiva en BD
	if err := h.store.DeleteDevice(deviceID); err != nil {
		slog.Error("db delete device", "device_id", deviceID, "err", err)
		writeError(w, http.StatusInternalServerError, "failed to revoke"); return
	}

	slog.Info("device revoked", "device_id", deviceID, "uid", uid)
	writeJSON(w, http.StatusOK, map[string]any{
		"status": "revoked", "device_id": deviceID, "name": d.Name,
	})
}

// GET /proxy/devices/{id}/traffic — consumo de tráfico por periodo.
func (h *DevicesHandler) Traffic(w http.ResponseWriter, r *http.Request) {
	uid, _ := userIDFromCtx(r)
	devID, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
	if err != nil || devID == 0 {
		writeError(w, http.StatusBadRequest, "invalid device id"); return
	}
	d, err := h.store.GetDeviceByID(devID)
	if err != nil { writeError(w, http.StatusNotFound, "device not found"); return }
	if d.UserID != uid { writeError(w, http.StatusForbidden, "not authorized"); return }

	period := r.URL.Query().Get("period")
	if period == "" { period = "daily" }

	sum, err := h.store.GetTrafficSummary(devID, period)
	if err != nil {
		slog.Error("traffic query", "device_id", devID, "err", err)
		writeError(w, http.StatusInternalServerError, "failed to get traffic"); return
	}
	writeJSON(w, http.StatusOK, sum)
}

// —————————————————————————————————————————————————————————————————
//  HEALTH
// —————————————————————————————————————————————————————————————————

type HealthHandler struct{}

func NewHealthHandler() *HealthHandler { return &HealthHandler{} }

func (h *HealthHandler) Handler(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{
		"status":  "ok",
		"service": "usipipo-backend",
		"version": version,
	})
}
