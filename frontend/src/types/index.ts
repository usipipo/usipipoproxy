// =========================================================
// Core User
// =========================================================

export interface User {
  id: number;
  telegram_id: number;
  username?: string;
  first_name?: string;
  role: string;
  created_at: string;
  subscription_ends_at?: string;
  early_adopter: boolean;
}

// =========================================================
// Device
// =========================================================

export interface DeviceResponse {
  id: number;
  user_id: number;
  name: string;
  public_key: string;
  assigned_ip: string;
  psk?: string;
  enabled: boolean;
  bytes_rx: number;
  bytes_tx: number;
  created_at: string;
  last_seen_at?: string;
}

export interface ClientConfig {
  privateKey: string;
  address: string;
  dns: string;
  public_key: string;
  endpoint: string;
  allowed_ips: string;
  psk?: string;
}

export interface CreateDeviceResponse {
  device: DeviceResponse;
  conf: ClientConfig;
}

export interface CreateDeviceRequest {
  name: string;
  psk?: string;
}

export interface RevokeDeviceResponse {
  status: string;
  device_id: number;
  name: string;
}

// =========================================================
// Traffic
// =========================================================

export interface TrafficSummary {
  device_id: number;
  period: string;
  total_rx_gb: number;
  total_tx_gb: number;
  total_gb: number;
}

// =========================================================
// Auth
// =========================================================

export interface LoginRequest {
  id: number;
  username?: string;
  first_name: string;
  last_name?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

export interface LoginResponse {
  token: string;
  user: User;
  expires_at: number;
}

export interface AuthStatusResponse {
  authenticated: boolean;
  user?: User;
}

export interface SetCookieRequest {
  token: string;
}

// =========================================================
// Health
// =========================================================

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

// =========================================================
// Payments / Invoices
// =========================================================

export type InvoiceStatus = "pending" | "confirmed" | "expired" | "failed" | "partial";

export interface Invoice {
  id: string;
  user_id: number;
  td_wallet_label: string;
  td_wallet_addr: string;
  amount_usdt: number;
  days: number;
  status: InvoiceStatus;
  td_order_id?: string;
  expires_at: string;
  confirmed_at?: string;
  swept_at?: string;
  created_at: string;
}

export interface CreateInvoiceRequest {
  days: number;
}

export interface CreateInvoiceResponse {
  invoice_uuid: string;
  address: string;
  amount_usdt: number;
  qr_data: string;
  expires_at: Date;
  days: number;
}

// =========================================================
// Webhooks (internal — TronDealer sends these)
// =========================================================

export type TronDealerWebhookEvent =
  | "payment.notified"
  | "payment.swept"
  | "wallet.expired";

export interface TronDealerWebhookPayload {
  event: TronDealerWebhookEvent;
  label: string;
  to_address: string;
  amount: number;
  asset: string;
  network: string;
  tx_hash: string;
  confirmations: number;
  received_at?: string;
}

// ── Barrel re-exports ───────────────────────────────────
export type { AuthStatusResponse, SetCookieRequest };
