# Fix gocritic deprecatedComment Lint Failure

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix CI lint failure by correcting deprecation comment format in internal/api/middleware.go

**Architecture:** Single-file comment formatting change to comply with gocritic linter's deprecatedComment rule requiring blank line separator between description and Deprecated notice.

**Tech Stack:** Go, golangci-lint, gocritic linter

---

## Context

- **PR:** #75 (refactor/wireguard-only branch)
- **Failing job:** `lint`
- **Error:** `internal/api/middleware.go:171:1: deprecatedComment: 'Deprecated: ' notices should be in a dedicated paragraph, separated from the rest`
- **Root cause:** Comment on lines 170-171 lacks blank line separator before `// Deprecated:`
- **Required format:** Description line, blank comment line (`//`), then `// Deprecated:` line

---

## Pre-Implementation Checklist

- [x] Verified current CI failure: GitHub Actions run 25649607123 failed
- [x] Located target file: `internal/api/middleware.go`
- [x] Understood gocritic rule: `deprecatedComment` enforces blank line before `Deprecated:`
- [x] Plan to run lint locally before committing

---

### Task 1: Examine Current Comment Format

**Files:**
- Read: `internal/api/middleware.go:165-175`

**Step 1:** Open the file and view lines around the problematic comment

```bash
sed -n '165,175p' internal/api/middleware.go
```

**Expected output:**
```go
  165:
  166:  // APIKeyMiddleware validates X-API-Key header (legacy, kept for backward compatibility)
  167:  // Deprecated: Use APIKeyMiddlewareWithRateLimit instead
  168:  func APIKeyMiddleware(validKey string) gin.HandlerFunc {
```

**Step 2:** Confirm issue — no blank line between description (166) and `Deprecated:` (167)

**Step 3:** Commit N/A (investigation only)

---

### Task 2: Fix Comment Format

**Files:**
- Modify: `internal/api/middleware.go:166-167`

**Step 1:** Edit the file to add blank line and improve punctuation

**Current code (lines 166-167):**
```go
// APIKeyMiddleware validates X-API-Key header (legacy, kept for backward compatibility)
// Deprecated: Use APIKeyMiddlewareWithRateLimit instead
```

**Fixed code:**
```go
// APIKeyMiddleware validates X-API-Key header (legacy, kept for backward compatibility)
//
// Deprecated: Use APIKeyMiddlewareWithRateLimit instead.
```

**Changes:**
- Insert new line `//` after line 166
- Append `.` to end of line 167

**Step 2:** Verify fix with sed:

```bash
sed -n '165,170p' internal/api/middleware.go
```

Expected:
```go
  165:
  166:  // APIKeyMiddleware validates X-API-Key header (legacy, kept for backward compatibility)
  167:  //
  168:  // Deprecated: Use APIKeyMiddlewareWithRateLimit instead.
  169:  func APIKeyMiddleware(validKey string) gin.HandlerFunc {
```

**Step 3:** Commit

```bash
git add internal/api/middleware.go
git commit -m "fix: correct deprecated comment format for gocritic lint

- Add blank line separator before Deprecated notice
- Append period to deprecation message
- Fixes CI lint failure in PR #75"
```

---

### Task 3: Verify Lint Passes Locally

**Files:** None (validation only)

**Step 1:** Check code formatting

```bash
gofmt -l internal/api/middleware.go
```

Expected output: (empty — no unformatted files)

If output shows file, fix with: `gofmt -w internal/api/middleware.go`

**Step 2:** Ensure golangci-lint is available

```bash
which golangci-lint || { echo "golangci-lint not found, installing..."; \
  curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | \
  sh -s -- -b $(go env GOPATH)/bin v2.11.4; }
```

**Step 3:** Run linter only on the fixed file

```bash
golangci-lint run --disable-all --enable=gocritic ./internal/api/middleware.go
```

Expected output: `No issues found` or empty output

**Step 4:** Run linter on entire repository

```bash
golangci-lint run ./...
```

Expected: `issues found: 0` or at least NO `deprecatedComment` error

**Step 5:** If lint passes, proceed. If fails, check:
- Blank line correctly inserted (line 167 should be just `//`)
- `Deprecated:` line has proper spacing
- No tabs vs spaces issues

Commit N/A (verification only)

---

### Task 4: Push and Monitor CI

**Files:** None (git operations)

**Step 1:** Push commit to PR branch

```bash
git push origin refactor/wireguard-only
```

**Step 2:** Monitor GitHub Actions

Open URL: https://github.com/uSipipo-Team/usipipo-agent/actions

Wait for `lint` job on run 25649607123+ to complete.

**Expected:** ✅ PASS (green checkmark on lint job)

**If lint still fails:**
- Check CI logs for remaining `deprecatedComment` errors
- Verify edit was applied correctly in CI environment
- Search for other `Deprecated:` comments that might also fail:
  ```bash
  grep -rn "// Deprecated:" internal/ --include="*.go"
  ```
- Fix any additional violations found

**Step 3:** After lint passes, `test` and `build` jobs should run automatically

Verify all jobs pass.

**Step 4:** Commit N/A (CI automatic)

---

### Task 5: Merge PR #75

**Files:** None (GitHub operation)

**Once all CI jobs pass:**

**Option A — GitHub CLI:**
```bash
gh pr checkout 75
gh pr merge 75 --squash --delete-branch
```

**Option B — GitHub UI:** Click "Squash and merge" on PR #75

**Step 1:** Confirm all checks green (lint, test, build)

**Step 2:** Squash and merge

**Step 3:** Verify release workflow triggered (v0.12.0 tag)

**Step 4:** Confirm branch deleted

---

## Testing Strategy

- **Pre-commit:** Run `golangci-lint run ./...` locally
- **CI verification:** lint job must pass
- **No unit tests needed** (comment-only change, no functional behavior)

---

## Rollback Plan

If issues arise after merge:

```bash
# Revert commit on main (if needed)
git revert <commit-hash>
git push origin main
```

Change is minimal (comment formatting), safe to revert.

---

## References

- gocritic `deprecatedComment` rule: https://github.com/golangci/golangci-lint/tree/master/pkg/linters/gocritic#deprecatedcomment
- CI run (failed): https://github.com/uSipipo-Team/usipipo-agent/actions/runs/25649607123
- PR #75: https://github.com/uSipipo-Team/usipipo-agent/pull/75
- Go doc comment conventions: https://go.dev/doc/effective_go#commentary

---

**Total estimated time:** 10–15 minutes  
**Risk level:** Low (single-line formatting fix)  
**Dependencies:** None
