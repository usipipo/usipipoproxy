# uSipipo Proxy — Frontend Implementation Plan

> **Project:** uSipipo Proxy Frontend  
> **Tech stack:** Vite + React 19 + TypeScript + Tailwind CSS v4 + Framer Motion  
> **Base directory:** `frontend/`  
> **Emotion goal:** Tecnológico y confiable  
> **Design language:** Glassmorphism dark mode · Electric Blue · Bento Grid

---

## Design System Specification

### 1. Architecture: Why Tailwind v4 + Framer Motion

- **Tailwind v4** (browser-runtime) provides the entire utility surface without a build step for CSS classes. All the color, spacing, and glass-surface utilities are defined as CSS custom properties in `:root` and consumed as Tailwind utilities via `@theme` configuration (or browser-runtime `<script>` setup). No pre-compilation of Tailwind utilities is needed — the JS runtime maps class names to CSS variables at render time.
- **Framer Motion** provides motion primitives (`motion.div`, `motion.section`) that integrate seamlessly with React 19 concurrent rendering, unlike imperative GSAP or `useEffect`-driven animation libraries.
- This approach keeps every visual decision in one place: `src/styles/tokens.css`.

### 2. Color Palette (CSS Custom Properties)

```css
:root {
  /* Surfaces */
  --color-bg-0: #050a14;       /* Deepest background */
  --color-bg-1: #0d1321;       /* Body background */
  --color-bg-2: #131c31;       /* Section elevation 1 */
  --color-bg-3: #1a2540;       /* Section elevation 2 */

  /* Glass surfaces */
  --glass-bg: rgba(13, 19, 33, 0.65);
  --glass-border: rgba(59, 130, 246, 0.15);
  --glass-highlight: rgba(59, 130, 246, 0.08);
  --glass-blur: blur(20px) saturate(160%);

  /* Primary — Electric Blue */
  --color-primary-50:  #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-200: #bfdbfe;
  --color-primary-300: #93c5fd;
  --color-primary-400: #60a5fa;
  --color-primary-500: #3b82f6;   /* MAIN */
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  --color-primary-800: #1e40af;
  --color-primary-900: #1e3a8a;

  /* Accent — cyan highlight */
  --color-accent: #06d6a0;

  /* Text */
  --color-text-1: #f0f4ff;       /* Primary text */
  --color-text-2: #8896b3;       /* Secondary text */
  --color-text-3: #4f6391;       /* Tertiary text */

  /* Status */
  --status-ok:   #06d6a0;
  --status-warn: #f59e0b;
  --status-err:  #ef4444;

  /* Glows */
  --glow-primary: 0 0 24px rgba(59, 130, 246, 0.35);
  --glow-accent:  0 0 24px rgba(6, 214, 160, 0.25);
  --glow-error:   0 0 16px rgba(239, 68, 68, 0.30);
}
```

### 3. Typography Tokens

```
Space Grotesk  →  Headings / display
DM Sans        →  Body / UI

--font-display: 'Space Grotesk', system-ui, sans-serif;
--font-body:    'DM Sans', system-ui, sans-serif;
--font-mono:    'JetBrains Mono', 'Fira Code', monospace;

Size scale (rem, base 16 px):
  text-xs    0.75rem  / 12px
  text-sm    0.875rem / 14px
  text-base  1rem     / 16px
  text-lg    1.125rem / 18px
  text-xl    1.25rem  / 20px
  text-2xl   1.5rem   / 24px
  text-3xl   1.875rem / 30px
  text-4xl   2.25rem  / 36px
  text-5xl   3rem     / 48px
  text-6xl   3.75rem  / 60px

Line-height: headings 1.15, body 1.6
Letter-spacing: headings -0.02em
```

### 4. Spacing Scale

```
--space-05:  0.125rem  (2px)
--space-1:   0.25rem   (4px)
--space-2:   0.5rem    (8px)
--space-3:   0.75rem   (12px)
--space-4:   1rem      (16px)
--space-5:   1.25rem   (20px)
--space-6:   1.5rem    (24px)
--space-8:   2rem      (32px)
--space-10:  2.5rem    (40px)
--space-12:  3rem      (48px)
--space-16:  4rem      (64px)
--space-20:  5rem      (80px)
--space-24:  6rem      (96px)
```

### 5. Glass Surface Utilities

```css
.glass {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
}

.glass-card {
  @extend .glass;
  padding: var(--space-6);
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
  border-color: rgba(59, 130, 246, 0.30);
  box-shadow: var(--glow-primary);
}

.glass-input {
  background: rgba(19, 28, 49, 0.80);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(59, 130, 246, 0.12);
  border-radius: 10px;
  color: var(--color-text-1);
}
.glass-input:focus {
  outline: none;
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}
```

### 6. Animation Presets (Framer Motion)

