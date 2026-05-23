# Design: Phase A Fixes + Phase 6 Payments + Phase 7 Integration

> Project: uSipipo Proxy Frontend
> Date: 2026-05-23
> Status: Approved

---

## A-1 · TypeScript baseUrl deprecation

`tsconfig.app.json:25` — `baseUrl: "."` deprecated in TS 6. Build passes but warns under `tsc`. CI floods with TS5101.

**Fix:** Add `"ignoreDeprecations": "6.0"` to `compilerOptions`.

---

## A-2 · Tailwind dual-loader conflict

`main.tsx` injects `@tailwindcss/browser@4` script at runtime. `vite.config.ts` uses `@tailwindcss/vite` build plugin. Both process the same CSS. Works by accident but is architecturally wrong.

**Fix:** Remove browser script injection from `main.tsx`. Keep `@tailwindcss/vite` as sole Tailwind engine — standard v4 dev+prod setup.

---

## A-3 · Dead files

`frontend/src/ctx-test.tsx` and `frontend/src/__ctx_probe.tsx` — neither imported anywhere. `ctx-test.tsx` calls undefined `useCtx()` — fails if ever imported.

**Fix:** Delete both files.

---

## A-4 · CreateDeviceModal .conf — private key silently dropped

`CreateDeviceModal.tsx:59-61` manually concatenates fields but never shows `conf.privateKey`. Resulting .conf is non-functional — user cannot connect WireGuard client.

**Fix:** Render actual WireGuard `.conf` format:
```ini
[Interface]
PrivateKey = {conf.privateKey}
Address = {conf.address}
DNS = {conf.dns}

[Peer]
PublicKey = {conf.public_key}
PresharedKey = {conf.psk}
Endpoint = {conf.endpoint}
AllowedIPs = {conf.allowed_ips}
```

---

## A-5 · Phase 6 — PaymentsPage

### 5.1 Architecture

```
frontend/src/pages/PaymentsPage.tsx       — top-level page
frontend/src/hooks/usePayments.ts         — usePayments hook (createInvoice + listInvoices)
frontend/src/components/modals/InvoiceQRModal.tsx        — QR + countdown
frontend/src/components/modals/InvoiceHistoryModal.tsx  — history + detail
```

### 5.2 Data flow (TronDealer V2)

1. User selects 1–60 days via range slider
2. `monto = días × 0.06633 USDT/día` (early_adopter discount applied server-side)
3. `POST /proxy/payments/invoice { days }` → backend calls TronDealer → returns `CreateInvoiceResponse`
4. Response fields: `invoice_uuid`, `address`, `amount_usdt`, `qr_data` (data-URI), `expires_at`, `days`
5. Frontend renders `InvoiceQRModal` with QR + copy-address + countdown

### 5.3 InvoiceQRModal

- QR image: `<img src={qr_data} alt="Scan to pay" />`
- Countdown: `setInterval` every 1s → `expires_at - now`
- Expired: show "Factura expirada", disable copy button
- Copy: `navigator.clipboard.writeText(address)`

### 5.4 InvoiceHistoryModal

- Table fetched on mount via `usePayments`
- Polls every 60s
- Status badges:
  | State | Color |
  |-------|-------|
  | `pending` / `detected` | amber |
  | `confirmed` / `notified` | green |
  | `swept` | cyan |
  | `expired` / `failed` | red |
- Row click: JSON detail panel with full invoice data in `<pre>`

---

## A-6 · Phase 7 — Integration polish

| Task | Action |
|------|--------|
| 404 route (hash: `*`) | `<Route path="*" element={<NotFound />} />` — glass card centered |
| ErrorBoundary in App | Wrap entire `<HashRouter>` with `<ErrorBoundary>` in `App.tsx` |
| Skeleton screens | `.skeleton` class + `<SkeletonCard>` — show while any async fetch pending |
| Responsive | `useMediaQuery('(min-width: 640px)')` hook — hide Sidebar on <640px, grid 1-col on mobile |
| Env vars | `frontend/.env`: `VITE_API_BASE=http://localhost:8001/proxy` |
| `tsc --noEmit` | After all changes: zero errors, zero warnings |

---

## A-7 · AuthGuard redirect

`AuthGuard.tsx:18` uses `setTimeout(() => window.location.href = '/login', 300)` — full page reload, loses SPA state.

**Fix:** Import `useNavigate`, call `navigate('/login', { replace: true })`.

---

## Open questions (answered)

1. **PaymentsPage route** — yes, add `<Route path="/payments" element={<PaymentsPage />} />` inside `AuthGuard`/`ProtectedLayout`.
2. **@keyframes shimmer** — `tokens.css` already has it; keep there. `global.css` just imports `tokens.css`.
3. **Tailwind cleanup** — yes, remove `@tailwindcss/browser@4` script from `main.tsx`, keep `@tailwindcss/vite` only.
