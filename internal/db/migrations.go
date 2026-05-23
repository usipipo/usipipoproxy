package db

import (
	"database/sql"
	"fmt"
	"time"

	"github.com/usipipo/usipipoproxy/pkg/models"
	_ "github.com/mattn/go-sqlite3"
)

// ─── Migrations ────────────────────────────────────────────────────────────────

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
	private_key   TEXT NOT NULL,
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
	if _, err := db.Exec(migrationSQL); err != nil {
		return err
	}
	// ALTER TABLE users — must be a separate Exec because SQLite does not
	// support ADD COLUMN IF NOT EXISTS.
	if _, err := db.Exec(`
		ALTER TABLE users ADD COLUMN subscription_ends_at DATETIME;
	`); err != nil {
		if !isDuplicateColumnError(err) {
			return fmt.Errorf("alter users subscription_ends_at: %w", err)
		}
	}
	if _, err := db.Exec(`
		ALTER TABLE users ADD COLUMN early_adopter INTEGER NOT NULL DEFAULT 0;
	`); err != nil {
		if !isDuplicateColumnError(err) {
			return fmt.Errorf("alter users early_adopter: %w", err)
		}
	}
	if _, err := db.Exec(`
		ALTER TABLE devices ADD COLUMN private_key TEXT NOT NULL DEFAULT '';
	`); err != nil {
		if !isDuplicateColumnError(err) {
			return fmt.Errorf("alter devices private_key: %w", err)
		}
	}
	if _, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS invoices (
			id                TEXT PRIMARY KEY,
			user_id           INTEGER NOT NULL REFERENCES users(id),
			td_wallet_label   TEXT NOT NULL UNIQUE,
			td_wallet_addr    TEXT NOT NULL,
			amount_usdt       REAL NOT NULL,
			days              INTEGER NOT NULL,
			status            TEXT NOT NULL DEFAULT 'pending',
			td_order_id       TEXT UNIQUE,
			expires_at        DATETIME NOT NULL,
			confirmed_at      DATETIME,
			swept_at          DATETIME,
			raw_webhook_body  TEXT,
			created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
		);
		CREATE INDEX IF NOT EXISTS idx_invoices_user ON invoices(user_id);
		CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
		CREATE INDEX IF NOT EXISTS idx_invoices_wallet_addr ON invoices(td_wallet_addr);
		CREATE INDEX IF NOT EXISTS idx_invoices_order_id ON invoices(td_order_id);
	`); err != nil {
		return fmt.Errorf("create invoices table: %w", err)
	}
	if _, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS webhook_events (
			id          INTEGER PRIMARY KEY AUTOINCREMENT,
			invoice_id  TEXT NOT NULL REFERENCES invoices(id),
			event_type  TEXT NOT NULL,
			td_tx_hash  TEXT,
			raw_body    TEXT NOT NULL,
			processed   INTEGER NOT NULL DEFAULT 0,
			received_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
		);
	`); err != nil {
		return fmt.Errorf("create webhook_events table: %w", err)
	}
	return nil
}

func isDuplicateColumnError(err error) bool {
	return err != nil && err.Error() != ""
}

// ─── Invoice CRUD ─────────────────────────────────────────────────────────────

