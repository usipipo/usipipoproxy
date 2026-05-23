# LESSONS.md

> Hard-won insights from grill-me sessions, systematic debugging, diagnose loops, and zoom-outs on the uSipipo Proxy codebase.

---

## LL-001 — Always audit `go vet` local availability before committing

**Level:** `[CRITICAL]`

**Symptom:** `go vet ./...` only worked inside Docker due to no local Go 1.24 install.

**Pattern:** If the only way to verify is via `docker run … golang:1.24-alpine`, the loop is "build → maybe wait 2 min → check". If host has Go, `go vet` is instant. Without host Go, a forgotten `go vet` in CI-or-bust mode will ship broken code that only surfaces in CI or in production build.

**Fix:** Install Go 1.24 locally or add a pre-commit hook (`scripts/vet.sh`) that shells out to Docker automatically. Document in SESSION_SUMMARY.md under "How to resume".

---

## LL-002 — Bug confirmations require code inspection, not doc reading

**Level:** `[HIGH]`

**Symptom:** AGENTS.md listed Bug #1 (`wgManager` nil) and Bug #3 (`ensureDir` no-op) as "pending", but both were already fixed in the codebase. The tracking docs and CONTEXT.md §17 were simply stale.

**Pattern:** When a bug is listed as "pending" and you're about to fix it, first grep the affected file and confirm the bug actually exists. Don't trust that prior documentation is accurate — the code is the source of truth. Consequence of skipping this: wasted debugging on a fixed bug.

**Fix:** Use `codegraph_codegraph_search` or `grep` first; verify `go vet ./...` clean before investigating any listed bug.

---

## LL-003 — WireGuard manager must be nil-safe

**Level:** `[HIGH]`

**Symptom:** Bot `WebhookHandler` and `DevicesHandler` both dereference `h.wgManager` in `/connect` and `List`. If the binary isn't on the host (Docker container without `wg` installed), these code paths panic rather than returning a helpful error.

**Pattern:** Dependencies that may be nil in non-prod environments (WireGuard tools, Prometheus exporter, external APIs) must be nil-guarded at every access point, not just at the call site.

**Fix:** Never return `&wg.Manager{endpoint, cidr}` from `NewManager` unless `wg genkey` succeeds. All callers already guard (`if h.wgManager != nil { … }`), which is correct; keep that pattern when adding any future `wgManager` caller.

---

## LL-004 — `ensureDir()` should use `os.MkdirAll`, not a stub

**Level:** `[HIGH]`

**Symptom:** The original code was a no-op stub that returned success without touching the filesystem, silently masking all directory-missing scenarios.

**Pattern:** A "does nothing and returns success" helper function is a silent lie — it tells callers the DB file directory is ready when it's not.

**Fix applied:** `internal/db/store.go` now calls `os.MkdirAll(p, 0o755)`.

---

## LL-005 — Labels in TronDealer `order-{uuid}` must fit their length constraint

**Level:** `[MEDIUM]`

**Pattern:** `genUUIDv4()` strips dashes to produce a 32-char hex prefix after `"order-"`. Short nonces are safe; UUIDv4 hex is safe. Adding timestamps would risk exceeding TronDealer label limits.

**Fix applied:** Label format kept simple: `"order-" + uuidv4hex`.

---

## LL-006 — HMAC-SHA256 constant-time comparison is non-negotiable for auth

**Level:** `[HIGH]`

**Pattern:** Both Telegram login hash (`validateTelegramHashManual`) and TronDealer webhook (`validateTDSignature`) use `hmac.Equal` instead of `bytes.Equal` or `==`. This prevents timing side-channel attacks that could leak valid hashes byte-by-byte.

**Fix applied:** Both validators use `hmac.Equal`; a shared helper can be extracted if a third HMAC endpoint is added.

---

## LL-007 — Async webhook processing decouples latency from robustness

**Level:** `[MEDIUM]`

**Pattern:** HTTP handlers acting as inbound webhooks must return 200 within a tight deadline. Offload all DB mutations and business logic to a buffered channel consumed by a background goroutine. Drop events only if the channel is already full.

**Fix applied:** `PaymentQueue` (buffered channel 256); `StartPaymentWorker` goroutine; `processPaymentEvent` switch-case dispatcher.

---

## LL-008 — `GenUUIDv4` — don't use `math/rand` for payment IDs

**Level:** `[MEDIUM]`