```tsx
// Fade up — for section and card reveal
const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.6, ease: [0.22, 1, 0.36, 1] }
  })
};

// Stagger container — for bento grid and list items
const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.15 }
  }
};

// Parallax blob — for background decorative orbs
const blobParallax = {
  rest:  { x: 0, y: 0, scale: 1 },
  hover: { scale: 1.05 },
  parallax: (offsetY: number) => ({
    y: offsetY * 0.25,
    transition: { ease: 'none' }
  })
};

// Button hover — magnetic-ish scale + glow
const buttonHover = {
  scale: 1.03,
  boxShadow: '0 0 20px rgba(59,130,246,0.45)',
  transition: { type: 'spring', stiffness: 400, damping: 25 }
};

// Exit animation
const fadeExit = {
  hidden: { opacity: 0, y: -10 },
  visible: { opacity: 1, y: 0 }
};
```

---

## Directory Layout After All Phases

```
frontend/
  src/
    api/
      client.ts              — HTTP client with base URL + auth injection
      auth.ts                — Login, cookie, logout
      devices.ts             — CRUD + traffic
      payments.ts            — Invoice creation, list
      health.ts              — Health ping
    types/
      index.ts               — All TypeScript interfaces
    hooks/
      useAuth.ts             — Auth state + login/logout helpers
      useDevices.ts          — Devices CRUD hook
      usePayments.ts         — Payments + invoice hooks
      useToast.ts            — Toast notification system
    components/
      layout/
        Sidebar.tsx
        Navbar.tsx
      glass/
        GlassCard.tsx
        GlassSurface.tsx
      buttons/
        AnimatedButton.tsx
        GhostButton.tsx
      form/
        GlassInput.tsx
        GlassSelect.tsx
      feedback/
        ScrollReveal.tsx
        Spinner.tsx
        Toast.tsx
        ErrorBoundary.tsx
      modals/
        Modal.tsx
        CreateDeviceModal.tsx
        InvoiceQRModal.tsx
    pages/
      LandingPage.tsx
      LoginPage.tsx
      DashboardPage.tsx
      DevicesPage.tsx
      PaymentsPage.tsx
    styles/
      tokens.css              — Design token CSS custom properties
      global.css              — Tailwind v4 directives, resets, utilities
      animations.css          — Reusable @keyframes (only; Framer Motion handles JS-driven motion)
    App.tsx
    main.tsx
    vite.config.ts
  index.html
  tsconfig.json
```

---

## Phase 0 — API Client + Types (Foundational)

**Goal:** Establish the typed HTTP layer before any UI code is written. All phases depend on this layer.

### Task 0.1 — TypeScript type definitions

**Files:** `src/types/index.ts` (new)

**Implementation:**
Copy the full type block from the spec into `src/types/index.ts`. No modifications. Add one export alias per type:

```ts
export type { /* all */ };
```

**Acceptance criteria:**
- `tsc --noEmit` produces zero errors
- Every type from the spec is exported exactly once
- No `any` types present

### Task 0.2 — API client (`src/api/client.ts`)

**Files:** `src/api/client.ts` (new)

**Implementation:**
```ts
const BASE_URL = import.meta.env.VITE_API_BASE ?? '/proxy';

class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

async function request<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...opts,
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    credentials: 'include',   // send HttpOnly cookie automatically
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, (body as any).error ?? res.statusText);
  }
  return res.json();
}

export const api = {
  // auth
  telegramLogin: (body: LoginRequest) =>
    request<LoginResponse>('/auth/telegram', { method: 'POST', body: JSON.stringify(body) }),
  setCookie:       (token: string) =>
    request<{status: string}>('/auth/cookie', { method: 'POST', body: JSON.stringify({ token }) }),
  health:          ()                => request<HealthResponse>('/health'),

  // devices
  listDevices:  ()                => request<DeviceResponse[]>('/devices'),
  createDevice: (body: CreateDeviceRequest) =>
    request<CreateDeviceResponse>('/devices', { method: 'POST', body: JSON.stringify(body) }),
  deleteDevice: (id: number) =>
    request<RevokeDeviceResponse>(`/devices/${id}`, { method: 'DELETE' }),
  getTraffic:   (id: number, period: string) =>
    request<TrafficSummary>(`/devices/${id}/traffic?period=${period}`),
  getConf:      (id: number) =>
    fetch(`${BASE_URL}/devices/${id}/conf`, { credentials: 'include' }).then(r => r.text()),

  // payments
  createInvoice: (body: CreateInvoiceRequest) =>
    request<CreateInvoiceResponse>('/payments/invoice', { method: 'POST', body: JSON.stringify(body) }),
  listInvoices:  ()                => request<Invoice[]>('/payments/invoices'),
};

export { ApiError };
```

