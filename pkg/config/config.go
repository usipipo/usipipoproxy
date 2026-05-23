package config

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

type Config struct {
	DBPath                  string
	WGInterface             string
	WGEndpointHost          string
	WGEndpointPort          int
	WGSubnet                string
	TelegramBotToken        string
	TelegramWebhookSecret   string
	JWTSecret               string
	APIPort                 string
	ExporterPoll            time.Duration
	TronDealerAPIKey        string
	TronDealerWebhookSecret string
	TronDealerBaseURL       string
}

func MustLoad() Config {
	cfg := Config{
		DBPath:                  getEnvDefault("DB_PATH", "./data/usipipo.db"),
		WGInterface:             getEnvDefault("WG_INTERFACE", "wg0"),
		WGEndpointHost:          getEnvDefault("WG_ENDPOINT_HOST", ""),
		WGEndpointPort:          mustInt("WG_ENDPOINT_PORT"),
		WGSubnet:                getEnvOrDefault("WG_SUBNET", "10.66.66.0/24"),
		TelegramBotToken:        os.Getenv("TELEGRAM_BOT_TOKEN"),
		TelegramWebhookSecret:   getEnvOrDefault("TELEGRAM_WEBHOOK_SECRET", ""),
		JWTSecret:               os.Getenv("JWT_SECRET"),
		APIPort:                 getEnvOrDefault("API_PORT", "8001"),
		ExporterPoll:            parseDuration(getEnvOrDefault("EXPORTER_POLL_INTERVAL", "15s")),
		TronDealerAPIKey:        os.Getenv("TRONDEALER_API_KEY"),
		TronDealerWebhookSecret: getEnvOrDefault("TRONDEALER_WEBHOOK_SECRET", ""),
		TronDealerBaseURL:       getEnvOrDefault("TRONDEALER_BASE_URL", "https://www.trondealer.com"),
	}

	if cfg.JWTSecret == "" {
		panic("JWT_SECRET is required")
	}
	if cfg.TelegramBotToken == "" {
		panic("TELEGRAM_BOT_TOKEN is required")
	}
	if cfg.WGEndpointPort == 0 {
		panic("WG_ENDPOINT_PORT must be a non-zero integer")
	}
	// WGEndpointHost es vacío en build/test; en producción Docker (NET_ADMIN) se fija en runtime
	if cfg.WGEndpointHost == "" {
		fmt.Println("WARN: WG_ENDPOINT_HOST vacío — el endpoint WireGuard se resolverá desde wg show")
	}
	return cfg
}

func getEnvDefault(key, def string) string {
	v := os.Getenv(key)
	if v == "" {
		return def
	}
	return v
}
func getEnvOrDefault(key, def string) string { return getEnvDefault(key, def) }
func getEnv(key string) string               { return os.Getenv(key) }
func mustInt(key string) int {
	v, err := strconv.Atoi(getEnvDefault(key, "0"))
	if err != nil {
		panic(key + " must be an integer")
	}
	return v
}
func parseDuration(s string) time.Duration {
	d, err := time.ParseDuration(s)
	if err != nil {
		panic(err)
	}
	return d
}
