# Docker Release Workflow Design

**Date:** 2026-04-05
**Status:** Approved

## Overview

Add automated Docker image build and push to GitHub Container Registry (ghcr.io) on tag releases.

## Architecture

### Trigger
- Push of git tag matching `v*` (e.g., `v0.10.0`)

### Image Tags
- `ghcr.io/usipipo-team/usipipo-telegram-bot:v0.10.0` (specific version)
- `ghcr.io/usipipo-team/usipipo-telegram-bot:latest` (always latest stable)

### Dockerfile (Multi-stage)
- **Stage 1 (build):** Install dependencies with `uv sync --frozen`
- **Stage 2 (runtime):** Python 3.13-slim with only production dependencies

### Release Workflow
1. Reuses existing CI workflow (lint, type-check, test, security)
2. Builds Docker image with multi-stage Dockerfile
3. Pushes to ghcr.io with version and latest tags
4. Requires `packages: write` permission

## Files
- **Create:** `.github/workflows/release.yml`
- **Modify:** `Dockerfile` (multi-stage optimization)