**Acceptance criteria:**
- All 8 API routes implemented with correct HTTP methods
- `credentials: 'include'` on every request to send HttpOnly cookie
- `ApiError` carries `status` and `message`
- No hardcoded base URL outside `import.meta.env`

### Task 0.3 — Auth module (`src/api/auth.ts`)

**Files:** `src/api/auth.ts` (new)

**Implementation:**
```ts
import { api } from './client';

export async function loginWithTelegram(data: LoginRequest) {
  const res = await api.telegramLogin(data);
  await api.setCookie(res.token);
  return res;
}
```

Acceptance criteria:
- `loginWithTelegram` exchanges Telegram data for JWT then calls `/auth/cookie`
- Returns `LoginResponse` to caller

---

## Phase 1 — Design Tokens + Global CSS

**Goal:** A single-file, non-readable CSS setup that powers every component in the app. No per-component style files.

### Task 1.1 — `src/styles/tokens.css`

**Files:** `src/styles/tokens.css` (new)

**Implementation:**
Paste the exact CSS custom properties block from §2, §3, §4, §5 of the Design System Specification. Add:

```css
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

:root {
  --font-display: 'Space Grotesk', system-ui, sans-serif;
  --font-body:    'DM Sans', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', 'Fira Code', monospace;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }

body {
  font-family: var(--font-body);
  background: var(--color-bg-0);
  color: var(--color-text-1);
  line-height: 1.6;
  min-height: 100vh;
  overflow-x: hidden;
}
```

**Acceptance criteria:**
- File is ≤ 200 lines
- All color tokens from §2 are present with correct values
- Google Fonts import present
- `body` sets `overflow-x: hidden`

### Task 1.2 — `src/styles/global.css`

**Files:** `src/styles/global.css` (new)

**Implementation:**
```css
@import './tokens.css';

/* Tailwind v4 — browser-runtime import (loaded dynamically in main.tsx) */

/* Utility: glass surface */
.glass {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
}

/* Utility: glass card */
.glass-card {
  @extend .glass;
  padding: var(--space-6);
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
  border-color: rgba(59, 130, 246, 0.30);
  box-shadow: var(--glow-primary);
}

/* Utility: glass input */
.glass-input {
  background: rgba(19, 28, 49, 0.80);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(59, 130, 246, 0.12);
  border-radius: 10px;
  color: var(--color-text-1);
  font-family: var(--font-body);
  padding: var(--space-3) var(--space-4);
  width: 100%;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.glass-input:focus {
  outline: none;
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--color-bg-1); }
::-webkit-scrollbar-thumb { background: var(--color-text-3); border-radius: 3px; }

/* Selection */
::selection { background: rgba(59, 130, 246, 0.30); color: var(--color-text-1); }
```

**Acceptance criteria:**
- Imports `tokens.css` first
- `.glass-card` hover emits `--glow-primary`
- `::selection` uses primary blue tint
- Scrollbar matches dark theme

### Task 1.3 — Tailwind v4 browser-runtime setup in `main.tsx`

**Files:** `src/main.tsx` (modify)

**Implementation:**
Update `main.tsx` to include Tailwind v4 browser-runtime before React renders:

```tsx
import './styles/global.css';

// Tailwind v4 browser-runtime: inject <script src="…tailwindcss…">
const twScript = document.createElement('script');
twScript.src = 'https://unpkg.com/@tailwindcss/browser@4';
twScript.async = true;
document.head.appendChild(twScript);
```

Also update `index.html` to load React from CDN with type="module" for browser ESM (Vite handles this, no change needed to `index.html`).

**Acceptance criteria:**
- Tailwind utilities like `className="flex gap-4"` work immediately on page load
- No build step required for Tailwind classes
- `npm run dev` starts cleanly with zero configuration errors

---

## Phase 2 — Reusable Components

**Goal:** Build the atom-level component library that all pages consume. No layout or page logic here — pure presentational components.

### Task 2.1 — `GlassCard` (`src/components/glass/GlassCard.tsx`)

```tsx
import { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface Props {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'hover-glow' | 'flat';
  as?: keyof JSX.IntrinsicElements;
}

export default function GlassCard({ children, className = '', variant = 'default', as: Tag = 'div' }: Props) {
  const variants = {
    default: 'glass glass-card',
    'hover-glow': 'glass glass-card',
    flat: 'glass', // no glow on hover
  };
  return (
    <Tag as={Tag} className={`${variants[variant]} ${className}`}>
      {children}
    </Tag>
  );
}
```

**Acceptance criteria:**
- Renders on any HTML tag via `as` prop
- `hover-glow` variant only — consistent brand behavior

### Task 2.2 — `AnimatedButton` (`src/components/buttons/AnimatedButton.tsx`)

