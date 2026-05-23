# Implementation Plan — Phase A: Fixes + Payments + Integration

## Context from design

See `docs/plans/2026-05-23-phase-a-payments-integration-design.md`

---

## Prerequisites — read before starting

```
frontend/src/App.tsx              — HashRouter, AuthGuard, ProtectedRoute, ProtectedLayout, and all route definitions  
frontend/src/main.tsx             — only spokesperson for canvas; `window` writes and most first-order logic go in main.tsx  
frontend/src/api/client.ts        — see routes of automating. Config maps to routers. Auth/device/payment namespaces. ApiError class and `fetch` wrapper.  
frontend/src/types/index.ts        — All TypeScript DTOs.  
frontend/src/styles/global.css     — imports tokens. Glass utilities, spinner, skeleton, scrollbar, selection, :focus-visible.  
frontend/src/styles/tokens.css     — All CSS custom properties (colors, fonts, spacing, keyframes).  
frontend/src/hooks/useAuth.tsx     — AuthContext, `useAuth`, health-check with AbortController, logout clears `session` cookie.  
frontend/src/components/layout/AuthGuard.tsx — Redirect: when ` user is `null` and not `loading`, redirect `/login`. Now uses setTimeout → window.location.href.  
```

---

## Task A-1 · tsconfig baseUrl deprecation fix

- File: `frontend/tsconfig.app.json`  
- Add `"ignoreDeprecations": "6.0"` to `compilerOptions` (same level as `target`, `lib`, etc.)  
- Verify: `npx tsc -p tsconfig.app.json --noEmit` produces no TS5101 lines.

---

## Task A-2 · Tailwind dual-loader cleanup

- File: `frontend/src/main.tsx`  
- Block: remove the following lines (1-11):
  ```tsx
  // Tailwind v4 browser-runtime — no build step needed
  const twScript = document.createElement('script');
  twScript.src = 'https://unpkg.com/@tailwindcss/browser@4';
  twScript.async = true;
  document.head.appendChild(twScript);
  ```
- Keep all other imports and `ReactDOM.createRoot` call intact.

---

## Task A-3 · Dead code cleanup

- Delete `frontend/src/ctx-test.tsx`  
- Delete `frontend/src/__ctx_probe.tsx`

---

## Task A-4 · CreateDeviceModal .conf private key bug

- File: `frontend/src/components/modals/CreateDeviceModal.tsx`  
- Replace the hand-rolled .conf string block (lines 59-61) with...
  - Show the full `resp.conf` object in the WireGuard `.conf` INI format:
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
  - The `conf` object returned by `devices.create()` is the `CreateDeviceResponse['conf']` field — a `ClientConfig` with `privateKey` valid.  
- Add a "Copiar configuración" button alongside "Cerrar".  
- Validation: name must be non-empty before submit (already present).

---

## Task A-5 · Phase 6 — PaymentsPage

### A-5a · `usePayments` hook

- File: `frontend/src/hooks/usePayments.ts` (new)  
- Imports: `{ useState, useEffect, useCallback }` from `'react'`; `{ payments }` from `'@/api/client'`; types `CreateInvoiceRequest, CreateInvoiceResponse, Invoice`.  
- State:
  - `invoices: Invoice[]` — list  
  - `loading: boolean` — list loading  
  - `error: string` — list error  
- Exports:
  - `createInvoice(days: number): Promise<CreateInvoiceResponse>` — calls `payments.createInvoice({ days })`, no error throw. Sets `error` if rejected.  
  - `listInvoices(): Promise<void>` — single `payments.listInvoices()` call, stores result.  
  - `refreshInvoices: () => void`: same as `listInvoices`, used as the 60 s polling callback.  

- Verification: no lint error, narrow deps.

### A-5b · `InvoiceQRModal.tsx`

- File: `frontend/src/components/modals/InvoiceQRModal.tsx` (new)  
- Props: `{ open: boolean; onClose: () => void; qrData: string; amountUSDT: number; address: string; expiresAt: Date }`  
- Behavior:  
  - Modal overlay: `fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4`  
  - GlassCard centered, max-width 520px  
  - QR: `<img src={qrData} alt="QR de pago" className="rounded-xl" />` — data-URI from backend  
  - Countdown: `useEffect` with `setInterval(1000)` → compute `expiresAt - now` → format `mm:ss`. When ≤ 0, show "Factura expirada. Genera una nueva factura." and disable copy button.  
  - Copy address button: `navigator.clipboard.writeText(address)`, indicate "Copiado!" on success.  
  - Amount: `text-2xl font-display font-bold text-blue-400`  
  - Close button or backdrop click → `onClose()`.  
  - `AnimatePresence` with fade transition.

- Verification: narrow deps for `useCallback`/`useEffect`. No lint error.

### A-5c · `InvoiceHistoryModal.tsx`

- File: `frontend/src/components/modals/InvoiceHistoryModal.tsx` (new)  
- Props: `{ open: boolean; onClose: () => void; onSelectInvoice: (inv: Invoice) => void }`  
- Behavior:  
  - Fetches invoices via `usePayments` on mount; polls with `setInterval(refreshInvoices, 60_000)`.  
  - Renders glass table: columns = Fecha | Días | Monto (USDT) | Estado | —.  
  - Status badges: `pending/detected` → amber; `confirmed/notified` → green; `swept` → cyan; `expired/failed` → red.  
  - On row click: `onSelectInvoice(rowInv)` — parent shows invoice detail.  
  - Receives each row as a `<tr>` with `onClick={() => ...}`.

- Verification: Use `useRef`/`useEffect` for 60 s poll; no lint error. Narrow deps.

### A-5d · `PaymentsPage.tsx`

- File: `frontend/src/pages/PaymentsPage.tsx` (new)  
- Composition:
  - Header ("Pagos")  
  - Invoice creation form: range slider 1–60 days; amount display → `días × 0.06633 USDT/día`; "Generar factura" button → `createInvoice` → shows `InvoiceQRModal` on success.  
  - History button → shows `InvoiceHistoryModal`.  
  - Invoice history uses `usePayments`.  
  - Invoice detail panel: when `selectedInvoice` set, show full JSON inside `<pre>` in a `GlassCard`.  

- Verification: `AnimatedButton`, `GlassInput`, `spinner`, glass error banner like spec. Narrow deps.

---

## Task A-6 · Phase 7 — Integration polish

### A-6a · 404 NotFound route

- File: `frontend/src/App.tsx` (modify)  
- Component: `function NotFound() { return ... }`  
  - `glass rounded-2xl p-12 max-w-md w-full mx-auto mt-20 text-center`  
  - "Página no encontrada" heading → "Página no encontrada" 3xl `font-display font-bold text-blue-400`  
  - `AnimatedButton variant="ghost"` → `navigate('/')`  
  - Import `useNavigate` from `react-router-dom`.  
- `<Route path="*" element={<NotFound />} />` after all other routes.

### A-6b · ErrorBoundary wrapping HashRouter

- File: `frontend/src/App.tsx`  
- Import `ErrorBoundary` from `'@/components/feedback/ErrorBoundary'`  
- Wrap `<HashRouter>` with `<ErrorBoundary>`:  
  ```tsx
  <ErrorBoundary>
    <HashRouter>  …  </HashRouter>
  </ErrorBoundary>
  ```
- Import at top: `import ErrorBoundary from '@/components/feedback/ErrorBoundary';`

### A-6c · Responsive breakpoints

- File: `frontend/src/components/layout/Sidebar.tsx` (modify)  
- Add `useMediaQuery('(min-width: 640px)')` hook. Store result in `const isDesktop`.  
- Conditional: `isDesktop ? <aside …> : null`  
- For mobile: in `ProtectedLayout` (App.tsx), add a `hamburger` button → sets `drawerOpen` state → `<motion.div>` overlay with menu items.  
- Grids on `DashboardPage.tsx` and `LandingPage.tsx` already use responsive tailwind classes (`md:grid-cols-2`, `lg:grid-cols-4`). Verify no inline container overrides that break the grid at `text-[640px]`.  
- Modal widths: `.max-w-xs md:max-w-md lg:max-w-lg` pattern on modals.

### A-6d · Env vars `.env`

- File: `frontend/.env` (new)  
  ```
  VITE_API_BASE=http://localhost:8001/proxy
  ```
- `frontend/.env.example` (new) — template without real value:
  ```
  VITE_API_BASE=https://usipipo.dpdns.org/proxy
  ```

- No hardcoded URLs elsewhere besides these files. Check `client.ts` uses `import.meta.env.VITE_API_BASE` exclusively — already correct.

### A-6e · Final verification

```
cd frontend && npx tsc -p tsconfig.app.json --noEmit
cd frontend && npx vite build
```
- Zero errors. Build exits 0. No console warnings in dev console.

---

## Task A-7 · AuthGuard window.location → navigate()

- File: `frontend/src/components/layout/AuthGuard.tsx`  
- Import `useNavigate` from `react-router-dom`.  
- Replace `setTimeout(() => window.location.href = '/login', 300)` with `navigate('/login', { replace: true })`.  
- Remove the `setTimeout` wrapper entirely; call `navigate` synchronously inside the `useEffect` body.

---

## Acceptance criteria

- [ ] `npx tsc -p tsconfig.app.json --noEmit` produces no output (zero warnings and zero errors)
- [ ] `npx vite build` exits 0; no `[lightningcss] Unknown at rule: @extend` or any CSS warnings (lightningcss needs PostCSS for `@extend` or: acceptable if build output is correct).
- [ ] No `// TODO`, `// FIXME`, `// MVP` in any modified or new file.
- [ ] `npm run dev` starts cleanly; Tailwind classes render (no 404s from CDN).
- [ ] All new hooks/components receive thorough narrow-typed props; `as const`, `satisfies`, and `Omit<…, 'children'>` patterns used.
