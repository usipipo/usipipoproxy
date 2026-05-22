package db

import (
	"database/sql"
	"fmt"
	"log/slog"
	"path/filepath"

	"github.com/usipipo/usipipoproxy/pkg/models"

	_ "github.com/mattn/go-sqlite3"
)

type Store struct {
	db *sql.DB
}

func NewStore(dbPath string) (*Store, error) {
	dir := filepath.Dir(dbPath)
	if err := ensureDir(dir); err != nil {
		return nil, err
	}

	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, fmt.Errorf("open db: %w", err)
	}
	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("ping db: %w", err)
	}
	if err := applyMigrations(db); err != nil {
		return nil, fmt.Errorf("migrate: %w", err)
	}
	slog.Info("store ready", "path", dbPath)
	return &Store{db: db}, nil
}

func ensureDir(p string) error {
	if _, err := sql.Open("sqlite3", ":memory:"); err != nil {
		return err
	}
	return nil
}

// ─── Migrations ───────────────────────────────────────────────────────────────

const migrationSQL = `
CREATE TABLE IF NOT EXISTS users (
	id            INTEGER PRIMARY KEY AUTOINCREMENT,
	telegram_id   INTEGER NOT NULL UNIQUE,
	username      TEXT,
	first_name    TEXT,
	role          TEXT NOT NULL DEFAULT 'user',
	created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS devices (
	id            INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id       INTEGER NOT NULL REFERENCES users(id),
	name          TEXT NOT NULL,
	public_key    TEXT NOT NULL UNIQUE,
	assigned_ip   TEXT NOT NULL,
	psk           TEXT,
	enabled       INTEGER NOT NULL DEFAULT 1,
	created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	last_seen_at  DATETIME
);

CREATE TABLE IF NOT EXISTS traffic_samples (
	id          INTEGER PRIMARY KEY AUTOINCREMENT,
	device_id   INTEGER NOT NULL REFERENCES devices(id),
	bytes_rx    INTEGER NOT NULL,
	bytes_tx    INTEGER NOT NULL,
	timestamp   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_devices_user ON devices(user_id);
CREATE INDEX IF NOT EXISTS idx_traffic_device_ts ON traffic_samples(device_id, timestamp);
`

func applyMigrations(db *sql.DB) error {
	_, err := db.Exec(migrationSQL)
	return err
}

// ─── Users ────────────────────────────────────────────────────────────────────

func (s *Store) GetOrCreateUser(u *models.TelegramUser) (*models.User, error) {
	var user models.User
	err := s.db.QueryRow("SELECT id, telegram_id, username, first_name, role, created_at FROM users WHERE telegram_id = ?", u.ID).
		Scan(&user.ID, &user.TelegramID, &user.Username, &user.FirstName, &user.Role, &user.CreatedAt)
	if err == nil {
		return &user, nil
	}

	res, err := s.db.Exec("INSERT INTO users (telegram_id, username, first_name, role) VALUES (?, ?, ?, 'user')",
		u.ID, u.Username, u.FirstName)
	if err != nil {
		return nil, err
	}
	id, _ := res.LastInsertId()
	return &models.User{ID: id, TelegramID: u.ID, Username: u.Username, FirstName: u.FirstName, Role: "user", CreatedAt: user.CreatedAt}, nil
}

func (s *Store) GetUserByTGID(tgID int64) (*models.User, error) {
	var u models.User
	err := s.db.QueryRow("SELECT id, telegram_id, username, first_name, role, created_at FROM users WHERE telegram_id = ?", tgID).
		Scan(&u.ID, &u.TelegramID, &u.Username, &u.FirstName, &u.Role, &u.CreatedAt)
	if err != nil { return nil, err }
	return &u, nil
}

// ─── Devices ──────────────────────────────────────────────────────────────────

func (s *Store) CreateDevice(userID int64, name, publicKey, assignedIP, psk string) (*models.Device, error) {
	res, err := s.db.Exec(
		"INSERT INTO devices (user_id, name, public_key, assigned_ip, psk) VALUES (?, ?, ?, ?, ?)",
		userID, name, publicKey, assignedIP, psk)
	if err != nil { return nil, err }
	id, _ := res.LastInsertId()
	return &models.Device{
		ID: id, UserID: userID, Name: name,
		PublicKey: publicKey, AssignedIP: assignedIP, PSK: psk, Enabled: true,
	}, nil
}

