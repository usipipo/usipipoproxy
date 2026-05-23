# TRACKING_LOG.md

> Records every significant action with: `Date | Skill | Type | Summary`. Chronological, newest first.

---

## Entry format

```
YYYY-MM-DD HH:MM | [Skill: name] | [TYPE: category] | Brief description
```

---

## Legend

| TYPE | Meaning |
|---|---|
| `BUG` | Bug found, root cause identified, and (if fixed) confirmed |
| `FIX` | Piece of code written or corrected |
| `DECISION` | Architectural or process decision recorded |
| `LESSON` | Insight extracted via brainstorming/diagnose/grill-me |
| `DOC` | Documentation written or updated |
| `DEBT` | Known open issue not yet addressed |
| `VERIFY` | Build/vet/test verification pass or fail |

---

## 2026-05-22 (current session continuation)

| # | Log entry |
|---|-----------|
| C-1 | `2026-05-22 20:51` `[FIX]` `internal/bot/handler.go` — Agregar `errDev` al `CreateDevice` call en `/connect`: `device` nunca se usaba → `if _, errDev := h.store.CreateDevice(...)`. Error `declared and not used: device` eliminado. |
| C-2 | `2026-05-22 20:50` `[DECISION]` `baseUrl()` removido de `internal/bot/handler.go`. Función package-level muerta; todo código usa `h.baseURL` inyectado. También removí `_ = reply` huérfano y restauré casos `/help`/`default` que un edit anterior había borrado por error de scope. |
| C-3 | `2026-05-22 20:50` `[FIX]` Build + vet limpios en Docker (`golang:1.24-alpine`): `go build ./...` ✅ `go vet ./...` ✅. Después de corregir `device` unused. |
| C-4 | `2026-05-22 20:40` `[DOC]` Creado `docs/ROADMAP.md` — roadmap de creación completo con 5 fases (backend limpieza, bot Telegram, app web, app Android, wg-exporter) con criterios de salida por fase. |
| C-5 | `2026-05-22 20:40` `[DOC]` Actualizado `docs/SESSION_SUMMARY.md` — refleja verificación build+veter limpia, estado del bot con bug corregido, roadmap actualizado, orden de retorno actualizado. |
| C-6 | `2026-05-22 20:35` `[FIX]` **Refactor arquitectónico 2026-05-22:** `models.Device` pierde `Conf`; agregados `DeviceResponse` y `CreateDeviceResponse` DTOs; `ClientConfig` eliminado de `pkg/models`; `deviceResponseFrom()` DRY builder en handlers. |
| C-7 | `2026-05-22 20:00` `[FIX]` `wg/manager.go` — `privateKey` unexported; `NewClientConfig()` único constructor; `String()` actualizado. |

---

## 2026-05-22 (prior session, from original TRACKING_LOG.md)
</content>