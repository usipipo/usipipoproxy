# Fix gocritic deprecatedComment Lint Failure

**Date:** 2026-05-11  
**PR:** #75 — refactor: Remove Outline and TrustTunnel support (WireGuard-only agent)  
**Author:** mowgliph (CI Debug)  
**Status:** Approved  
**Priority:** High (blocks CI)  

---

## Problem Statement

The CI lint job fails on PR #75 with a `gocritic` lint error in `internal/api/middleware.go`:

```
internal/api/middleware.go:171:1: deprecatedComment:
`Deprecated: ` notices should be in a dedicated paragraph,
separated from the rest (gocritic)
```

This blocks merging the wireguard-only refactor (v0.12.0 release).

---

## Root Cause Analysis

### Investigation

- **Error location:** `internal/api/middleware.go:171`
- **Linter:** `gocritic` check `deprecatedComment`
- **Current comment (non-compliant):**
  ```go
  // APIKeyMiddleware validates X-API-Key header (legacy, kept for backward compatibility)
  // Deprecated: Use APIKeyMiddlewareWithRateLimit instead
  ```
- **Git blame:** Lines 170-171 from commit `08b6b482` (2026-03-31) — not recently modified in this PR
- **Trigger:** `.golangci.yml` enables `gocritic` linter with `ruleguard` checks; CI now enforces this rule

### Pattern Analysis

The `gocritic` `deprecatedComment` rule enforces Go documentation conventions:
- `Deprecated:` notices **must** be in a dedicated separate paragraph
- Blank comment line (`//`) required between description and `// Deprecated:`
- Improves readability and tooling compatibility (godoc, IDEs)

**Correct format:**
```go
// APIKeyMiddleware validates X-API-Key header (legacy, kept for backward compatibility)
//
// Deprecated: Use APIKeyMiddlewareWithRateLimit instead.
```

### Hypothesis

✅ **Root cause:** Comment lacks blank line separator between description and deprecation notice. The `gocritic` linter enforces this and fails the build.

✅ **Why now?** PR #75 runs CI with `gocritic` enabled (via `.golangci.yml`). This may be the first CI run on this branch since enabling the rule, or the linter version changed.

✅ **Evidence:** Error from `gocritic: deprecatedComment` — a rule validating comment formatting.

---

## Solution Design

### Approach Options

| Approach | Pros | Cons | Recommendation |
|----------|------|------|---------------|
| **Fix comment format** | Standards-compliant; improves documentation; no runtime impact | Single-line change | ✅ **Recommended** |
| Disable gocritic rule | Quick workaround | Weakens linting; tech debt; affects all code | ❌ |
| `//nolint:gocritic` | Local suppression | Scattered suppressions; not scalable | ❌ |

### Proposed Change

**File:** `internal/api/middleware.go`

**Line 171 modification:** Insert blank comment line (`//`) after line 170's description, before `// Deprecated:`.

**Before:**
```go
// APIKeyMiddleware validates X-API-Key header (legacy, kept for backward compatibility)
// Deprecated: Use APIKeyMiddlewareWithRateLimit instead
func APIKeyMiddleware(validKey string) gin.HandlerFunc {
```

**After:**
```go
// APIKeyMiddleware validates X-API-Key header (legacy, kept for backward compatibility)
//
// Deprecated: Use APIKeyMiddlewareWithRateLimit instead.
func APIKeyMiddleware(validKey string) gin.HandlerFunc {
```

**Changes:**
- Add blank comment line (line 171: `//`)
- Update `Deprecated:` line to end with period (minor style improvement)

### Scope

- **Files modified:** 1 (`internal/api/middleware.go`)
- **Lines changed:** 2 (insert blank line + punctuation)
- **Functional impact:** None (comment-only change)
- **Tests affected:** None
- **Breaking changes:** None

---

## Implementation Plan

1. Modify `internal/api/middleware.go` — add blank line separator and punctuation
2. Run `gofmt` to ensure formatting compliance
3. Run `golangci-lint run` locally to verify fix
4. Commit change to PR #75 branch
5. CI should pass (lint job succeeds)
6. Merge PR #75 after all checks pass

---

## Verification

### Success Criteria

- ✅ `golangci-lint` passes with zero issues
- ✅ All other CI jobs (test, build) remain green
- ✅ PR #75 can be merged

### Validation Commands

```bash
# Verify lint passes
golangci-lint run ./internal/api/middleware.go

# Expected output: (no issues found)

# Full test suite
go test -v ./...

# Format check
gofmt -l .
# Expected: (empty output)
```

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Other deprecation comments also fail | Medium | Low | Search for `// Deprecated:` patterns; fix preemptively |
| Linter rule configuration change | Low | Low | `.golangci.yml` already stable; rule is appropriate |
| Merge conflict with PR #75 | Low | Medium | PR #75 is current branch; change is small; rebase if needed |

---

## Related References

- **CI Run:** https://github.com/uSipipo-Team/usipipo-agent/actions/runs/25649607123
- **PR #75:** https://github.com/uSipipo-Team/usipipo-agent/pull/75
- **gocritic deprecatedComment rule:** https://github.com/golangci/golangci-lint/tree/master/pkg/linters/gocritic#deprecatedcomment
- **Go Doc Comment conventions:** https://go.dev/doc/effective_go#commentary

---

**Approved by:** User (2026-05-11)  
**Implementation:** Ready for writing-plans phase
