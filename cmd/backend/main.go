package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/usipipo/usipipoproxy/internal/bot"
	"github.com/usipipo/usipipoproxy/internal/db"
	"github.com/usipipo/usipipoproxy/internal/http/handlers"
	"github.com/usipipo/usipipoproxy/internal/http/middleware"
	"github.com/usipipo/usipipoproxy/internal/wg"
	"github.com/usipipo/usipipoproxy/pkg/config"
	"github.com/usipipo/usipipoproxy/pkg/models"
)

var version = "dev"

func main() {
	var (
		migrate    bool
		seed       bool
		buildStamp string
		staticDir  string
	)
	flag.BoolVar(&migrate, "migrate", false, "aplica migraciones y sale")
	flag.BoolVar(&seed, "seed", false, "carga usuarios beta y sale")
	flag.StringVar(&buildStamp, "build-stamp", time.Now().UTC().Format(time.RFC3339), "timestamp de build")
	flag.StringVar(&staticDir, "static-dir", "", "directorio con el frontend compilado (SPA)")
	flag.Parse()

	cfg := config.MustLoad()
	level := slog.LevelInfo
	if os.Getenv("LOG_LEVEL") == "debug" {
		level = slog.LevelDebug
	}
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: level}))
	slog.SetDefault(logger)

	// ─── BD ────────────────────────────────────────────────────────────────────
	store, err := db.NewStore(cfg.DBPath)
	if err != nil {
		slog.Error("db init failed", "err", err)
		os.Exit(1)
	}

	if migrate {
		slog.Info("migraciones aplicadas, saliendo")
		return
	}
	if seed {
		runSeeds(store)
		slog.Info("seeds aplicadas, saliendo")
		return
	}

	// ─── WireGuard Manager ──────────────────────────────────────────────────────
	endpoint := "165.140.241.96:64000"
	if cfg.WGEndpointHost != "" {
		endpoint = fmt.Sprintf("%s:%d", cfg.WGEndpointHost, cfg.WGEndpointPort)
	}
	wgMgr, err := wg.NewManager(cfg.WGInterface, cfg.WGSubnet, cfg.WGInterface)
	if err != nil {
		slog.Warn("wg manager no disponible (¿sin NET_ADMIN?)", "error", err)
		wgMgr = nil
	}

	// ─── Handlers ──────────────────────────────────────────────────────────────
	authH := handlers.NewAuthHandler(store, cfg.TelegramBotToken, cfg.JWTSecret)
	healthH := handlers.NewHealthHandler()
	devicesH := handlers.NewDevicesHandler(store, wgMgr, endpoint)

	// Payments / TronDealer
	paymentQueue := make(chan handlers.PaymentEvent, 256)
	paymentsH := handlers.NewPaymentHandlers(store, cfg.TronDealerAPIKey, cfg.TronDealerWebhookSecret, cfg.TronDealerBaseURL, paymentQueue)
	handlers.StartPaymentWorker(paymentsH, paymentQueue)

	botH := bot.NewWebhookHandler(store, wgMgr, "usipipo.dpdns.org",
		fmt.Sprintf("%s:%d", cfg.WGEndpointHost, cfg.WGEndpointPort),
		cfg.TelegramBotToken)

	mux := http.NewServeMux()

	// ─── API bajo prefijo /proxy ─────────────────────────────────────────────────
	const prefix = "/proxy"

	// Rutas públicas (sin JWT)
	mux.HandleFunc(prefix+"/auth/telegram", authH.Handler)
	mux.HandleFunc(prefix+"/auth/cookie", setSessionCookieHandler(store, cfg.JWTSecret))
	mux.HandleFunc(prefix+"/health", healthH.Handler)
	mux.HandleFunc(prefix+"/openapi.json", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"openapi":"3.0.0","info":{"title":"uSipipo API","version":"0.1.0"}}`))
	})

	// Rutas protegidas por JWT
	protected := http.NewServeMux()
	protected.Handle(prefix+"/devices", http.StripPrefix(prefix+"/devices", http.HandlerFunc(devicesH.Router)))
	protected.Handle(prefix+"/payments", http.StripPrefix(prefix+"/payments", http.HandlerFunc(paymentsH.Router)))
	protected.HandleFunc("POST /proxy/webhooks/trondealer", handlers.NewTronDealerWebhookHandler(store, cfg.TronDealerWebhookSecret, paymentQueue).Handler)
	mux.Handle("/", middleware.AuthMiddleware(store, cfg.JWTSecret, protected))

	// ─── Webhook Telegram ───────────────────────────────────────────────────────
	mux.HandleFunc("POST /bot/telegram", botH.Handler)

	// ─── Frontend SPA /proxy/app/ ────────────────────────────────────────────────
	if staticDir != "" {
		fileSrv := http.FileServer(http.Dir(staticDir))
		mux.Handle("GET /proxy/app/", fileSrv)
		mux.Handle("GET /proxy/app", http.RedirectHandler("/proxy/app/", http.StatusFound))
		mux.HandleFunc("GET /proxy/app/*", func(w http.ResponseWriter, r *http.Request) {
			r.URL.Path = "/index.html"
			http.StripPrefix("/proxy/app", http.FileServer(http.Dir(staticDir))).
				ServeHTTP(w, r)
		})
		slog.Info("frontend estático servido", "static_dir", staticDir)
	}

	// ─── Server ─────────────────────────────────────────────────────────────────
	srv := &http.Server{Addr: ":" + cfg.APIPort, Handler: loggingMiddleware(mux),
		ReadHeaderTimeout: 10 * time.Second,
		ReadTimeout:       30 * time.Second,
		WriteTimeout:      30 * time.Second,
		IdleTimeout:       120 * time.Second,
	}

	go func() {
		slog.Info("uSipipo Proxy backend",
			"addr", srv.Addr, "version", version, "build", buildStamp)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			slog.Error("ListenAndServe", "err", err)
			os.Exit(1)
		}
	}()

	// Graceful shutdown
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
	<-sigCh
	slog.Info("shutdown signal recibida, cerrando gracefully…")
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	_ = srv.Shutdown(ctx)
	slog.Info("backend cerrado")
}

// loggingMiddleware agrega trazabilidad de peticiones.
func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		slog.Debug("http",
			"method", r.Method, "path", r.URL.Path,
			"remote", r.RemoteAddr, "dur_ms", time.Since(start).Milliseconds())
	})
}

// setSessionCookieHandler recibe un JWT por body y lo establece como cookie HttpOnly.
// POST /proxy/auth/cookie  body: {"token": "<jwt>"}
func setSessionCookieHandler(store *db.Store, jwtSecret string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		var req struct {
			Token string `json:"token"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.Token == "" {
			http.Error(w, "token required", http.StatusBadRequest)
			return
		}
		// Validar JWT y extraer claims
		tok, err := jwt.Parse(req.Token, func(t *jwt.Token) (any, error) {
			if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, jwt.ErrSignatureInvalid
			}
			return []byte(jwtSecret), nil
		})
		if err != nil || !tok.Valid {
			http.Error(w, "invalid token", http.StatusUnauthorized)
			return
		}
		claims, ok := tok.Claims.(jwt.MapClaims)
		if !ok {
			http.Error(w, "invalid claims", http.StatusUnauthorized)
			return
		}
		uidF, ok := claims["uid"].(float64)
		if !ok {
			http.Error(w, "invalid uid", http.StatusUnauthorized)
			return
		}
		// Verificar que el usuario existe
		if _, err := store.GetUserByID(int64(uidF)); err != nil {
			http.Error(w, "user not found", http.StatusUnauthorized)
			return
		}
		exp := time.Unix(int64(claims["exp"].(float64)), 0)
		middleware.SetSessionCookie(w, req.Token, exp)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_ = json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	}
}

var betaUsers = []struct {
	tgID int64
	name string
}{
	{891835105, "mowgli"},
	{634873279, "ersu"},
}

func runSeeds(store *db.Store) {
	for _, b := range betaUsers {
		if _, err := store.GetOrCreateUser(&models.TelegramUser{ID: b.tgID, FirstName: b.name}); err != nil {
			slog.Warn("seed user", "name", b.name, "err", err)
		}
	}
	slog.Info("seeds aplicadas", "count", len(betaUsers))
}