```tsx
import { ButtonHTMLAttributes, ReactNode } from 'react';
import { motion } from 'framer-motion';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

const sizeClass = { sm: 'px-3 py-1.5 text-sm', md: 'px-5 py-2.5 text-base', lg: 'px-7 py-3.5 text-lg' };
const variantClass = {
  primary: 'bg-blue-600 text-white hover:bg-blue-500',
  ghost:   'bg-transparent border border-blue-500/30 text-blue-400 hover:bg-blue-500/10',
  danger:  'bg-red-600/80 text-white hover:bg-red-500',
};

export default function AnimatedButton({ children, variant = 'primary', size = 'md', className = '', ...rest }: Props) {
  return (
    <motion.button
      whileHover={buttonHover}
      whileTap={{ scale: 0.97 }}
      className={`
        rounded-xl font-semibold font-body cursor-pointer
        disabled:opacity-40 disabled:cursor-not-allowed
        ${sizeClass[size]} ${variantClass[variant]} ${className}
      `}
      {...rest}
    >
      {children}
    </motion.button>
  );
}
```

**Acceptance criteria:**
- Three variants render distinct styles
- `whileHover` applies glow + scale; `whileTap` shrinks
- All standard `<button>` props pass through

### Task 2.3 — `ScrollReveal` (`src/components/feedback/ScrollReveal.tsx`)

```tsx
'use client';
import { ReactNode } from 'react';
import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';

interface Props {
  children: ReactNode;
  delay?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
}

export default function ScrollReveal({ children, delay = 0, direction = 'up' }: Props) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });

  const hiddenMap = { up: { opacity: 0, y: 40 }, down: { opacity: 0, y: -40 }, left: { opacity: 0, x: -40 }, right: { opacity: 0, x: 40 } };

  return (
    <motion.div
      ref={ref}
      initial={hiddenMap[direction]}
      animate={isInView ? { opacity: 1, x: 0, y: 0 } : hiddenMap[direction]}
      transition={{ duration: 0.65, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}
```

**Acceptance criteria:**
- Triggers only once (`once: true`) when 80px from viewport edge
- Supports four entry directions
- Children render inside a single FP layer

### Task 2.4 — `Sidebar` (`src/components/layout/Sidebar.tsx`)

```tsx
'use client';
import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link'; // will replace with react-router-dom hash links

const navItems = [
  { label: 'Inicio', href: '#/' },
  { label: 'Panel', href: '#/dashboard' },
  { label: 'Dispositivos', href: '#/devices' },
  { label: 'Pagos', href: '#/payments' },
];

export default function Sidebar({ active }: { active: string }) {
  return (
    <motion.aside
      initial={{ x: -60, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="fixed left-0 top-0 h-full w-60 glass border-r border-blue-500/10 z-40 flex flex-col p-6"
    >
      {/* Logo */}
      <div className="text-2xl font-bold font-display text-blue-400 mb-10 tracking-tight">
        uSipipo
      </div>
      <nav className="flex flex-col gap-2">
        {navItems.map(item => (
          <Link
            key={item.href}
            href={item.href}
            className={`
              px-4 py-2.5 rounded-xl text-sm font-medium transition-all
              ${active === item.label
                ? 'bg-blue-600/20 text-blue-300 border border-blue-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-blue-500/5'}
            `}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="mt-auto pt-6 border-t border-blue-500/10">
        <span className="text-xs text-slate-500 block">Versión 1.0.0</span>
      </div>
    </motion.aside>
  );
}
```

**Acceptance criteria:**
- Desktop: fixed left sidebar ; mobile: hidden → replaced by hamburger (waits Phase 4 on skipping this — see §responsive)
- Logo uses `--color-primary-400` via Tailwind `text-blue-400` 
- Active nav item highlighted with blue tint
- version footer shows `1.0.0`

### Task 2.5 — `GlassInput` and `GlassSelect`

**Files:** `src/components/form/GlassInput.tsx`, `src/components/form/GlassSelect.tsx` (new)

Both wrap native `<input>` / `<select>` with the `.glass-input` class. They forward all props via `{...rest}`.

**Acceptance criteria:**
- Margin/className props accepted
- Floating label variant in GlassInput via `label` prop + peer selector

### Task 2.6 — `Spinner` and `ErrorBoundary`

**Files:** `src/components/feedback/Spinner.tsx`, `src/components/feedback/ErrorBoundary.tsx` (new)

- **Spinner:** CSS rotation animation; 32px blue ring; no JS animation library.  
- **ErrorBoundary:** Class component with `componentDidCatch`; renders a retry card with `AnimatedButton` inside.

**Acceptance criteria:**
- Spinner: pure CSS keyframe `spin`; zero Framer Motion
- ErrorBoundary: catch errors in subtree and render recovery UI

---

## Phase 3 — Auth System

**Goal:** Complete Telegram Login Web App authentication flow with JWT → HttpOnly cookie, auth guard, logout, and protected page routing.

### 3.1 Auth flow sequence (exact)

