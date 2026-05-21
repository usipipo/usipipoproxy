# Docker Release Workflow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add automated Docker image build and push to GitHub Container Registry on tag releases.

**Architecture:** Multi-stage Dockerfile for minimal image, GitHub Actions workflow triggered on `v*` tags, pushes to `ghcr.io/usipipo-team/usipipo-telegram-bot` with version and latest tags.

**Tech Stack:** Docker, GitHub Actions, uv, Python 3.13-slim, ghcr.io

---

## Task 1: Optimize Dockerfile (Multi-Stage)

**Files:**
- Modify: `Dockerfile`

**Step 1: Replace current Dockerfile with multi-stage version**

```dockerfile
FROM python:3.13-slim AS builder

WORKDIR /build

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (production only)
RUN uv sync --frozen --no-dev --no-cache

# Copy source code
COPY src/ ./src/

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /build/.venv /app/.venv
COPY --from=builder /build/src /app/src

# Use venv Python
ENV PATH="/app/.venv/bin:$PATH"

# Run the bot
CMD ["python", "-m", "src"]
```

**Step 2: Test Dockerfile builds locally**

Run: `docker build -t test-bot .`
Expected: Build succeeds, image size < 200MB

**Step 3: Commit**

```bash
git add Dockerfile
git commit -m "feat: optimize Dockerfile with multi-stage build"
```

---

## Task 2: Create Release Workflow

**Files:**
- Create: `.github/workflows/release.yml`

**Step 1: Create release workflow file**

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  ci:
    uses: ./.github/workflows/ci.yml

  docker:
    needs: ci
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract version from tag
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ steps.version.outputs.VERSION }}
            ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Step 2: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "feat: add Docker release workflow to ghcr.io"
```

---

## Task 3: Test and Verify

**Step 1: Push to remote and create tag**

```bash
git push origin <branch>
gh pr create --base main --head <branch> --title "feat: Docker release workflow" --body "..."
# Merge PR
git pull origin main
git tag -a v0.11.0 -m "Release v0.11.0 - Docker release workflow"
git push origin v0.11.0
```

**Step 2: Verify workflow runs**

Run: `gh run list --limit 3`
Expected: Release workflow shows success

**Step 3: Verify image published**

Run: `gh api repos/uSipipo-Team/usipipo-telegram-bot/packages/container/usipipo-telegram-bot/versions`
Expected: Returns version metadata

---

## Summary Checklist

- [ ] Task 1: Multi-stage Dockerfile
- [ ] Task 2: Release workflow
- [ ] Task 3: Test and verify