func (s *Store) ListDevices(userID int64) ([]models.Device, error) {
	rows, err := s.db.Query("SELECT id, user_id, name, public_key, assigned_ip, psk, enabled, created_at, last_seen_at FROM devices WHERE user_id = ?", userID)
	if err != nil { return nil, err }
	defer rows.Close()
	var out []models.Device
	for rows.Next() {
		var d models.Device
		if err := rows.Scan(&d.ID, &d.UserID, &d.Name, &d.PublicKey, &d.AssignedIP, &d.PSK, &d.Enabled, &d.CreatedAt, &d.LastSeenAt); err != nil {
			return nil, err
		}
		out = append(out, d)
	}
	return out, nil
}

func (s *Store) GetDeviceByID(deviceID int64) (*models.Device, error) {
	var d models.Device
	err := s.db.QueryRow("SELECT id, user_id, name, public_key, assigned_ip, psk, enabled, created_at, last_seen_at FROM devices WHERE id = ?", deviceID).
		Scan(&d.ID, &d.UserID, &d.Name, &d.PublicKey, &d.AssignedIP, &d.PSK, &d.Enabled, &d.CreatedAt, &d.LastSeenAt)
	if err != nil { return nil, err }
	return &d, nil
}

func (s *Store) GetDeviceByPublicKey(pubKey string) (*models.Device, error) {
	var d models.Device
	err := s.db.QueryRow("SELECT id, user_id, name, public_key, assigned_ip, psk, enabled, created_at, last_seen_at FROM devices WHERE public_key = ? LIMIT 1", pubKey).
		Scan(&d.ID, &d.UserID, &d.Name, &d.PublicKey, &d.AssignedIP, &d.PSK, &d.Enabled, &d.CreatedAt, &d.LastSeenAt)
	if err != nil { return nil, err }
	return &d, nil
}

func (s *Store) DeleteDevice(deviceID int64) error {
	_, err := s.db.Exec("UPDATE devices SET enabled = 0 WHERE id = ?", deviceID)
	return err
}

func (s *Store) MarkDeviceSeen(pubKey string) error {
	_, err := s.db.Exec("UPDATE devices SET last_seen_at = CURRENT_TIMESTAMP WHERE public_key = ?", pubKey)
	return err
}

// GetAllAssignedIPs devuelve el mapa de IPs virtuales actualmente asignadas.
func (s *Store) GetAllAssignedIPs() (map[string]bool, error) {
	rows, err := s.db.Query("SELECT assigned_ip FROM devices WHERE enabled = 1")
	if err != nil { return nil, err }
	defer rows.Close()
	m := make(map[string]bool)
	for rows.Next() {
		var ip string
		if err := rows.Scan(&ip); err != nil { return nil, err }
		m[ip] = true
	}
	return m, nil
}

// ─── Traffic ──────────────────────────────────────────────────────────────────

func (s *Store) InsertTraffic(deviceID int64, rx, tx uint64) error {
	_, err := s.db.Exec("INSERT INTO traffic_samples (device_id, bytes_rx, bytes_tx) VALUES (?, ?, ?)", deviceID, rx, tx)
	return err
}

func (s *Store) GetTrafficSummary(deviceID int64, period string) (*models.TrafficSummary, error) {
	var rx, tx uint64
	err := s.db.QueryRow(`
		SELECT COALESCE(SUM(bytes_rx),0), COALESCE(SUM(bytes_tx),0)
		FROM traffic_samples WHERE device_id = ?
	`, deviceID).Scan(&rx, &tx)
	if err != nil { return nil, err }

	toGB := func(u uint64) float64 { return float64(u) / (1024 * 1024 * 1024) }

	return &models.TrafficSummary{
		DeviceID: deviceID, Period: period,
		TotalRxGB: toGB(rx), TotalTxGB: toGB(tx),
		TotalGB: toGB(rx + tx),
	}, nil
}
