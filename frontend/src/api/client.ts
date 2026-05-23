import type {
  LoginRequest, LoginResponse, HealthResponse,
  DeviceResponse, CreateDeviceRequest, CreateDeviceResponse,
  RevokeDeviceResponse, TrafficSummary,
  Invoice, CreateInvoiceRequest, CreateInvoiceResponse,
  SetCookieRequest
} from '@/types';

// ── Config ──────────────────────────────────────────────
const RAW_BASE = import.meta.env.VITE_API_BASE ?? '/proxy';
export const BASE_URL = RAW_BASE;

// ── Error type ──────────────────────────────────────────
function apiError(status: number, message: string): Error & { status: number } {
  const err = new Error(message);
  Object.defineProperty(err, 'status', { value: status, enumerable: false, writable: false });
  return err as Error & { status: number };
}

// ── Core fetch helper ───────────────────────────────────
async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init.headers ?? {}),
    },
    credentials: 'include',
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({} as Record<string, unknown>));
    throw apiError(res.status, (body as { error?: string }).error ?? res.statusText);
  }
  return res.json() as Promise<T>;
}

// ── Auth ────────────────────────────────────────────────
export const auth = {
  telegramLogin: (body: LoginRequest) =>
    request<LoginResponse>('/auth/telegram', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  setCookie: (token: string) =>
    request<{ status: string }>('/auth/cookie', {
      method: 'POST',
      body: JSON.stringify({ token } satisfies SetCookieRequest),
    }),

  health: () =>
    request<HealthResponse>('/health'),
};

// ── Devices ─────────────────────────────────────────────
export const devices = {
  list: () =>
    request<DeviceResponse[]>('/devices'),

  create: (body: CreateDeviceRequest) =>
    request<CreateDeviceResponse>('/devices', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  remove: (id: number) =>
    request<RevokeDeviceResponse>(`/devices/${id}`, { method: 'DELETE' }),

  traffic: (id: number, period: string) =>
    request<TrafficSummary>(`/devices/${id}/traffic?period=${period}`),

  // Raw text .conf — not JSON
  conf: async (id: number): Promise<string> => {
    const res = await fetch(`${BASE_URL}/devices/${id}/conf`, {
      credentials: 'include',
    });
    if (!res.ok) throw apiError(res.status, await res.text());
    return res.text();
  },
};

// ── Payments ────────────────────────────────────────────
export const payments = {
  createInvoice: (body: CreateInvoiceRequest) =>
    request<CreateInvoiceResponse>('/payments/invoice', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  listInvoices: () =>
    request<Invoice[]>('/payments/invoices'),
};