```
┌─────────────────────┐
│  Telegram Web App   │  TelegaMiniApp SDK
│  (simulates data)   │
└──────────┬──────────┘
           │ 1. User opens /login
           │    Telegram widget triggers callback with auth_data
           ▼
┌────────────────────────────────────────────────┐
│  LoginPage.tsx                                  │
│  Receives LoginRequest object                   │
│  { id, first_name, last_name?, username?,       │
│    photo_url?, auth_date, hash }                │
└──────────┬─────────────────────────────────────┘
           │ 2. onSubmit → call api.auth.telegramLogin(data)
           ▼
┌────────────────────────────────────────────────┐
│  POST /proxy/auth/telegram  (JWT HS256 HMAC     │
│    verification of data_check_string by backend) │
│  → { token, user, expires_at }                  │
└──────────┬─────────────────────────────────────┘
           │ 3. Call api.setCookie(token)           │ api.auth.setCookie
           ▼
┌────────────────────────────────────────────────┐
│  POST /proxy/auth/cookie                        │
│  Backend: Set-Cookie: token=<JWT>; HttpOnly;    │
│    Path=/; Secure; SameSite=Lax                 │
│  → { status: "ok" }                             │
└──────────┬─────────────────────────────────────┘
           │ 4. Cookie stored by browser (HttpOnly)
           │    Future requests auto-send via credentials: 'include'
           ▼
┌────────────────────────────────────────────────┐
│  useAuth hook sets authenticated=true            │
│  App routes to /dashboard                       │
└─────────────────────────────────────┬──────────┘
                                       │
┌─────────────────────────────────────▼───┐
│  Every subsequent API                    │
│  call sends Cookie header automatically   │
│  Backend validates JWT from Cookie        │
└──────────────────────────────────────┬───┘ │
                                           │   │
│  Logout                                 │   │
│  → DELETE /auth/cookie (optional) ──────┘   │
│  → setCookie('', { expires: -1 }) in client  │
└────────────────────────────────────────────────┘
```

### Task 3.1 — `useAuth` hook (`src/hooks/useAuth.ts`)

**Implementation:**
```tsx
'use client';
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '@/api/client';
import type { User } from '@/types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: () => void;           // triggers Telegram widget
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({ user: null, loading: true, login: () => {}, logout: async () => {} });

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser]   = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api.health().then(r => { if (!cancelled) { setUser({ id: 0, telegram_id: 0, role: '', created_at: '', early_adopter: false } as User); setLoading(false); }})
        .catch(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  const logout = async () => {
    // clear client-side cookie
    document.cookie = 'token=; Max-Age=0; path=/;';
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login: () => window.open('/login', '_blank'), logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

**Acceptance criteria:**
- Context loads immediately, pings `/health`, sets `loading=false` on response
- `logout` clears cookie and sets `user=null`
- Hook accessible across any component

### Task 3.2 — `AuthGuard` component (`src/components/layout/AuthGuard.tsx`)

**Implementation:**
```tsx
'use client';
import { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/api/client';

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const [ok, setOk] = useState(false);

  // Re-check session health on mount to catch legitimate sessions missed by Context init
  useEffect(() => {
    if (!loading) {
      api.health().then(() => setOk(true)).catch(() => setOk(false));
    }
  }, [loading]);

  if (loading || !ok) {
    return <div className="flex items-center justify-center min-h-screen"><Spinner /></div>;
  }
  return <>{children}</>;
}
```

**Acceptance criteria:**
- Spinner shows while auth initialises
- Redirects to `/login` if session unavailable
- No layout shift during loading (full-viewport fallback)

### Task 3.3 — Login page (`src/pages/LoginPage.tsx`)

**Implementation:**
```tsx
'use client';
import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom'; // step 3.4 manages routing
import { api } from '@/api/client';
import type { LoginRequest } from '@/types';

