# Lessons Learned — Fase 3 Frontend uSipipo Proxy

> Vault: inline in `docs/tracking/lessons.md` for at-a-glance lookup.  
> Scope: Fase 0–2 sólo. Actualizado al próximo "cerrar etapa".

---

## [2026-05-23] Levantado del estado

### Setup inicial

- **NPM scaffold preexistente** — el directorio `frontend/` traía paquetes por defecto generados manualmente (`package.json`, `vite.config.ts`, `tsconfig.json` vacíos). Entregar `npm create vite@latest . -- --template react-ts` con `--no-overwrite` equivalente: crear scaffold separado, instalar deps, mover archivos encima de los pre-existentes. El approach correcto fue eliminar placeholders primero y correr scaffolding.
- **Tailwind v4 browser-runtime** — No hay etapa `npx tailwindcss init`. La importación ocurre dinámicamente en `main.tsx` con un `<script>` tag que apunta a `unpkg.com/@tailwindcss/browser`. Funciona sin compilaciónpaso previo, pero es un riesgo de producción en entornos de baja conectividad. Para prod, usar el build estándar con PostCSS preset-env.
- **Framer Motion + React 19** — Se requiere `'use client';` en componentes que usan hooks de Framer Motion (`useInView`) cuando se compila con React 19 Server Components. Sin el pragma, Vite compila pero el componente no renderiza en el cliente.
- **Iconos lucide-react** — Importar desde `lucide-react` siempre (no desde `react-icons`, no desde archivos SVG lg propios). Las props de SVG tienen nombres en camelCase (`size`, `strokeWidth`, `className`).

### Subagentes

- **Subagent especificidad de paths** — Los subagentes escriben rutas relativas a la cwd actual. Usar filesystem paths absolutos `$(pwd)` o rutas relativas claras. Para este projecto (cwd = repo root) `frontend/src/...` funcionó.
- **Speccompliance takes time** — El revisador de especificación es estricto y tarda segundos de overhead. Vale la pena por reducir errores de overspec/underspec.
- **tsc --noEmit en subagentes** — Incluir el comando de verificación en el prompt del subagente obliga a autocorregir antes de devolver, sin trabajo adicional del usuario.

### Diseño

- **Skill ui-ux-pro-max default** → Si la query no menciona "professional SaaS" el skill devuelve estilos Matrix/cyberpunk. Agregar siempre "professional" y "dark mode" para obtener resultados alineados con VPN SaaS.
- **Electric Blue sobre Glass** — (#3b82f6 sobre rgba(13,19,33,0.65) glass) es altamente contrastante: ratio ≈ 5.8:1 cumple WCAG AA+. El glow de botón primary debe usar `rgba(59,130,246,0.45)` para verse sin saturar pantallas OLED.
- **Framer Motion presets consistentes** — Usar `ease: [0.22, 1, 0.36, 1]` (curva Material motion) en todas las animaciones `fadeInUp` / `ScrollReveal`. Evitar mezclar easings en una misma página.

### Git workflow

- **Nueva rama por fase** → `git branch phase-3-frontend` antes de codificar. Permite commits atómicos por fase y revert limpio si la espec cambia.
- **Commits en inglés** — AGENTS.md exige mensajes en inglés incluso en un proyecto de habla hispana. Aplicar consistently.

### Pendiente para fases posteriores

- [ ] Tailwind v4 firefox `backdrop-filter` requiere prefijo `-moz` no; funciona nativo desde FF 103+ — no hay problema
- [ ] React Router `<NavLink>` className es una función (no tuple) — plan original usaba tupla `{isActive}`; usar clases con callback: `className={({isActive}) => isActive ? '...' : '...'}`
- [ ] `npx tsc --noEmit` no detecta errores de importaciones de rutas alias (`@/types`) cuando `tsconfig.app.json` no tiene correctamente `baseUrl` y `paths` configurados — verificar antes de Phase 3
- [ ] Lemonade variante: plan incluye巧合气泡 colores `/payments/invoice` QR; confirmar tamaño real de QR data-URI antes de empezar payments page
- [ ] Cookie `SameSite=Strict` en producción significa que Telegram open-in-browser puede fallar si el flujo cruza dominios (redirección de `t.me` a `usipipo.dpdns.org`). Planearlo como incógnita de investigación en Phase 3 integration.
