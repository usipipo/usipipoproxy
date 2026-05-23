package middleware

import (
	"context"
	"log/slog"
	"net/http"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/usipipo/usipipoproxy/internal/db"
	"github.com/usipipo/usipipoproxy/pkg/models"
)

// AuthMiddleware valida JWT desde header Authorization o cookie "session"
// e inyecta el usuario autenticado en el contexto.
func AuthMiddleware(store *db.Store, jwtSecret string, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		token := tokenFromRequest(r)
		if token == "" {
			http.Error(w, "missing token", http.StatusUnauthorized)
			return
		}

		claims, err := validateJWT(token, jwtSecret)
		if err != nil {
			slog.Warn("jwt validation failed", "err", err)
			http.Error(w, "invalid token", http.StatusUnauthorized)
			return
		}

		uid, ok := claims["uid"].(float64)
		if !ok {
			http.Error(w, "invalid token claims", http.StatusUnauthorized)
			return
		}

		user, err := store.GetUserByID(int64(uid))
		if err != nil {
			slog.Error("user lookup after jwt", "uid", uid, "err", err)
			http.Error(w, "user not found", http.StatusUnauthorized)
			return
		}

		next.ServeHTTP(w, r.WithContext(
			contextWithUser(r.Context(), user),
		))
	})
}

// tokenFromRequest extrae el JWT del header Authorization o de la cookie "session".
func tokenFromRequest(r *http.Request) string {
	// 1. Header Authorization: Bearer <token>
	auth := r.Header.Get("Authorization")
	if strings.HasPrefix(auth, "Bearer ") {
		return strings.TrimPrefix(auth, "Bearer ")
	}
	// 2. Cookie "session"
	cookie, err := r.Cookie("session")
	if err == nil && cookie.Value != "" {
		return cookie.Value
	}
	return ""
}

// validateJWT valida y devuelve los claims de un JWT HS256.
func validateJWT(tokenString, secret string) (jwt.MapClaims, error) {
	tok, err := jwt.Parse(tokenString, func(t *jwt.Token) (any, error) {
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, jwt.ErrSignatureInvalid
		}
		return []byte(secret), nil
	})
	if err != nil {
		return nil, err
	}
	if !tok.Valid {
		return nil, jwt.ErrTokenInvalidClaims
	}
	claims, ok := tok.Claims.(jwt.MapClaims)
	if !ok {
		return nil, jwt.ErrTokenInvalidClaims
	}
	return claims, nil
}

// contextWithUser inyecta un *models.User en el contexto.
// Usa la misma clave ctxKey que los handlers esperan.
type ctxKey int

const userCtxKey ctxKey = 0

func contextWithUser(ctx context.Context, u *models.User) context.Context {
	return context.WithValue(ctx, userCtxKey, u)
}

// UserFromCtx extrae el usuario del contexto.
func UserFromCtx(ctx context.Context) (*models.User, bool) {
	u, ok := ctx.Value(userCtxKey).(*models.User)
	return u, ok
}

// SetSessionCookie escribe una cookie de sesión HttpOnly con el JWT.
func SetSessionCookie(w http.ResponseWriter, token string, exp time.Time) {
	http.SetCookie(w, &http.Cookie{
		Name:     "session",
		Value:    token,
		Path:     "/",
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteStrictMode,
		Expires:  exp,
	})
}

// ClearSessionCookie borra la cookie de sesión.
func ClearSessionCookie(w http.ResponseWriter) {
	http.SetCookie(w, &http.Cookie{
		Name:     "session",
		Value:    "",
		Path:     "/",
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteStrictMode,
		Expires:  time.Now().Add(-1 * time.Hour),
		MaxAge:   -1,
	})
}