func (s *Store) CreateInvoice(inv *models.Invoice) error {
	_, err := s.db.Exec(
		`INSERT INTO invoices (id, user_id, td_wallet_label, td_wallet_addr, amount_usdt, days, status, td_order_id, expires_at, raw_webhook_body) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
		inv.ID, inv.UserID, inv.TDWalletLabel, inv.TDWalletAddr, inv.AmountUSDT, inv.Days, inv.Status, inv.TDOrderID, inv.ExpiresAt, inv.RawWebhookBody,
	)
	return err
}

func (s *Store) GetInvoiceByID(id string) (*models.Invoice, error) {
	var inv models.Invoice
	err := s.db.QueryRow(`SELECT id, user_id, td_wallet_label, td_wallet_addr, amount_usdt, days, status, td_order_id, expires_at, confirmed_at, swept_at, raw_webhook_body, created_at FROM invoices WHERE id = ?`,
		id).Scan(&inv.ID, &inv.UserID, &inv.TDWalletLabel, &inv.TDWalletAddr, &inv.AmountUSDT, &inv.Days, &inv.Status, &inv.TDOrderID, &inv.ExpiresAt, &inv.ConfirmedAt, &inv.SweptAt, &inv.RawWebhookBody, &inv.CreatedAt)
	if err != nil {
		return nil, err
	}
	return &inv, nil
}

func (s *Store) GetInvoiceByAddress(addr string) (*models.Invoice, error) {
	var inv models.Invoice
	err := s.db.QueryRow(`SELECT id, user_id, td_wallet_label, td_wallet_addr, amount_usdt, days, status, td_order_id, expires_at, confirmed_at, swept_at, raw_webhook_body, created_at FROM invoices WHERE td_wallet_addr = ?`,
		addr).Scan(&inv.ID, &inv.UserID, &inv.TDWalletLabel, &inv.TDWalletAddr, &inv.AmountUSDT, &inv.Days, &inv.Status, &inv.TDOrderID, &inv.ExpiresAt, &inv.ConfirmedAt, &inv.SweptAt, &inv.RawWebhookBody, &inv.CreatedAt)
	if err != nil {
		return nil, err
	}
	return &inv, nil
}

func (s *Store) GetInvoiceByLabel(label string) (*models.Invoice, error) {
	var inv models.Invoice
	err := s.db.QueryRow(`SELECT id, user_id, td_wallet_label, td_wallet_addr, amount_usdt, days, status, td_order_id, expires_at, confirmed_at, swept_at, raw_webhook_body, created_at FROM invoices WHERE td_wallet_label = ?`,
		label).Scan(&inv.ID, &inv.UserID, &inv.TDWalletLabel, &inv.TDWalletAddr, &inv.AmountUSDT, &inv.Days, &inv.Status, &inv.TDOrderID, &inv.ExpiresAt, &inv.ConfirmedAt, &inv.SweptAt, &inv.RawWebhookBody, &inv.CreatedAt)
	if err != nil {
		return nil, err
	}
	return &inv, nil
}

func (s *Store) UpdateInvoiceStatus(id, status string) error {
	_, err := s.db.Exec(`UPDATE invoices SET status = ? WHERE id = ?`, status, id)
	return err
}

func (s *Store) UpdateInvoiceConfirmation(id string, confirmedAt time.Time) error {
	_, err := s.db.Exec(`UPDATE invoices SET status = ?, confirmed_at = ? WHERE id = ?`,
		models.InvoiceStatusConfirmed, confirmedAt, id)
	return err
}

// ListInvoices returns all invoices for a given user ordered by created_at DESC.
func (s *Store) ListInvoices(userID int64) ([]models.Invoice, error) {
	rows, err := s.db.Query(`SELECT id, user_id, td_wallet_label, td_wallet_addr, amount_usdt, days, status, td_order_id, expires_at, confirmed_at, swept_at, raw_webhook_body, created_at FROM invoices WHERE user_id = ? ORDER BY created_at DESC`, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var out []models.Invoice
	for rows.Next() {
		var inv models.Invoice
		if err := rows.Scan(&inv.ID, &inv.UserID, &inv.TDWalletLabel, &inv.TDWalletAddr, &inv.AmountUSDT, &inv.Days, &inv.Status, &inv.TDOrderID, &inv.ExpiresAt, &inv.ConfirmedAt, &inv.SweptAt, &inv.RawWebhookBody, &inv.CreatedAt); err != nil {
			return nil, err
		}
		out = append(out, inv)
	}
	return out, nil
}

// ─── Webhook events ───────────────────────────────────────────────────────────

func (s *Store) CreateWebhookEvent(evt *models.WebhookEvent) error {
	_, err := s.db.Exec(
		`INSERT INTO webhook_events (invoice_id, event_type, td_tx_hash, raw_body, processed, received_at) VALUES (?, ?, ?, ?, ?, ?)`,
		evt.InvoiceID, evt.EventType, evt.TDTxHash, evt.RawBody, evt.Processed, evt.ReceivedAt,
	)
	return err
}
