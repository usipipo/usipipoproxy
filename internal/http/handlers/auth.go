package handlers

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/usipipo/usipipoproxy/pkg/models"
)

// AuthStore define lo que el handler de autenticacion necesita del store.
type AuthStore interface {
	GetOrCreateUser(u *models.TelegramUser) (*models.User, error)
}

type AuthHandler struct {
	store    AuthStore
	botToken string
	secret   string
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

// validateTelegramHashManual implementa el algoritmo oficial de Telegram:
// 1. Campos ordenados alfabeticamente, excluyendo "hash"
// 2. Unidos con \n: "auth_date=N\nfirst_name=X\nid=M\n..."
// 3. HMAC-SHA256(data_check_string, BOT_TOKEN) == hash recibido
func validateTelegramHashManual(req LoginRequest, botToken string) error {
	if botToken == "" {
		return fmt.Errorf("bot token is empty")
	}
	pairs := []string{
		"auth_date=" + fmt.Sprintf("%d", req.AuthDate),
		"first_name=" + req.FirstName,
		"id=" + fmt.Sprintf("%d", req.ID),
	}
	if req.Username != "" {
		pairs = append(pairs, "username="+req.Username)
	}
	if req.LastName != "" {
		pairs = append(pairs, "last_name="+req.LastName)
	}
	if req.PhotoURL != "" {
		pairs = append(pairs, "photo_url="+req.PhotoURL)
	}
	checkString := ""
	for i, p := range pairs {
		if i > 0 {
			checkString += "\n"
		}
		checkString += p
	}
	mac := hmac.New(sha256.New, []byte(botToken))
	mac.Write([]byte(checkString))
	expected := hex.EncodeToString(mac.Sum(nil))
	if !hmac.Equal([]byte(expected), []byte(req.Hash)) {
		return fmt.Errorf("hash mismatch")
	}
	return nil
}

// POST /proxy/auth/telegram — valida hash Telegram y devuelve JWT.
func (h *AuthHandler) Handler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeMethodNotAllowed(w)
		return
	}

	var req LoginRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid body")
		return
	}
	if req.ID == 0 || req.Hash == "" {
		writeError(w, http.StatusBadRequest, "id and hash required")
		return
	}

	if err := validateTelegramHashManual(req, h.botToken); err != nil {
		slog.Warn("invalid telegram hash", "tg_id", req.ID, "err", err)
		writeError(w, http.StatusUnauthorized, "invalid telegram auth")
		return
	}

	user, err := h.store.GetOrCreateUser(&models.TelegramUser{
		ID: req.ID, Username: req.Username, FirstName: req.FirstName,
	})
	if err != nil {
		slog.Error("get or create user", "err", err, "tg_id", req.ID)
		writeError(w, http.StatusInternalServerError, "user lookup failed")
		return
	}

	tok, err := generateJWT(user, h.secret, 30*24*time.Hour)
	if err != nil {
		slog.Error("jwt generation", "err", err, "tg_id", req.ID)
		writeError(w, http.StatusInternalServerError, "token generation failed")
		return
	}

	writeJSON(w, http.StatusOK, LoginResponse{
		Token: tok, User: *user, ExpiresAt: time.Now().Add(30 * 24 * time.Hour).Unix(),
	})
}