export default function LoginPage() {
  const navigate = useNavigate();
  const [error, setError] = useState('');

  // Real implementation: Telegram Mini App SDK calls this
  const handleTelegramAuth = useCallback(async (authData: LoginRequest) => {
    try {
      const res = await api.loginWithTelegram(authData);
      // store user info
      sessionStorage.setItem('usipipo_user', JSON.stringify(res.user));
      navigate('/#/dashboard', { replace: true });
    } catch (e: any) {
      setError(e.message ?? 'Error de autenticación');
    }
  }, [navigate]);

  // TEMPORARY: mock button for development without Telegram environment
  const mockLogin = async () => {
    await handleTelegramAuth({
      id: 123456789,
      first_name: 'Test',
      last_name: 'User',
      username: 'testuser',
      auth_date: Math.floor(Date.now() / 1000),
      hash: 'mock_hash_development_only',
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden"
    >
      {/* animated background blobs */}
      <div className="absolute inset-0 pointer-events-none">
        <motion.div
          animate={blobParallax.rest}
          className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-gradient-to-br from-blue-600/20 to-cyan-500/10 blur-3xl"
        />
        <motion.div
          animate={{ x: [0, 30, 0], y: [0, -20, 0], scale: [1, 1.1, 1] }}
          transition={{ repeat: Infinity, duration: 14, ease: 'linear' }}
          className="absolute bottom-20 -left-20 w-80 h-80 rounded-full bg-gradient-to-br from-indigo-600/15 to-blue-600/10 blur-3xl"
        />
      </div>

      <motion.div
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.7 }}
        className="glass rounded-2xl p-10 w-full max-w-md relative z-10"
      >
        <h1 className="text-3xl font-display font-bold text-blue-400 mb-2">Bienvenido</h1>
        <p className="text-slate-400 mb-8 text-sm">Accede a tu VPN WireGuard segura.</p>

        {error && <div className="bg-red-500/10 border border-red-500/25 rounded-xl px-4 py-3 text-red-400 text-sm mb-5">{error}</div>}

        <AnimatedButton variant="primary" size="lg" className="w-full mb-4"
          onClick={mockLogin}
        >
          Entrar con Telegram
        </AnimatedButton>
        <p className="text-xs text-slate-500 text-center">
          Al entrar aceptas los términos de servicio y la política de privacidad.
        </p>
      </motion.div>
    </motion.div>
  );
}
```

**Acceptance criteria:**
- Page renders with glass card centered on viewport
- Two parallax blobs animated in background (motion loop)
- Mock login button triggers full auth flow
- Real production: replaces mock with Telegram Mini App SDK callback
- Error bubble shows red glass card on auth failure
- Apostas: buttons with `AnimatedButton`

### Task 3.4 — Routing setup (`src/App.tsx`)

**Files:** `src/App.tsx` (replace default)

**Implementation:**
Install `react-router-dom` v6. Use hash-based routing (SPA via Caddy reverse proxy). Hash router required because:

1. Caddy only serves `/index.html` for missing-proxy 404 responses; clean URLs at `/dashboard` would fetch `/dashboard` directly and return the dist `index.html` instead — but `/dashboard` is handled at build-time (Vite prod build might still need fallback handling; better safe with `#/dashboard` hash-style paths).
2. History API client routes break behind HTTP-to-HTTPS redirects in Caddy unless full fallback matching (`try_files`) is set — avoid that dependency with hash routing.

```tsx
import { HashRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import AuthGuard from './components/layout/AuthGuard';
import Sidebar    from './components/layout/Sidebar';
import LoginPage  from './pages/LoginPage';
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';
import DevicesPage   from './pages/DevicesPage';
import PaymentsPage  from './pages/PaymentsPage';

function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="ml-60 flex-1 p-8">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <HashRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route element={<AuthGuard><AppLayout /></AuthGuard>}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/devices"  element={<DevicesPage />} />
            <Route path="/payments" element={<PaymentsPage />} />
          </Route>
        </Routes>
      </HashRouter>
    </AuthProvider>
  );
}
```

Route suggestions:
- `/` — Landing page (public)
- `/login` — Telegram login
- `/dashboard` — Summary + recent activity
- `/devices` — Device management + traffic
- `/payments` — Invoice creation + history

**Acceptance criteria:**
- Unauthenticated user hitting `/dashboard` redirects to `/login`
- `/login` never shows sidebar
- All protected routes wrapped by `AuthGuard`
- Hash-based routing works on plain HTTP under Caddy

---

## Phase 4 — Landing Page

**Goal:** A hero section, bento-grid feature cards, a three-step explanation, pricing cards, and footer. All animations driven by Framer Motion.

### Task 4.1 — Hero section (`src/pages/LandingPage.tsx`)

**Implementation details:**
- Full-viewport height (`min-h-screen`)
- Left column: heading (`text-5xl font-display font-bold text-blue-400`), subtext (`text-slate-400`), primary CTA (`AnimatedButton`), secondary link to `/login`
- Right column: floating 3-D wireframe / visual hint or brand mark
- Two parallax blobs (motion loop) behind content
- Stagger `fadeUp` on heading → subtext → buttons

**Layout:**
```
+------------------------------------------+
| [Sidebar logo]                           |
|                                          |
|   [Orb]   uSipipo Proxy     [Bento grid] |
|            hero CTA                        |
+------------------------------------------+
```

**Acceptance criteria:**
- Hero background uses gradient blob animation with `animate={{ scale: [1, 1.15, 1], opacity: [0.4, 0.7, 0.4] }}` (loop 14 s)
- CTA button navigates to `/login` via `useNavigate()`
- Mobile: columns stack vertically, blobs reposition

### Task 4.2 — Features bento grid