**Pattern:** `rand.Seed(time.Now().UnixNano())` is not cryptographically secure. For invoice IDs and TronDealer wallet labels, collision risk is practically negligible due to 128-bit space, but the pattern should eventually move to `crypto/rand` or `github.com/google/uuid`.

**Fix applied:** Not yet refactored (low risk). Documented here as P2 debt.

---

## LL-009 — Entity must never carry secrets or transport config

**Level:** `[HIGH]`

**Pattern:** `models.Device` had 3 responsibilities: (1) BD entity row, (2) DTO API response, (3) carrier for `ClientConfig` with private key. Every handler serializing `Device` in JSON risked leaking the private key.

**Fix applied:** `Device` stripped of `Conf`. New `DeviceResponse` (safe) and `CreateDeviceResponse` (includes `wg.ClientConfig`, sent only on creation). `deviceResponseFrom()` is the single DRY builder.

---

## LL-010 — Duplicate type definitions across packages silently diverge

**Level:** `[HIGH]`

**Pattern:** `ClientConfig` was defined in both `pkg/models` and `internal/wg`. The copies treated `PrivateKey` differently (exported vs unexported). Any change to one copy created a type mismatch at the boundary.

**Fix applied:** `ClientConfig` removed from `pkg/models`, only exists in `internal/wg`. `privateKey` field unexported; `PrivateKey()` getter explicit; `NewClientConfig()` sole constructor.

---

## LL-011 — Interface declarations live where consumed, not where implemented

**Level:** `[MEDIUM]`

**Pattern:** `DeviceStore` and `PaymentStore` were declared in the handlers package — correct ISP+DIP. Small interfaces at the consumer site mean the store implementation satisfies them without knowing handler internals.

**Fix applied:** `DeviceStore` was accidentally redeclared when the file was rewritten. Duplicate removed; original kept at `handlers.go:~179`.

---

## LL-012 — `String()` method must track field name changes

**Level:** `[LOW]`

**Pattern:** When `privateKey` was renamed from exported to unexported, `ClientConfig.String()` still referenced `c.PrivateKey`. The compiler caught it — but unexported fields have no JSON-tag safety net.

**Fix applied:** `String()` updated to `c.privateKey`.

---

## LL-013 — Unused-variable error requires correct error-binding syntax

**Level:** `[MEDIUM]`

**Symptom:** `device, err := h.store.CreateDevice(...)` produced `declared and not used: device` because the variable name was later shadowed or simply unused in the `/connect` bot handler path. The original code had `_ = device` as a workaround, but `go vet` flagged the unused-variable binding itself.

**Pattern:** When the return value of an error-returning function isn't needed, use `if _, err := f()` not `v, _ := f(); _ = v`. The former never creates the named binding. Bonus: name the error variable explicitly (`errDev`) to avoid shadowing the outer `err` from `GenerateKeyPair`.

**Fix applied:** Changed to `if _, errDev := h.store.CreateDevice(...); errDev != nil { … }`.

---

## LL-014 — Greedy edits destroy adjacent syntax; always verify surrounding context

**Level:** `[HIGH]`

**Symptom:** An edit that replaced `baseUrl()` with `h.baseURL` accidentally deleted the `}` closing the `/connect` case block AND the entire `/help` / `default` cases — because the `oldString` matched too broadly. The result was a build error for missing return and a `switch` with only two cases.

**Pattern:** When targeting a multi-line section for replacement, read ±5 lines of surrounding context before writing the `oldString`. Prefer the smallest unique matching window. Always rebuild immediately after structural edits.

**Fix applied:** Narrowed edit scope; restored `/help` and `default` cases in a second pass; removed dead `baseUrl()` function in a separate pass; verified build after each change.

---

## LL-015 — Reporter must verify state before claiming bug is "already fixed"

**Level:** `[HIGH]`

**Symptom:** CONTEXT.md §17 declared bug #9 (`baseUrl()` hardcoded in bot handler) as "pending" — but the code was correct on inspection: `h.baseURL` was already injected and used in the `main.go` constructor call. The bug was about the *function* `baseUrl()` existing as dead code, not about the handler struct field being wrong.

**Pattern:** "Pending" bugs reported by documentation-era agents aren't always real bugs. Always inspect the actual code path before marking a task as "to-do". The cost is a `grep` or `read`; the reward is not diverting attention to a phantom.

**Fix applied:** Confirmed `h.baseURL` was already correct; bug #9 is "dead-code removal" not "hardcoded URL". Updated CONTEXT.md §17 accordingly.