**Features (6 cards, 2 × 3 grid on desktop):**
1. **WireGuard VPN** — icon + short title + body glass card
2. **Suscripción prepagada** — billing in USDT BEP-20
3. **Auto-sweep** — TronDealer wallet sweep
4. **Gestión de dispositivos** — add / revoke / traffic
5. **Telegram Login** — no passwords, one tap
6. **Dashboard en tiempo real** — traffic meter

**Implementation:**
- Use `<motion.div variants={staggerContainer} initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-100px' }}>` as grid wrapper
- Each card: `variants={fadeUp}` custom `i` index for stagger
- Grid: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`

**Acceptance criteria:**
- Cards stagger in on scroll
- `.glass-card:hover` emits glow
- Icons from `react-icons` or SVG inline (no image dependencies)

### Task 4.3 — Three-step section

**Steps:**
1. **Regístrate** — click "Entrar con Telegram"
2. **Crea tu VPN** — add dispositivo WireGuard, genera .conf
3. **Conéctate** — carga .conf en cliente, navega libre

Implementation: horizontal timeline on desktop (`flex gap-8`), stacked on mobile. Arrow animation between steps (`motion.path` or CSS keyframe).

**Acceptance criteria:**
- Step icons animate with `whileInView`
- Arrow shifts between steps on mobile

### Task 4.4 — Pricing cards

Two tiers:
| Plan      | Precio         | Incluye              |
|-----------|----------------|----------------------|
| Básico    | 0.066 USDT/día | Dispositivo ilimitado, tráfico ilimitado |
| Early Adopter | 0.014 USDT/día | hosting 80% descuento |

Pricing cards must use `#3b82f6` accent borders; CTA navigates to `/payments`.

**Acceptance criteria:**
- "Early Adopter" card highlighted with `--glow-primary` and subtle blue border
- Both CTA buttons navigate to `/payments` hash path

### Task 4.5 — Footer

Dark full-width band. Columns: Brand | Product | Legal | Social icons. `text-xs text-slate-500` links.

**Acceptance criteria:**
- Footer matches `bg-bg-2` glass surface
- No hardcoded year (use JS `new Date().getFullYear()`)

---

## Phase 5 — Dashboard

**Goal:** Authenticated summary view: user greet, status cards, recent devices table, quick actions.

### Task 5.1 — Summary cards row

Four glass cards side by side (`md:grid-cols-2 lg:grid-cols-4`):
| Card          | Value source               | Icon  |
|---------------|----------------------------|-------|
| Suscripción   | `subscription_ends_at`     | 📅    |
| Dispositivos  | `devices.length`           | 📱    |
| Total RX      | `traffic.total_rx_gb GB`   | ⬇     |
| Total TX      | `traffic.total_tx_gb GB`   | ⬆     |

All cards `glass-card` with `fadeUp` stagger container.

**Acceptance criteria:**
- Loading skeleton (pulse animation) while API fetches
- Each card shows formatted value and label
- Enters via staggered scroll-reveal

### Task 5.2 — Device table (`src/components/` table, `src/pages/DashboardPage.tsx`)

Glass table with columns: Nombre, IP asignada, RX/TX, Última conexión, Acciones.

- `RX` and `TX` shown as `kb` / `MB` / `GB` human-readable
- Actions: «Ver .conf» button → trigge                                                                                                                                                                             rs `api.getConf(device.id)` → file download
- "Revocar" button → `api.deleteDevice(device.id)` → optimistic update

**Acceptance criteria:**
- `<table>` uses semantic HTML th/td
- Rx/Tx cells update on polling every 30 s
- Optimistic revoke: removes from table before API confirms

### Task 5.3 — Create Device modal (`src/components/modals/CreateDeviceModal.tsx`)

Modal overlay (`fixed inset-0 bg-black/60 backdrop-blur-sm`):
- Glass card centered
- Input: device name (glass input)
- Optional: PSK string (toggle "Clave precompartida")
- On submit → `api.createDevice` → show `.conf` content in `InvoiceQRModal`-style card

**Acceptance criteria:**
- Modal opens with scale-up animation (`fadeExit/visible`)
- On success: show `.conf` in a `<pre>` glass block, copy-to-clipboard button
- Validates name non-empty before submit

---

## Phase 6 — Payments Page

**Goal:** Invoice creation via TronDealer V2 invoice, QR display, invoice history.

### Task 6.1 — Invoice creation form

On the `PaymentsPage`:
1. User selects "días" from a range slider (1–60)
2. Shows calculated USDT amount in real time
3. "Generar factura" → `api.createInvoice({ days })` → shows QR modal

Amount calc:
```
monto = días × 0.06633 USDT/día
```
Early adopter discount already applied server-side (field `early_adopter`).

**Acceptance criteria:**
- Slider updates `<span>{días} días — {monto} USDT</span>` in real time
- On submit: loading state on button, then QR modal appears
- Error: glass red alert if API fails