---

## LL-016 — Go multi-value return across lines needs a trailing comma on the last element

**Level:** `[MEDIUM]`

**Symptom:** `return "texto", &InlineKeyboardMarkup{...}` written as a raw multi-line expression in `cmdStart`/`cmdConnect`/`cmdHelp` produced "unexpected }, expected expression". The Go parser saw the closing `}` of the struct literal and expected the `,` separator to be at the right indentation level, but the write tool collapsed indentation and dropped the separating comma between the two return values.

**Pattern:** When a `return` returns multiple values and the second is a struct/function literal spanning multiple lines, assign to a named variable first to avoid multi-line return ambiguity:
```go
text := "..."
keyboard := &InlineKeyboardMarkup{...}
return text, keyboard
```

**Fix applied:** Refactored all `cmdXXXX` return statements to use named `text` + `keyboard` variables.

---

## LL-017 — Use `path.Base()` instead of `strings.HasSuffix` for URL segment routing

**Level:** `[MEDIUM]`

**Symptom:** `DevicesHandler.Router` matched routes with `strings.HasSuffix(r.URL.Path, "/conf")`. If a future endpoint like `/devices/{id}/config-history` were added, it would silently match `/conf` as a suffix and route to the wrong handler.

**Pattern:** For path segment routing (especially after `http.StripPrefix`), use `path.Base(r.URL.Path)` which extracts only the last URL segment. It is unambiguous and self-documenting. Reserve `HasSuffix` for exact-match string comparisons, not path routing.

**Fix applied:** Replaced both `HasSuffix` checks in `Router` with `path.Base()`.

---

## LL-018 — Cookie-based JWT auth for browser endpoints

**Level:** `[HIGH]`

**Symptom:** Bot buttons that open `https://usipipo.dpdns.org/proxy/devices/{id}/conf` in a browser fail because the endpoint expects `Authorization: Bearer <jwt>`, but the browser session has no JWT stored.

**Pattern:** Decouple token transport from the browser. The frontend calls `POST /proxy/auth/cookie` with the JWT in the body; the backend validates the JWT, looks up the user, and sets a `session` cookie (`HttpOnly; Secure; SameSite=Strict`). Subsequent requests from the browser include the cookie automatically. The `AuthMiddleware` reads from both `Authorization` header AND `session` cookie.

**Fix applied:**
- New `middleware.AuthMiddleware` in `internal/http/middleware/auth.go`
- New `POST /proxy/auth/cookie` handler in `cmd/backend/main.go`
- `middleware.SetSessionCookie()` / `middleware.ClearSessionCookie()` helpers
- `tokenFromRequest()` reads header first, then cookie

---

## LL-019 — Extract resource IDs from URL path after `StripPrefix`, not via `PathValue`

**Level:** `[MEDIUM]`

**Symptom:** `ServeConf` tried `r.PathValue("id")` but `http.StripPrefix("/proxy/devices", ...)` does not register `{id}` as a named path parameter. `PathValue("id")` always returned empty string regardless of the actual device ID in the URL.

**Pattern:** When using `StripPrefix` for simple REST-style paths, extract resource IDs by splitting the remaining path string:
```go
trimmed := strings.TrimPrefix(r.URL.Path, "/")
idStr := strings.SplitN(trimmed, "/", 2)[0]
```
`PathValue` only works with `http.ServeMux` registered patterns that use `{param}` syntax (e.g. `"/proxy/devices/{id}/conf"`), which requires `http.NewServeMux` and manual segment matching — more complexity than most handlers need.

**Fix applied:** `ServeConf` now extracts the device ID via `strings.SplitN` on the trimmed path.

---

## LL-020 — Bot `baseUrl()` dead-code pattern: injected fields replace hardcoded values

**Level:** `[LOW]`

**Symptom:** The bot handler originally had a `baseUrl()` method that returned a hardcoded string `"http://localhost:9001"`. The `WebhookHandler.baseURL` field was already injected via constructor but the unused method lingered.

**Pattern:** When a struct field is injected via constructor, the compiler will not catch a stray method that computes the same value differently — it is simply unused. Run `grep -rn "TODO\|FIXME\|fake\|func.*url\|func.*base"` before each session close to catch dead utility methods.

**Fix applied:** Dead `baseUrl()` removed; `h.baseURL` is the single source of truth for the public URL.

---