### Task 6.2 — QR modal (`src/components/modals/InvoiceQRModal.tsx`)

Shows:
- Amount in bold `text-2xl font-display`
- QR code: render `<img src={response.qr_data} alt="QR" />` — the backend returns a data-URL
- Countdown timer (expires_at − now); at 0 show "Factura expirada, genera una nueva"
- "Copiar dirección" button → copies `response.address` to clipboard
- `ontouchstart` enabling copy and paste

**Acceptance criteria:**
- QR image lazy-loads based on modal open state
- Countdown updates every second
- Expired state disables copy button

### Task 6.3 — Invoice history table

Columns: Fecha, Días, Monto (USDT), Estado, Acciones.

Status badge colors:
| State               | Color       |
|---------------------|-------------|
| `pending`           | amber       |
| `confirmed`/`notified` | green    |
| `swept`             | cyan        |
| `expired`/`failed`  | red         |

**Acceptance criteria:**
- Table fetches on mount via `usePayments`
- Polls every 60 s to refresh statuses (no over-poller; server controls refresh interval)
- Clicking an invoice row opens detail panel with JSON response in `<pre>`

---

## Phase 7 — Integration Pass

**Goal:** Wire everything, polish resilience, verify responsive behaviour.

### Task 7.1 — Routing + 404

- Hash-based 404 page for unmatched routes (`<Route path="*" element={<NotFound />} />`)
- NotFound = glass card centered with "Página no encontrada" + button to `/`

### Task 7.2 — Error Boundary + Error Boundary

- Already placed in Phase 2 task 2.6
- `ErrorBoundary` wraps the entire `<HashRouter>` in `App.tsx`
- "Recover" button resets error state and re-renders

### Task 7.3 — Loading states skeleton

Every async-fetching component must show a skeleton pattern during load.
- `SkeletonCard`: dark glass rectangle with shimmer gradient (`@keyframes shimmer`)

```css
@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position:  200% center; }
}
.skeleton {
  background: linear-gradient(90deg, transparent, transparent 40%, rgba(59,130,246,0.08) 50%, transparent 60%, transparent);
  background-size: 200% auto;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: 8px;
}
```

**Acceptance criteria:**
- Every list/table/grid that fetches from API shows skeleton for at most 2 s
- Shimmer visible on dark background

### Task 7.4 — Responsive breakpoints

| Breakpoint | Sidebar | Grid | Modal |
|------------|---------|------|-------|
| Mobile (< 640px) | Hidden | `cols-1` | Full width |
| Tablet (≥ 640 px) | Icon only / hidden | `cols-2` | Centered 90% |
| Desktop (≥ 1024 px) | Full | `cols-3` | Centered 520 px |

Implementation: `useMediaQuery('(min-width: 640px)')` hook → conditional render of `Sidebar`.

**Acceptance criteria:**
- Sidebar hidden on mobile app; hamburger icon opens drawer overlay at `/login`
- Bento grid collapses to 1 column on mobile
- Modals max-width constrained at 92 % viewport on mobile

### Task 7.5 — Environment variables

`.env` file only at `frontend/`:
```
VITE_API_BASE=http://localhost:8001/proxy
```
In production build set by Vercel/Render env panel:
```
VITE_API_BASE=https://usipipo.dpdns.org/proxy
```

**Acceptance criteria:**
- `import.meta.env.VITE_API_BASE` consumed only via `client.ts`
- No hardcoded URLs anywhere else

### Task 7.6 — Build & type check

```bash
# final verification
cd frontend && npx tsc --noEmit       # 0 errors
npx vite build                        # clean production build
```

**Acceptance criteria:**
- TypeScript zero errors
- Vite production build < 150 KB gzip (attempt)
- No console warnings in dev mode

---

## Summary Checklist

| Phase | Deliverable                                  | Criteria                              |
|-------|----------------------------------------------|---------------------------------------|
| 0     | `api/client.ts` + `types/index.ts`           | All 8 API routes typed, `tsc`         |
| 1     | `styles/tokens.css` + `global.css`           | Tokens present, glass utilities work  |
| 2     | 6 components: GlassCard, AnimatedButton, ScrollReveal, Sidebar, GlassInput/Select, Spinner, ErrorBoundary | Enumeration complete                   |
| 3     | Auth flow: `useAuth`, `AuthGuard`, `LoginPage`, routing | JWT → cookie → no-password access     |
| 4     | Landing: Hero, Bento, Steps, Pricing, Footer | All 5 sections with stagger animations|
| 5     | Dashboard: 4 summary cards, device table, create-modal | Polling, optimistic deletes, .conf download |
| 6     | Payments: invoice form + QR + history table  | Expiration countdown, status badges   |
| 7     | Integration: routing polish, skeleton, responsive, build | Hash-routes, skeleton shimmer, 0 ts errors |
